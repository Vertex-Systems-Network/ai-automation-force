from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLOTS_PATH = ROOT / "ai-native" / "parallel" / "AGENT-SLOTS.json"
PLAN_PATH = ROOT / "ai-native" / "parallel" / "SUPERVISOR-PLAN.md"
ACTIVE_PATH = ROOT / "ai-native" / "parallel" / "ACTIVE-WORK.yaml"
STATE_PATH = ROOT / "ai-native" / "parallel" / "SUPERVISOR-STATE.yaml"
BROADCASTS_PATH = ROOT / "ai-native" / "parallel" / "SUPERVISOR-BROADCASTS.yaml"
MIGRATIONS_PATH = ROOT / "ai-native" / "parallel" / "MIGRATION-REGISTRY.yaml"
README_PATH = ROOT / "README.md"

REJECTION = "Go Home Come Back Next Time"
COMPLETION = "Work Done and Submitted"
ALERT = (
    "New changes have been merged — please merge these changes into your branch first, "
    "then resume your own work."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_text(path: Path) -> str:
    require(path.is_file(), f"missing governance file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def yaml_int(text: str, key: str) -> int:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(\d+)\s*$", text)
    require(match is not None, f"missing integer governance key: {key}")
    return int(match.group(1))


def active_write_claims(text: str) -> dict[str, list[str]]:
    claims: dict[str, list[str]] = {}
    current_task: str | None = None
    in_writes = False

    for raw in text.splitlines():
        task_match = re.match(r"^  - task_id:\s*(\S+)\s*$", raw)
        if task_match:
            current_task = task_match.group(1)
            claims.setdefault(current_task, [])
            in_writes = False
            continue

        if current_task is None:
            continue

        if re.match(r"^    writes:\s*$", raw):
            in_writes = True
            continue

        if in_writes:
            item_match = re.match(r"^      -\s+(.+?)\s*$", raw)
            if item_match:
                claims[current_task].append(item_match.group(1))
                continue
            if raw.strip() and not raw.startswith("      "):
                in_writes = False

    return claims


def wildcard_prefix(path: str) -> str | None:
    marker = min(
        [index for index in (path.find("*"), path.find("?")) if index >= 0],
        default=-1,
    )
    if marker < 0:
        return None
    return path[:marker]


def claims_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    left_prefix = wildcard_prefix(left)
    right_prefix = wildcard_prefix(right)
    if left_prefix is not None and right.startswith(left_prefix):
        return True
    if right_prefix is not None and left.startswith(right_prefix):
        return True
    if left_prefix is not None and right_prefix is not None:
        return left_prefix.startswith(right_prefix) or right_prefix.startswith(left_prefix)
    return False


def migration_reservations(text: str) -> set[str]:
    reservations_section = text.split("landed:", 1)[0]
    return {
        match.group(1)
        for match in re.finditer(r"(?m)^\s*- revision:\s*(\S+)\s*$", reservations_section)
    }


def active_migration_reservations(text: str) -> set[str]:
    values: set[str] = set()
    for match in re.finditer(r"(?m)^\s*migration_reservation:\s*(\S+)\s*$", text):
        value = match.group(1)
        if value not in {"null", "None", "~"}:
            values.add(value)
    return values


def main() -> None:
    slots = json.loads(load_text(SLOTS_PATH))
    plan = load_text(PLAN_PATH)
    active = load_text(ACTIVE_PATH)
    state = load_text(STATE_PATH)
    broadcasts = load_text(BROADCASTS_PATH)
    migrations = load_text(MIGRATIONS_PATH)
    readme = load_text(README_PATH)

    require(slots.get("source_branch_required") == "main", "new agents must start from main")
    require(slots.get("assignment_authority") == "supervisor", "Supervisor must own assignment")
    require(slots.get("no_slot_response") == REJECTION, "no-slot response drifted")

    records = slots.get("slots")
    require(isinstance(records, list) and records, "slot registry must contain slots")

    seen_ids: set[str] = set()
    seen_branches: set[str] = set()
    seen_agents: set[str] = set()
    open_slots = 0

    for slot in records:
        require(isinstance(slot, dict), "slot entries must be objects")
        slot_id = str(slot.get("slot_id", ""))
        branch = str(slot.get("branch", ""))
        module = str(slot.get("module", ""))
        status = slot.get("status")
        agent = slot.get("assigned_agent")
        accepts_new = slot.get("accepts_new_agent")

        require(slot_id and slot_id not in seen_ids, f"duplicate/empty slot_id: {slot_id}")
        require(branch and branch not in seen_branches, f"duplicate/empty slot branch: {branch}")
        require(module, f"slot {slot_id} missing module")
        require(status in {"open", "occupied"}, f"slot {slot_id} has invalid status")
        require(isinstance(accepts_new, bool), f"slot {slot_id} missing accepts_new_agent bool")
        seen_ids.add(slot_id)
        seen_branches.add(branch)

        require(branch in plan, f"slot branch missing from Supervisor plan: {branch}")
        require(module in active, f"slot module missing from active-work state: {module}")

        if status == "occupied":
            require(isinstance(agent, str) and agent, f"occupied slot {slot_id} missing agent")
            require(agent not in seen_agents, f"agent assigned to multiple slots: {agent}")
            seen_agents.add(agent)
            require(agent in plan, f"assigned agent missing from Supervisor plan: {agent}")
            require(branch in active, f"occupied branch missing from active-work: {branch}")
            require(agent in active, f"occupied agent missing from active-work: {agent}")
        else:
            require(accepts_new is True, f"open slot {slot_id} must accept new agents")
            require(agent is None, f"open slot {slot_id} must not have assigned_agent")
            open_slots += 1

    require(REJECTION in plan and REJECTION in readme, "new-agent rejection phrase must be visible")
    require(COMPLETION in plan and COMPLETION in state, "completion signal drifted")
    require(ALERT in plan and ALERT in state and ALERT in broadcasts, "post-merge alert drifted")

    broadcast_sequence = yaml_int(broadcasts, "latest_sequence")
    state_sequence = yaml_int(state, "latest_broadcast_sequence")
    require(
        broadcast_sequence == state_sequence,
        f"Supervisor broadcast sequence mismatch: broadcasts={broadcast_sequence}, state={state_sequence}",
    )

    claims = active_write_claims(active)
    flat_claims: list[tuple[str, str]] = [
        (task, path) for task, paths in claims.items() for path in paths
    ]
    for task, path in flat_claims:
        require(
            path != "ai-native/checkpoints/**",
            f"broad shared checkpoint claim is forbidden for parallel task {task}",
        )
    for index, (left_task, left_path) in enumerate(flat_claims):
        for right_task, right_path in flat_claims[index + 1 :]:
            if left_task == right_task:
                continue
            require(
                not claims_overlap(left_path, right_path),
                "overlapping active write claims: "
                f"{left_task}:{left_path} vs {right_task}:{right_path}",
            )

    reserved = migration_reservations(migrations)
    active_reserved = active_migration_reservations(active)
    require(
        active_reserved <= reserved,
        f"active task migration reservation missing from registry: {sorted(active_reserved - reserved)}",
    )
    require(len(reserved) == len(set(reserved)), "duplicate migration reservations detected")

    if open_slots == 0:
        print(
            "Parallel governance PASS: "
            f"broadcast={broadcast_sequence}; write-claims={len(flat_claims)}; "
            f"all module slots occupied; response='{REJECTION}'"
        )
    else:
        print(
            "Parallel governance PASS: "
            f"broadcast={broadcast_sequence}; write-claims={len(flat_claims)}; "
            f"{open_slots} open module slot(s) available"
        )


if __name__ == "__main__":
    main()
