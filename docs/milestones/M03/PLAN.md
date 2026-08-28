# M03 — Asset Storage and Provenance

## Objective

Implement the canonical asset/media lifecycle on S3-compatible storage with upload validation, lineage, rights/provenance and signed access.

## Entry criteria

- P0 complete.
- M01/M02 accepted.
- Explicit M03 consent.
- Object-storage/provider SDK versions revalidated.

## Dependencies

`M01 -> M02 -> M03`

## Work packages

### M03-WP1 — Storage adapter and object metadata
- S3-compatible interface;
- local MinIO/filesystem test adapter;
- stable object/asset IDs;
- hashes/MIME/size/region/lifecycle metadata.

### M03-WP2 — Upload sessions
- signed direct upload;
- multipart/resumable;
- quota reservation;
- complete/abort/expiry;
- idempotency.

### M03-WP3 — Quarantine/probe/security
- MIME/magic validation;
- size/type limits;
- media probe;
- malware/threat hook;
- resource-limited parser/FFmpeg worker;
- accept/reject lifecycle.

### M03-WP4 — Asset lineage/provenance/rights
- source/import/provider references;
- derived-from graph;
- rights/licensing/consent links;
- approved/rejected state;
- content hashes.

### M03-WP5 — Derivatives/proxies
- thumbnails;
- image previews;
- audio waveform/preview;
- video proxy/poster;
- lineage and deterministic derivative job records.

### M03-WP6 — Signed delivery
- authorized short-lived download/stream URLs;
- Range support strategy;
- private/public asset classes;
- share-link constraints.

### M03-WP7 — Retention/archive/delete/export primitives
- temp cleanup;
- soft/hard deletion propagation;
- archive/restore states;
- export staging object;
- vector/index cleanup hooks.

### M03-WP8 — Acceptance
- multipart interruption/resume;
- cross-tenant signed URL denial;
- malicious/malformed fixtures;
- lineage/hash integrity;
- deletion/temp cleanup;
- archive/restore smoke.

## Expected modules/files

- storage/asset package in backend;
- upload API endpoints;
- media probe worker activities;
- object-storage configuration;
- asset/provenance DB migrations;
- test media fixtures.

## Data/migration impact

Adds Asset, StorageObject, UploadSession, derivative/provenance/rights relationships and retention states.

## API/UI impact

Adds asset metadata, upload-session, completion, signed-access and status APIs. Full asset-library UI comes later but API contracts are established.

## Security/cost/rights impact

- tenant-scoped signed URLs;
- untrusted upload quarantine;
- no arbitrary filesystem paths;
- storage/egress tracking;
- rights/provenance required for canonical usable assets according to policy.

## Test/acceptance

Apply storage/upload/media sections of Master QA plus tenant isolation/security tests.

## Rollout/rollback

Object creation is append-oriented. Deletion during development uses isolated buckets. Migrations remain compatible; source assets are never destructively overwritten by derivative work.

## Exit criteria

Every test media asset is traceable, validated, tenant-safe, signed-accessible and lineage/rights aware without storing large binaries in Git.

## Non-goals

- character UI;
- content generation providers;
- full timeline/editor;
- production CDN/adaptive streaming optimization;
- billing UI.
