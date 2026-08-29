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
- Initial canonical S3 SDK: boto3/botocore `1.43.80`.
- `aiobotocore 3.9.0` is not introduced because its current botocore compatibility range does not include `1.43.80`.
- Filesystem adapter is the deterministic local/unit implementation.
- Preferred future network-level S3 CI target: Adobe S3Mock `5.1.0`.
- Moto `5.2.3` may be used for focused fixtures.
- MinIO Community Server is not a mandatory new CI dependency because the upstream community repository is archived/source-only; S3/MinIO protocol compatibility remains a target.

## Current executable target

**M03-WP1 — Storage adapter and object metadata**

Required WP1 scope:

- provider-neutral storage adapter interface;
- stable storage object IDs/object keys;
- deterministic filesystem adapter with path containment and atomic writes;
- S3-compatible boto3 adapter with configurable endpoint/region/addressing;
- SHA-256, MIME, byte size, region, version ID and ETag metadata semantics;
- credentials/configuration never become canonical domain state;
- no upload-session API (WP2), quarantine/probe pipeline (WP3), derivatives (WP5), signed delivery (WP6), or retention implementation (WP7) yet;
- exact-head required CI and existing M01/M02 regressions must be green before merge.

## Remaining M03 sequence

1. WP1 — storage adapter and object metadata;
2. WP2 — upload sessions;
3. WP3 — quarantine/probe/security;
4. WP4 — asset lineage/provenance/rights;
5. WP5 — derivatives/proxies;
6. WP6 — signed delivery;
7. WP7 — retention/archive/delete/export primitives;
8. WP8 — acceptance;
9. M03 closure and fresh M04 consent gate.

## Consent boundary

M03 authorization does not authorize M04+ executable work. Generic continuation commands may continue already-authorized M03 work but cannot expand beyond M03 or authorize M04.

GitHub remains canonical for engineering contracts, implementation evidence and checkpoints. Linear mirrors verified execution state.
