# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m02-ready-for-consent.md`

Current phase: **M02 — Durable Workflow Control Plane**

Status: **M02_READY_FOR_CONSENT**

## Previous completed milestone

M01 — Core Domain & Persistence Boundary is complete.

Final M01 checkpoint:
`checkpoints/2026-08-29-m01-complete.md`

M01 closure merge commit:
`424b76214ab8eb94d3205a2eba2d75cf4ffa0cc7`

Verified M01 executable evidence:
`33221966779 / 99017705054`

## Full-project planning prerequisite

P0 Full Project Preplanning is complete.

Checkpoint:
`checkpoints/2026-08-29-full-project-preplanning-complete.md`

Status:
`FULL_PROJECT_PLANNING_READY_FOR_CONSENT`

## M02 readiness

Canonical milestone plan:
`docs/milestones/M02/PLAN.md`

Development Consent Brief:
`docs/architecture/M02-DEVELOPMENT-CONSENT-BRIEF.md`

Current stack revalidation:
`docs/architecture/M02-CURRENT-STACK-REVALIDATION-2026-08-29.md`

Readiness checkpoint:
`checkpoints/2026-08-29-m02-ready-for-consent.md`

M02 work-package sequence:
1. WP1 — FastAPI application/control scaffold;
2. WP2 — Temporal foundation;
3. WP3 — job/idempotency/DB↔Temporal durability boundary;
4. WP4 — retry/backoff/circuit/cancellation;
5. WP5 — durable human/approval waits;
6. WP6 — fake external async callback/reconciliation pattern;
7. WP7 — job/control API + SSE progress;
8. WP8 — replay/restart/100-shot recovery acceptance.

## Current mutable-stack evidence

Planning-time current stable versions observed on 2026-08-29:
- FastAPI `0.141.1`;
- Temporal Python SDK `1.30.0`;
- Temporal CLI `1.8.1`;
- Temporal Server `1.31.2`.

These are not runtime pins yet. They must be revalidated immediately before dependency/runtime changes.

## Consent state

**M02 executable development is blocked pending fresh explicit operator approval.**

The prior M01 approval has been consumed and does not authorize M02.

A valid explicit authorization may be:

`Milestone 2 development approve — start.`

Generic `continue`, `next`, `resume`, `audit`, or planning instructions remain non-authorizing.

## M02 scope boundary

M02 excludes real provider execution/credentials/spend, object storage/media generation, content intelligence, full web/mobile/auth/billing/social implementation, production Temporal HA/DR rollout, public publishing, autonomous spend and M03+ development.

## Known governance risk

GitHub currently reports `main` as unprotected with no required-status-check enforcement. No branch-protection setting was changed during planning. Early approved M02 execution should either harden this through a reviewed repository-governance change or explicitly record temporary acceptance.

## GitHub ↔ Linear

GitHub remains canonical for engineering contracts, implementation evidence and checkpoints. Linear mirrors milestone/work-package readiness and execution status.
