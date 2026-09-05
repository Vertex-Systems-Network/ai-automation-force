# CROSS-CUTTING-QA Checkpoint

## Current state

- Issue: #73
- Branch: `agent/cross-cutting-qa-security`
- Baseline before QA planning: `main@76b91c15752c0b5840cc5094f74d612a43d4499e`
- Authority: audit/planning only
- Executable tests: not authorized by this slice
- Migration reservation: none
- Provider/credential/spend/public side effects: none

## Completed in this slice

- reused M03-WP8 source-acceptance evidence instead of duplicating tests;
- mapped all 10 `AI-AGENT-THREAT-MODEL.md` required scenarios to current/partial/deferred evidence states;
- defined cross-cutting fail-closed authority, tenant, secret, memory, provider, budget and rights invariants;
- assigned future adversarial hooks to M04, M05, M06, M07 and M08 planning surfaces;
- kept Issue #36 separate as `EXTERNAL_NOT_VERIFIED` protected-main evidence.

Canonical audit plan:

- `docs/qa/ADVERSARIAL-AUDIT-PLAN.md`

## Important boundary

The threat model explicitly defines generic `continue` as insufficient privileged authorization. This checkpoint therefore does not treat conversational continuation as authority to begin M04 executable development while M03 final governance acceptance remains blocked by Issue #36.

## Next action

For the next module seeking executable promotion, re-evaluate only the newly reachable security surfaces and add minimum targeted adversarial tests under that module's authorized scope. Do not create synthetic umbrella tests or use production credentials/paid providers merely to satisfy planning evidence.

Work Done and Submitted
