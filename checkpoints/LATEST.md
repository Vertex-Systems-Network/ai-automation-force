# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m02-development-approved-governance-reconciled.md`

Current phase: **M02 — Durable Workflow Control Plane**

Status: **M02_DEVELOPMENT_APPROVED_CONTINUATION**

## Fresh development consent

Explicit operator authorization received on 2026-08-29:

`Milestone 2 development approve — start.`

This authorization governs M02 executable continuation from this checkpoint forward. It does not fabricate retroactive approval for historical WP1-WP5 merges.

## Historical governance reconciliation

The previous `M02_READY_FOR_CONSENT` checkpoint remained stale while M02 WP1-WP5 executable PRs merged. The contradiction is recorded truthfully in:

`checkpoints/2026-08-29-m02-development-approved-governance-reconciled.md`

WP1-WP5 are accepted as the current technical baseline based on their exact-head green CI evidence; historical consent is not retroactively asserted.

Current accepted `main` executable baseline before WP6 continuation:

`f1169d6a68b1a45248d343df58b882d8d15db7b6`

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

## Canonical M02 plan

`docs/milestones/M02/PLAN.md`

M02 work-package sequence:
1. WP1 — FastAPI application/control scaffold — merged/technical baseline accepted;
2. WP2 — Temporal foundation — merged/technical baseline accepted;
3. WP3 — job/idempotency/DB↔Temporal durability boundary — merged/technical baseline accepted;
4. WP4 — retry/backoff/circuit/cancellation — merged/technical baseline accepted;
5. WP5 — durable human/approval waits — merged/technical baseline accepted;
6. WP6 — fake external async callback/reconciliation pattern — **current executable target**;
7. WP7 — job/control API + durable SSE progress;
8. WP8 — replay/restart/100-shot recovery acceptance.

## Current WP6 state

PR `#15` / head `39a1429002b64b68a96550b95ec1b4d5e6ed2876` is open.

Current evidence before remediation:
- Core Domain Contracts: GREEN;
- Durable Control Plane: RED;
- four Temporal integration scenarios fail because workflow input expects `timeout_ms` while tests send `timeout_seconds`.

WP6 must not merge until the exact candidate head has both required workflows green and retained-history replay acceptance passes.

## M02 scope boundary

M02 excludes real provider execution/credentials/spend, object storage/media generation, content intelligence, full web/mobile/auth/billing/social implementation, production Temporal HA/DR rollout, public publishing, autonomous spend and M03+ development.

## Merge governance

GitHub `main` was previously observed as unprotected. Until repository protection is hardened, exact-head Core Domain Contracts + Durable Control Plane verification is a mandatory manual merge gate for executable M02 PRs.

GitHub remains canonical for engineering contracts, implementation evidence and checkpoints. Linear mirrors verified execution state.
