from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
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


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    branch: str
    module: str
    agent: str
    status: str
    writes: tuple[str, ...]
    last_acknowledged_broadcast: int | None


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


def _task_scalar(block: list[str], key: str) -> str:
    prefix = f"    {key}:"
    for line in block:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def _task_list(block: list[str], key: str) -> tuple[str, ...]:
    marker = f"    {key}:"
    values: list[str] = []
    collecting = False
    for line in block:
        if line == marker:
            collecting = True
            continue
        if not collecting:
            continue
        if line.startswith("      - "):
            values.append(line[8:].strip())
            continue
        if line.strip() and not line.startswith("      "):
            break
    return tuple(values)


def parse_active_tasks(text: str) -> list[TaskRecord]:
    match = re.search(r"(?ms)^active:\s*\n(.*?)(?=^rules:\s*$)", text)
    require(match is not None, "ACTIVE-WORK.yaml missing active/rules sections")
    lines = match.group(1).splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if line.startswith("  - task_id:"):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    tasks: list[TaskRecord] = []
    seen_ids: set[str] = set()
    for block in blocks:
        task_id = block[0].split(":", 1)[1].strip()
        branch = _task_scalar(block, "branch")
        module = _task_scalar(block, "module")
        agent = _task_scalar(block, "assigned_agent")
        status = _task_scalar(block, "status")
        acknowledgement = _task_scalar(block, "last_acknowledged_broadcast")
        writes = _task_list(block, "writes")

        require(task_id and task_id not in seen_ids, f"duplicate/empty active task_id: {task_id}")
        require(branch, f"active task {task_id} missing branch")
        require(module, f"active task {task_id} missing module")
        require(agent, f"active task {task_id} missing assigned_agent")
        require(status, f"active task {task_id} missing status")
        require(writes, f"active task {task_id} must have at least one authoritative write claim")
        seen_ids.add(task_id)

        ack_value = None if not acknowledgement else int(acknowledgement)
        tasks.append(
            TaskRecord(
                task_id=task_id,
                branch=branch,
                module=module,
                agent=agent,
                status=status,
                writes=writes,
                last_acknowledged_broadcast=ack_value,
            )
        )
    require(tasks, "ACTIVE-WORK.yaml must contain active tasks")
    return tasks


def parse_revision_section(text: str, section: str) -> list[str]:
    header = re.search(rf"(?m)^{re.escape(section)}:\s*(.*)$", text)
    require(header is not None, f"MIGRATION-REGISTRY.yaml missing {section} section")
    inline = header.group(1).strip()
    if inline == "[]":
        return []

    start = header.end()
    next_header = re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*", text[start:])
    end = start + next_header.start() if next_header else len(text)
    body = text[start:end]
    return re.findall(r"(?m)^\s{2}- revision:\s*([^\s#]+)\s*$", body)


def normalize_write_claim(claim: str) -> tuple[str, str]:
    require(claim and not claim.startswith("/"), f"invalid absolute write claim: {claim}")
    require(".." not in claim.split("/"), f"unsafe parent segment in write claim: {claim}")
    if "*" not in claim:
        return ("exact", claim.rstrip("/"))
    require(
        claim.endswith("/**") and claim.count("*") == 2,
        f"write claim must be exact or end only with '/**': {claim}",
    )
    prefix = claim[:-3].rstrip("/")
    require(prefix, f"recursive write claim must have a non-empty prefix: {claim}")
    return ("tree", prefix)


def claims_conflict(left: str, right: str) -> bool:
    left_kind, left_path = normalize_write_claim(left)
    right_kind, right_path = normalize_write_claim(right)

    if left_kind == "exact" and right_kind == "exact":
        return left_path == right_path
    if left_kind == "tree" and right_kind == "exact":
        return right_path == left_path or right_path.startswith(f"{left_path}/")
    if left_kind == "exact" and right_kind == "tree":
        return left_path == right_path or left_path.startswith(f"{right_path}/")
    return (
        left_path == right_path
        or left_path.startswith(f"{right_path}/")
        or right_path.startswith(f"{left_path}/")
    )


def find_write_conflicts(tasks: list[TaskRecord]) -> list[str]:
    conflicts: list[str] = []
    for index, left in enumerate(tasks):
        for right in tasks[index + 1 :]:
            for left_claim in left.writes:
                for right_claim in right.writes:
                    if claims_conflict(left_claim, right_claim):
                        conflicts.append(
                            f"{left.task_id}:{left_claim} conflicts with "
                            f"{right.task_id}:{right_claim}"
                        )
    return conflicts


