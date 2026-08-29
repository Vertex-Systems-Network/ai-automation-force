# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m02-wp7-complete.md`

Current phase: **M02 — Durable Workflow Control Plane**

Status: **M02_WP7_COMPLETE_WP8_ACTIVE**

## Development consent

Explicit operator authorization received on 2026-08-29:

`Milestone 2 development approve — start.`

Canonical consent/governance reconciliation:
`checkpoints/2026-08-29-m02-development-approved-governance-reconciled.md`

## Completed baseline

- M01 complete: `424b76214ab8eb94d3205a2eba2d75cf4ffa0cc7`
- M02 WP1 — FastAPI scaffold: `c8591278ed0fc5624e1bff6169d7684ad36e01dd`
- M02 WP2 — Temporal foundation: `29a3432480027f63f9c572782297e8707c501730`
- M02 WP3 — job/idempotency/outbox: `0de15a90cff5f44eeccdaf1d667aba69b890bbcc`
- M02 WP4 — retry/circuit/cancel: `54c613a5adfa95c6ebc5d6699cf7dbafa140d68e`
- M02 WP5 — durable approval waits: `f1169d6a68b1a45248d343df58b882d8d15db7b6`
- M02 governance reconciliation: `12a4e33678beb6e6c5fce41f9c8b5c312083aa3a`
- M02 WP6 — fake async provider callback/reconciliation: `2b93c023249852d29862abbe36f6b2f46f9f02d4`
- M02 WP7 — job control API + durable SSE progress: `b1e99d0da6b38ae3c826c15bb594c40b8c34d607`

## WP7 verified acceptance

Exact executable candidate head:
`81489ce89290dc05e1b14784d174247ac31701ba`

Fresh required CI on replacement PR #19:
- Core Domain Contracts `33258197047` / job `99115470093` — GREEN
- Durable Control Plane `33258197044` / job `99115470409` — GREEN

WP7 completion checkpoint:
`checkpoints/2026-08-29-m02-wp7-complete.md`

## Current executable target

**M02-WP8 — Replay, restart and synthetic 100-shot recovery acceptance**

Required acceptance package:
- synthetic 100-shot fan-out/join;
- controlled worker/process kill and restart recovery;
- API restart independence from workflow durability;
- Activity retry/recovery;
- duplicate event and callback injection;
- cancellation recovery;
- manual approval wait/resume;
- retained Temporal histories and deterministic replay verification;
- no duplicate terminal side effects/actions;
- correct canonical completion state across 100 shots;
- Continue-As-New/history-growth policy proof where threshold applies;
- all M01/M02 required CI gates remain green;
- unverified claims explicitly recorded rather than inferred.

## Remaining M02 sequence

1. WP8 — replay/restart/synthetic 100-shot recovery acceptance;
2. M02 closure checkpoint;
3. fresh M03 consent gate.

## Merge governance

Until repository protection automatically enforces the same policy, executable M02 PRs require exact-candidate-head Core Domain Contracts + Durable Control Plane verification before merge.

## Scope boundary

M02 excludes real provider execution/credentials/spend, object storage/media generation, content intelligence, full web/mobile/auth/billing/social implementation, production Temporal HA/DR rollout, public publishing, autonomous spend and M03+ development.

GitHub remains canonical for engineering contracts, implementation evidence and checkpoints. Linear mirrors verified execution state.
