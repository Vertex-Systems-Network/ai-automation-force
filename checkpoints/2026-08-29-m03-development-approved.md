# M03 Development Approved

Date: 2026-08-29

Status: **M03_DEVELOPMENT_APPROVED_WP1_ACTIVE**

## Fresh operator authorization

The operator explicitly authorized M03 executable development with:

`Milestone 3 development approve — start.`

The authorization is fresh, milestone-specific, and applies to planned M03 scope only.

## Entry criteria

M03 entry criteria are satisfied:

- P0 complete;
- M01 accepted;
- M02 accepted and closed at `acf8d30f04124290cab97eab702c2cca6b9e3dcb`;
- explicit M03 consent received;
- object-storage SDK/local integration stack revalidated in `docs/architecture/M03-CURRENT-STACK-REVALIDATION-2026-08-29.md`.

## Revalidated implementation direction

- canonical SDK boundary: synchronous `boto3 1.43.83` / `botocore 1.43.83`;
- matching boto3 S3 stubs may be used for strict typing;
- provider-neutral core contracts; boto3 shapes must not leak into canonical models;
- deterministic filesystem adapter for local/unit development;
- preferred future network-level S3 compatibility target: Adobe S3Mock 5.1.0;
- Moto 5.2.3 permitted for focused test fixtures;
- MinIO Community Server is not a mandatory new CI dependency because current upstream community distribution is archived/source-only;
- aiobotocore 3.9.0 is not introduced because its botocore range does not support the current AWS SDK line.

## Current executable target

**M03-WP1 — Storage adapter and object metadata**

WP1 acceptance requires:

- stable storage-object IDs and canonical key rules;
- provider-neutral storage adapter contract;
- safe filesystem implementation;
- S3-compatible boto3 implementation;
- SHA-256/size/MIME/backend/region/version/ETag metadata semantics;
- path traversal/root escape protection;
- no credentials in domain state/logs;
- tests for deterministic keying, hashing and adapter behavior;
- existing M01/M02 regression gates remain green.

## M03 work-package sequence

1. WP1 — storage adapter and object metadata;
2. WP2 — upload sessions;
3. WP3 — quarantine/probe/security;
4. WP4 — asset lineage/provenance/rights;
5. WP5 — derivatives/proxies;
6. WP6 — signed delivery;
7. WP7 — retention/archive/delete/export primitives;
8. WP8 — milestone acceptance;
9. M03 closure and fresh M04 consent gate.

## Scope boundary

M03 does not authorize M04+ implementation, AI generation provider spend, public publishing/social execution, full web/mobile/auth/billing features, or autonomous destructive actions outside the M03 plan.

GitHub remains canonical. Linear mirrors verified execution state.
