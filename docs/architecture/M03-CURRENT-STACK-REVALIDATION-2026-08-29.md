# M03 Current Stack Revalidation — 2026-08-29

Status: **REVALIDATED_FOR_M03_ENTRY**

## Operator authorization

Fresh explicit operator authorization received on 2026-08-29:

`Milestone 3 development approve — start.`

This authorizes executable M03 work within `docs/milestones/M03/PLAN.md`. It does not authorize M04+ or expand M03 scope.

## Revalidation requirement

Current object-storage/provider SDK versions and the local test-storage stack were revalidated before the first executable M03 work package. A second freshness pass was performed before implementation after the initial evidence showed the fast-moving AWS SDK line had advanced again.

## Python S3 SDK decision

### boto3 / botocore

Observed current stable line on the final freshness pass:

- `boto3 1.43.83`
- `botocore 1.43.83`
- release date: 2026-08-28
- Python support includes repository Python 3.12
- Apache-2.0

Decision: **use synchronous boto3 as the initial S3-compatible adapter SDK**.

Reasons:

- AWS-maintained reference S3 client;
- custom S3-compatible endpoints supported;
- stable production SDK line;
- avoids an unnecessary async dependency-compatibility matrix in the canonical boundary;
- blocking SDK calls belong in worker Activities or bounded off-event-loop execution, never deterministic Temporal workflow code.

Canonical domain models must not expose boto3 request/response shapes.

### boto3 typing

Current generated `boto3-stubs` tracks the AWS SDK line and provides S3 typing. WP1 may pin the matching `1.43.83` typing line for strict mypy validation.

### aiobotocore

Observed current release:

- `aiobotocore 3.9.0`
- release date: 2026-08-01
- Python 3.12 supported
- declared botocore range `>=1.43.3,<1.43.57`

This does not cover current botocore `1.43.83`.

Decision: **do not add aiobotocore in M03-WP1**. Revisit only if an async transport is materially required and compatibility is revalidated then.

## Local S3-compatible integration target

### MinIO status change

The historical M03 plan mentioned a local MinIO/filesystem test adapter. Current upstream state changed materially:

- `minio/minio` community repository archived on 2026-04-25;
- community edition described as source-only distribution;
- historical precompiled releases are no longer maintained.

Decision: **do not make MinIO Community Server a mandatory new CI dependency**. Preserve S3/MinIO protocol compatibility as a target without anchoring merge acceptance to an archived server distribution.

## Test stack decision

### Adobe S3Mock

- active current 5.x line;
- immutable Docker release observed: `5.1.0`;
- Docker integration and multipart/checksum behavior;
- preferred network-level S3-compatible CI target when introduced.

### Moto

- current release observed: `5.2.3` (2026-08-22);
- Python 3.12 supported;
- Apache-2.0;
- suitable for focused Python fixtures where a network store is unnecessary.

Decision for M03:

1. filesystem adapter for deterministic local/unit use;
2. boto3 S3 adapter as production-facing S3-compatible boundary;
3. Adobe S3Mock 5.1.0 preferred future network-level CI compatibility target;
4. Moto 5.2.3 permitted for focused fixtures;
5. MinIO remains optional compatibility target, not required merge infrastructure.

## M03-WP1 implementation boundary

WP1 may implement:

- provider-neutral storage-object metadata/value contracts;
- storage adapter protocol;
- filesystem adapter with root containment and atomic writes;
- S3-compatible boto3 adapter with custom endpoint/region/path-style configuration;
- stable storage-object identity and object-key rules;
- SHA-256, MIME, byte-size, ETag/version/checksum metadata where trustworthy;
- storage-object persistence needed for WP1 only;
- no upload sessions (WP2), quarantine/probe (WP3), lineage/rights linkage (WP4), derivatives (WP5), signed delivery (WP6), or lifecycle orchestration (WP7).

## Security constraints

- callers never provide arbitrary filesystem paths;
- object keys are normalized canonical identities, not trusted host paths;
- credentials remain configuration/secrets and never canonical state/log data;
- endpoint URLs must not embed credentials;
- TLS verification defaults on; insecure local-test mode must be explicit;
- ETag is not a universal content hash;
- SHA-256 over actual bytes is canonical when bytes are available;
- no large binary fixture is committed to Git.

## Source evidence

Revalidation sources used on 2026-08-29:

- PyPI boto3/botocore current-release metadata (final observed latest `1.43.83`);
- PyPI boto3-stubs current generated typing line;
- PyPI aiobotocore 3.9.0 dependency metadata;
- `minio/minio` upstream repository/distribution notice;
- `adobe/S3Mock` releases/current 5.x changelog;
- PyPI Moto 5.2.3 metadata.

Mutable versions must be revalidated again if execution crosses a meaningful dependency-update boundary.
