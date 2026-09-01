from __future__ import annotations

import json
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
    require("latest_broadcast_sequence: 1" in state, "Supervisor state broadcast sequence is stale")

    revisions: list[str] = []
    for raw in migrations.splitlines():
        line = raw.strip()
        if line.startswith("- revision:"):
            revisions.append(line.split(":", 1)[1].strip())
    require(len(revisions) == len(set(revisions)), "duplicate migration reservations detected")

    if open_slots == 0:
        print(f"Parallel governance PASS: all module slots occupied; response='{REJECTION}'")
    else:
        print(f"Parallel governance PASS: {open_slots} open module slot(s) available")


if __name__ == "__main__":
    main()
