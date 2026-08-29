# M03 Current Stack Revalidation — 2026-08-29

Status: **REVALIDATED_FOR_M03_ENTRY**

## Operator authorization

Fresh explicit operator authorization received on 2026-08-29:

`Milestone 3 development approve — start.`

This authorizes executable M03 work within `docs/milestones/M03/PLAN.md`. It does not authorize M04+ or expand the M03 scope.

## Revalidation requirement

`checkpoints/LATEST.md` required current object-storage/provider SDK versions and the local test-storage stack to be revalidated before the first executable M03 work package.

Revalidation was performed against current upstream/PyPI information on 2026-08-29.

## Python S3 SDK decision

### boto3 / botocore

Observed current stable line:

- `boto3 1.43.80`
- `botocore 1.43.80`
- release date: 2026-08-25
- Python support includes Python 3.12 used by this repository
- Apache-2.0

Decision: **use synchronous boto3 as the initial S3-compatible adapter SDK**.

Reasons:

- AWS-maintained reference S3 client;
- works with custom S3-compatible endpoints;
- stable production status;
- avoids introducing an async compatibility matrix into the canonical storage boundary;
- blocking SDK calls belong in worker Activities or bounded thread/off-event-loop execution, not inside deterministic Temporal workflow code.

The canonical domain API remains provider-neutral and must not expose boto3 request/response shapes.

### aiobotocore

Observed current release:

- `aiobotocore 3.9.0`
- release date: 2026-08-01
- supports Python 3.12
- its declared botocore range is `>=1.43.3,<1.43.57`

This does not cover current botocore `1.43.80`.

Decision: **do not add aiobotocore in M03-WP1**. Revisit only if an async transport is materially required and its botocore compatibility is revalidated at that time.

## Local S3-compatible integration target

### MinIO status change

The historical M03 plan mentioned a local MinIO/filesystem test adapter. Current upstream state changed materially:

- the `minio/minio` community repository was archived on 2026-04-25;
- the community edition is described as source-only distribution;
- historical precompiled releases are no longer maintained.

Decision: **do not make MinIO Community Server a new mandatory CI dependency**. Preserve MinIO/S3 compatibility as a protocol target, but do not anchor M03 acceptance to an archived server distribution.

The MinIO Python client remains available, but M03-WP1 does not use it as the canonical SDK because boto3 provides the reference S3-compatible boundary required by the plan.

## Test stack decision

Two active test options were revalidated:

### Adobe S3Mock

- current 5.x line is actively developed;
- current immutable Docker release observed: `5.1.0`;
- supports Docker integration and S3 multipart/checksum behavior;
- suitable for network-level S3-compatible integration tests.

### Moto

- current release observed: `5.2.3` (2026-08-22);
- Python 3.12 supported;
- Apache-2.0;
- suitable for fast Python-level S3 behavior tests/mocks.

Decision for M03:

1. **filesystem adapter** for deterministic local/unit tests and development without network/object-store dependency;
2. **boto3 S3 adapter** as the production-facing S3-compatible implementation boundary;
3. **Adobe S3Mock 5.1.0** as the preferred network-level CI compatibility target when container integration is introduced;
4. **Moto 5.2.3** may be used for focused unit/integration fixtures where a full network store is unnecessary;
5. MinIO remains an optional compatibility target and is not required for merge acceptance.

## M03-WP1 implementation boundary

WP1 may now implement:

- provider-neutral object metadata/value contracts;
- storage adapter protocol/interface;
- filesystem adapter with root containment and atomic writes;
- S3-compatible boto3 adapter with custom endpoint/region/path-style configuration;
- stable storage-object identity and object-key rules;
- SHA-256, MIME, byte-size, ETag/version/checksum metadata where trustworthy;
- no upload-session API yet (WP2);
- no quarantine/probe pipeline yet (WP3);
- no derivatives/signed delivery/retention implementation yet (WP5-WP7).

## Security constraints

- no arbitrary filesystem paths from callers;
- object keys are normalized canonical identities, never trusted host paths;
- credentials remain configuration/secrets, never canonical domain state or logs;
- endpoint URLs must not embed credentials;
- TLS verification defaults on; insecure local test mode must be explicit;
- do not treat ETag as a universal content hash;
- SHA-256 content digest is canonical when content bytes are available;
- no large binary fixture is committed to Git.

## Source evidence

Revalidation sources:

- PyPI `boto3` / `botocore` current release metadata;
- PyPI `aiobotocore 3.9.0` dependency metadata;
- `minio/minio` GitHub repository status/distribution notice;
- `adobe/S3Mock` GitHub releases/current 5.x changelog;
- PyPI `moto 5.2.3` metadata.

Mutable versions must be revalidated again if M03 execution crosses a meaningful dependency-update boundary.
