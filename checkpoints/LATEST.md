# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m03-development-approved.md`

Current phase: **M03 — Asset Storage and Provenance**

Status: **M03_DEVELOPMENT_APPROVED_WP1_ACTIVE**

## Completed baseline

- M01 complete: `424b76214ab8eb94d3205a2eba2d75cf4ffa0cc7`
- M02 complete/closure checkpoint merge: `acf8d30f04124290cab97eab702c2cca6b9e3dcb`
- M02 final executable WP8 merge: `bb82c3bd115723504cf233e0cab93ca9513d10a8`

## M03 development consent

Fresh explicit operator authorization received on 2026-08-29:

`Milestone 3 development approve — start.`

M03 consent checkpoint:
`checkpoints/2026-08-29-m03-development-approved.md`

Current stack revalidation:
`docs/architecture/M03-CURRENT-STACK-REVALIDATION-2026-08-29.md`

## Revalidated storage baseline

- Python runtime remains 3.12+.
- Final pre-WP1 freshness pass: boto3/botocore `1.43.83` (2026-08-28).
- matching boto3 S3 stubs may be pinned for strict mypy.
- `aiobotocore 3.9.0` is not introduced because its current botocore range does not include the current AWS SDK line.
- filesystem adapter is the deterministic local/unit implementation.
- preferred future network-level S3 CI target: Adobe S3Mock `5.1.0`.
- Moto `5.2.3` may be used for focused fixtures.
- MinIO Community Server is not a mandatory new CI dependency because current upstream community distribution is archived/source-only; S3/MinIO protocol compatibility remains a target.

## Current executable target

**M03-WP1 — Storage adapter and object metadata** / Linear `ABD-200`

Required WP1 scope:

- provider-neutral storage adapter interface;
- stable storage-object IDs/object keys;
- deterministic filesystem adapter with path containment and atomic writes;
- S3-compatible boto3 adapter with configurable endpoint/region/addressing;
- SHA-256, MIME, byte size, backend, region, version ID and ETag metadata semantics;
- preserve existing canonical Asset rather than duplicating it;
- credentials/configuration never become canonical domain state;
- no upload-session API (WP2), quarantine/probe (WP3), provenance linkage (WP4), derivatives (WP5), signed delivery (WP6), or retention orchestration (WP7) yet;
- exact-head required CI and existing M01/M02 regressions must be green before merge.

## Linear M03 execution chain

- WP1 `ABD-200` — In Progress
- WP2 `ABD-201` — Backlog, blocked by WP1
- WP3 `ABD-202` — Backlog, blocked by WP2
- WP4 `ABD-203` — Backlog, blocked by WP3
- WP5 `ABD-204` — Backlog, blocked by WP4
- WP6 `ABD-205` — Backlog, blocked by WP5
- WP7 `ABD-206` — Backlog, blocked by WP6
- WP8 `ABD-207` — Backlog, blocked by WP7

## Consent boundary

M03 authorization does not authorize M04+ executable work. Generic continuation commands may continue already-authorized M03 work but cannot expand beyond M03 or authorize M04.

GitHub remains canonical for engineering contracts, implementation evidence and checkpoints. Linear mirrors verified execution state.
