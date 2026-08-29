# M02 Development Consent & Governance Reconciliation

Date: 2026-08-29

Status: **M02_DEVELOPMENT_APPROVED_CONTINUATION**

## Fresh operator authorization

Fresh explicit operator authorization was received on 2026-08-29:

`Milestone 2 development approve — start.`

This authorization permits executable work inside the existing M02 scope from this checkpoint forward. It does **not** retroactively claim that the earlier M02 executable merges were authorized by the stale pre-consent checkpoint.

## Historical governance reconciliation

Before this fresh authorization, `checkpoints/LATEST.md` still reported `M02_READY_FOR_CONSENT` while M02 WP1-WP5 executable pull requests had already merged to `main`. That contradiction is preserved as a historical governance defect rather than rewritten away.

The already-merged WP1-WP5 trees are accepted as the current technical baseline because their exact PR heads were covered by green milestone CI before merge. This technical acceptance is distinct from, and does not fabricate, historical consent.

### WP1 — FastAPI control-plane scaffold

- PR: `#10`
- exact verified PR head: `8ae05b18e42afcb7b008e9acffb235f7a084738f`
- merge commit: `c8591278ed0fc5624e1bff6169d7684ad36e01dd`
- Durable Control Plane run: `33223054566` / run `#1` — GREEN
- the Durable workflow reran the required M01 regression gates for this stage

### WP2 — Temporal durable-workflow foundation

- PR: `#11`
- exact verified PR head: `0a2278a4f5d86037923c7fe46e2d724f506280e9`
- merge commit: `29a3432480027f63f9c572782297e8707c501730`
- Core Domain Contracts run `#74` — GREEN
- Durable Control Plane run `#10` — GREEN

### WP3 — Job idempotency and transactional outbox control

- PR: `#12`
- exact verified PR head: `bb9c96dbf5d71c887ac5c14e72706394f58bcdfc`
- merge commit: `0de15a90cff5f44eeccdaf1d667aba69b890bbcc`
- Core Domain Contracts run `#79` — GREEN
- Durable Control Plane run `#15` — GREEN

### WP4 — Retry, circuit breaker and cancellation control

- PR: `#13`
- exact verified PR head: `461a37c512bb98bf223f0c57dec59a7bd05c00cd`
- merge commit: `54c613a5adfa95c6ebc5d6699cf7dbafa140d68e`
- Core Domain Contracts run `#82` — GREEN
- Durable Control Plane run `#18` — GREEN

### WP5 — Durable human approval waits and safe resume

- PR: `#14`
- exact verified PR head: `ea5f18424850cb85d98cc9f5231b73bb98b78804`
- merge commit: `f1169d6a68b1a45248d343df58b882d8d15db7b6`
- Core Domain Contracts run `#85` — GREEN
- Durable Control Plane run `#21` — GREEN

## Current executable baseline

`main` baseline at reconciliation entry:

`f1169d6a68b1a45248d343df58b882d8d15db7b6`

WP1-WP5 remain in place. They are not reverted merely because the consent checkpoint was stale; instead, their technical evidence is explicitly reconciled here and fresh authorization governs all continuation/remediation from this point.

## Immediate continuation target

M02-WP6 / PR `#15` is the next executable work package.

PR `#15` is **not accepted or mergeable by policy yet** despite GitHub reporting it mechanically mergeable, because Durable Control Plane CI is red on current head `39a1429002b64b68a96550b95ec1b4d5e6ed2876`.

Known WP6 blocker:

- workflow input reads `timeout_ms` / `poll_interval_ms`;
- Temporal integration scenarios currently send `timeout_seconds` / `poll_interval_seconds`;
- the resulting `KeyError: 'timeout_ms'` causes four integration scenarios to time out.

WP6 must be remediated and pass exact-head Core + Durable CI before merge.

## M02 remaining sequence

1. WP6 — fake external async callback/reconciliation pattern;
2. WP7 — job/control API + durable SSE progress;
3. WP8 — replay/restart/synthetic 100-shot recovery acceptance;
4. M02 closure checkpoint and a fresh M03 consent gate.

## Scope boundary retained

M02 still excludes:

- real AI provider credentials/calls/spend;
- production object storage/media generation;
- content intelligence;
- full web/mobile/auth/billing/social implementation;
- public publishing/autonomous spend;
- M03+ executable work.

## Governance controls for continuation

- GitHub remains canonical for implementation evidence/checkpoints.
- Linear mirrors execution state only after canonical evidence is updated.
- Do not merge a work package with red or unverified required CI.
- Do not claim network/workflow exactly-once delivery; use durable at-least-once execution with idempotent side effects.
- Preserve retained Temporal history replay compatibility across workflow changes.
- Historical checkpoints remain immutable evidence; this checkpoint supersedes the stale consent state without rewriting history.

## Repository protection risk

`main` was previously observed as unprotected with no required-status-check enforcement. Until repository rules are hardened, M02 execution will enforce the equivalent process manually: exact-head required CI must be verified green before every merge.
