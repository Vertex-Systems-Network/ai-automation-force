# Checkpoint — M02 Ready for Development Consent

Date: 2026-08-29

Status: **M02_READY_FOR_CONSENT**

Milestone:
**M02 — Durable Workflow Control Plane**

## Entry criteria

- P0 Full Project Preplanning: complete.
- M01 Core Domain & Persistence Boundary: complete.
- M01 final checkpoint: `checkpoints/2026-08-29-m01-complete.md`.
- M02 canonical work-package plan exists: `docs/milestones/M02/PLAN.md`.
- current FastAPI/Temporal mutable facts revalidated.
- scoped M02 Development Consent Brief prepared.

## Canonical consent brief

`docs/architecture/M02-DEVELOPMENT-CONSENT-BRIEF.md`

## Current-stack evidence

`docs/architecture/M02-CURRENT-STACK-REVALIDATION-2026-08-29.md`

Revalidation verdict:
`PASS — EXISTING FASTAPI + TEMPORAL ARCHITECTURE REMAINS VALID`

Planning-time current stable versions observed:
- FastAPI `0.141.1`;
- Temporal Python SDK `1.30.0`;
- Temporal CLI `1.8.1`;
- Temporal Server `1.31.2`.

These values are evidence, not executable dependency pins. Revalidate immediately before implementation.

## Planned M02 execution sequence

1. WP1 — FastAPI application/control scaffold
2. WP2 — Temporal foundation
3. WP3 — job/idempotency/DB↔Temporal durability boundary
4. WP4 — retry/backoff/circuit/cancellation
5. WP5 — durable human/approval waits
6. WP6 — fake external async callback/reconciliation pattern
7. WP7 — job/control API + SSE progress surface
8. WP8 — replay/restart/100-shot recovery acceptance

## Exit target

A synthetic 100-shot project can fan out/join, wait, retry, cancel where supported, survive worker/API restarts and resume without duplicate completed jobs or side effects, with retained Temporal histories replaying successfully.

## Scope safety

M02 deliberately excludes:
- real AI provider execution/credentials/spend;
- object storage/media pipeline;
- content intelligence;
- production generation/rendering;
- full web/mobile/auth/billing/social implementation;
- production Temporal HA/DR provisioning;
- M03+ executable work.

## Known governance risk

GitHub currently reports `main` as unprotected with no required status-check enforcement. This is recorded for early reviewed hardening or explicit temporary acceptance during approved M02 execution. No repository protection setting has been changed by this planning checkpoint.

## Consent state

**Executable M02 development is NOT authorized yet.**

Required explicit approval phrase may be:

`Milestone 2 development approve — start.`

Generic `continue`, `next`, `resume`, or `audit` remains planning-only.