def self_test() -> None:
    assert claims_conflict("docs/milestones/M04/**", "docs/milestones/M04/PLAN.md")
    assert claims_conflict("docs/**", "docs/milestones/M04/**")
    assert claims_conflict("README.md", "README.md")
    assert not claims_conflict("docs/milestones/M04/**", "docs/milestones/M05/**")
    assert not claims_conflict("docs/qa/**", "docs/security/**")

    rejected = False
    try:
        normalize_write_claim("docs/**character**")
    except SystemExit:
        rejected = True
    assert rejected, "embedded wildcard claims must be rejected"

    synthetic = [
        TaskRecord("A", "a", "a", "a", "active", ("docs/a/**",), 3),
        TaskRecord("B", "b", "b", "b", "active", ("docs/b/**",), 3),
    ]
    assert find_write_conflicts(synthetic) == []
    synthetic.append(TaskRecord("C", "c", "c", "c", "active", ("docs/a/file.md",), 3))
    assert find_write_conflicts(synthetic), "recursive/exact overlap must be detected"
    print("Parallel governance validator self-test PASS.")


def main() -> None:
    slots = json.loads(load_text(SLOTS_PATH))
    plan = load_text(PLAN_PATH)
    active = load_text(ACTIVE_PATH)
    state = load_text(STATE_PATH)
    broadcasts = load_text(BROADCASTS_PATH)
    migrations = load_text(MIGRATIONS_PATH)
    readme = load_text(README_PATH)
    tasks = parse_active_tasks(active)

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
        require(branch in plan, f"slot branch missing from Supervisor plan: {branch}")
        seen_ids.add(slot_id)
        seen_branches.add(branch)

        if status == "occupied":
            require(isinstance(agent, str) and agent, f"occupied slot {slot_id} missing agent")
            require(agent not in seen_agents, f"agent assigned to multiple slots: {agent}")
            seen_agents.add(agent)
            require(agent in plan, f"assigned agent missing from Supervisor plan: {agent}")
            matches = [task for task in tasks if task.branch == branch]
            require(len(matches) == 1, f"occupied slot {slot_id} must map to exactly one active task")
            task = matches[0]
            require(task.agent == agent, f"slot/task agent mismatch for {slot_id}")
            require(task.module == module, f"slot/task module mismatch for {slot_id}")
        else:
            require(accepts_new is True, f"open slot {slot_id} must accept new agents")
            require(agent is None, f"open slot {slot_id} must not have assigned_agent")
            open_slots += 1

    require(
        yaml_int(state, "current_open_slots") == open_slots,
        "Supervisor current_open_slots does not match AGENT-SLOTS.json",
    )
    require(REJECTION in plan and REJECTION in readme, "new-agent rejection phrase must be visible")
    require(COMPLETION in plan and COMPLETION in state, "completion signal drifted")
    require(ALERT in plan and ALERT in state and ALERT in broadcasts, "post-merge alert drifted")

    broadcast_sequence = yaml_int(broadcasts, "latest_sequence")
    state_sequence = yaml_int(state, "latest_broadcast_sequence")
    require(
        broadcast_sequence == state_sequence,
        f"Supervisor broadcast sequence mismatch: broadcasts={broadcast_sequence}, state={state_sequence}",
    )

    for task in tasks:
        for claim in task.writes:
            normalize_write_claim(claim)
        if "sync-required" not in task.status:
            require(
                task.last_acknowledged_broadcast == broadcast_sequence,
                f"active task {task.task_id} acknowledgement is stale: "
                f"{task.last_acknowledged_broadcast} != {broadcast_sequence}",
            )

    conflicts = find_write_conflicts(tasks)
    require(not conflicts, "overlapping active write claims: " + "; ".join(conflicts))

    reservations = parse_revision_section(migrations, "reservations")
    landed = parse_revision_section(migrations, "landed")
    require(len(reservations) == len(set(reservations)), "duplicate active migration reservations")
    require(len(landed) == len(set(landed)), "duplicate landed migration revisions")
    overlap = sorted(set(reservations).intersection(landed))
    require(not overlap, f"migration revision appears active and landed: {', '.join(overlap)}")
    if landed:
        current_landed = re.search(r"(?m)^\s*current_landed_head:\s*([^\s#]+)\s*$", migrations)
        require(current_landed is not None, "landed migrations require current_landed_head")
        require(
            current_landed.group(1) == landed[-1],
            "current_landed_head must match the latest landed registry revision",
        )

    if open_slots == 0:
        print(
            "Parallel governance PASS: "
            f"broadcast={broadcast_sequence}; tasks={len(tasks)}; write-claims=collision-free; "
            f"all module slots occupied; response='{REJECTION}'"
        )
    else:
        print(
            "Parallel governance PASS: "
            f"broadcast={broadcast_sequence}; tasks={len(tasks)}; write-claims=collision-free; "
            f"{open_slots} open module slot(s) available"
        )


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    else:
        require(not sys.argv[1:], "usage: validate_parallel_governance.py [--self-test]")
        main()
