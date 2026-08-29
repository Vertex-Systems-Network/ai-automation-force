# M03 Development Consent Brief — Asset Storage and Provenance

Date prepared: 2026-08-29

Status: **READY_FOR_M03_CONSENT — EXECUTABLE WORK BLOCKED**

## Why M03 exists

M03 establishes the canonical asset/media lifecycle required by later generation, editing, publishing and provenance features. The milestone introduces S3-compatible storage abstractions, validated upload sessions, quarantine/probe controls, lineage/rights records, derivatives, signed delivery and retention primitives.

Canonical milestone plan:

`docs/milestones/M03/PLAN.md`

## Entry state

- P0 planning is complete.
- M01 is complete.
- M02 is complete at `bb82c3bd115723504cf233e0cab93ca9513d10a8` with closure evidence in `checkpoints/2026-08-29-m02-complete.md`.
- M03 has not received executable development consent.
- Current object-storage/provider SDK versions and the local test-storage stack must be revalidated before the first executable M03 work package.

## Planned work packages

### M03-WP1 — Storage adapter and object metadata

- S3-compatible interface;
- local MinIO/filesystem test adapter;
- stable object/asset identities;
- hash, MIME, size, region and lifecycle metadata.

### M03-WP2 — Upload sessions

- signed direct upload;
- multipart/resumable upload;
- quota reservation;
- complete/abort/expiry;
- idempotent session operations.

### M03-WP3 — Quarantine, probe and security

- MIME/magic validation;
- size/type policy;
- media probe;
- malware/threat hook;
- resource-limited parser/FFmpeg worker;
- deterministic accept/reject lifecycle.

### M03-WP4 — Asset lineage, provenance and rights

- source/import/provider references;
- derived-from graph;
- rights/licensing/consent links;
- approved/rejected usability state;
- content hashes.

### M03-WP5 — Derivatives and proxies

- thumbnails and image previews;
- audio waveform/preview;
- video proxy/poster;
- deterministic derivative jobs;
- provenance linkage back to source assets.

### M03-WP6 — Signed delivery

- authorized short-lived download/stream URLs;
- Range support strategy;
- private/public asset classes;
- constrained share-link semantics.

### M03-WP7 — Retention, archive, delete and export primitives

- temporary-object cleanup;
- soft/hard deletion propagation;
- archive/restore state;
- export staging objects;
- vector/index cleanup hooks for later milestones.

### M03-WP8 — Acceptance

- multipart interruption/resume;
- cross-tenant signed-URL denial;
- malicious/malformed upload fixtures;
- lineage/hash integrity;
- deletion/temp cleanup;
- archive/restore smoke acceptance.

## Security and rights boundary

M03 must fail closed around untrusted media and tenant boundaries:

- no arbitrary filesystem paths from user input;
- uploaded objects remain quarantined until policy checks complete;
- signed access is tenant-scoped and short-lived;
- parser/probe/FFmpeg work is resource-limited;
- canonical usable assets carry required provenance/rights state according to policy;
- source assets are not destructively overwritten by derivatives;
- secrets/private large media are not placed in workflow payloads or Git.

## Cost boundary

Development acceptance should default to local/test storage and synthetic fixtures. No production cloud bucket, paid storage/egress, CDN commitment or external media-provider spend is authorized by this brief. Any production credential or cost-bearing rollout requires separate configuration and deployment approval within the applicable later gate.

## Non-goals

M03 does not authorize:

- content-generation provider integration;
- character UI;
- full timeline/editor;
- production CDN/adaptive streaming optimization;
- billing UI;
- public publishing/social distribution;
- M04+ executable development.

## Required pre-execution revalidation

After explicit M03 consent and before the first executable WP1 change:

1. revalidate the current supported S3-compatible Python SDK/client choice and version;
2. revalidate MinIO/local test-storage tooling and compatibility;
3. revalidate signed-upload/download capabilities needed for multipart, Range and expiry semantics;
4. revalidate media probing/FFmpeg packaging and security posture;
5. record the selected versions and rationale in canonical repository documentation;
6. do not silently widen M03 scope if upstream capabilities differ from planning assumptions.

## Merge governance

Until repository protection automatically enforces equivalent rules, every executable M03 PR must be evaluated against its work-package scope and required exact-candidate-head CI before merge. Red, skipped or unverified required acceptance blocks merge.

## Consent semantics

M02 authorization is consumed and cannot be reused for M03.

The following are explicitly non-authorizing for M03 executable work:

- `continue`
- `next`
- `resume`
- `audit`
- research/planning requests
- requests to update documentation only

A valid explicit authorization phrase is:

`Milestone 3 development approve — start.`

Equivalent language is valid only when it clearly and explicitly authorizes **M03 executable development**, not merely planning, audit or continuation.

Until that consent is received, permitted work is limited to planning, research/revalidation, documentation, issue/milestone reconciliation and other non-executable preparation.
