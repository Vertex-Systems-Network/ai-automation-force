# Media Storage, Upload, Delivery and Archival

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define the complete media I/O lifecycle for a platform that handles generated and uploaded images, audio and video from small thumbnails through multi-hour masters.

## Principles

- large media never lives in ordinary Git history;
- canonical metadata is separate from binary object storage;
- users upload directly to controlled object storage whenever practical;
- every asset has hash/provenance/tenant ownership;
- untrusted uploads pass quarantine/validation;
- derivatives/proxies are separate versioned assets;
- download/streaming authorization is short-lived and scoped;
- storage/egress/retention are entitlement-aware;
- deletion/export includes derived objects and indexes.

## Storage abstraction

Use S3-compatible object-storage semantics behind an internal storage adapter.

Canonical `StorageObject`/asset metadata includes:
- asset ID;
- workspace/project;
- object key;
- storage backend/region;
- content hash;
- size;
- MIME/media type;
- original filename as metadata only;
- source/import/provider;
- lifecycle class;
- encryption/status;
- created/verified/deleted timestamps.

Business logic uses Asset IDs, not provider/cloud bucket paths.

## Object namespaces

Logical prefixes/classes:
- `uploads/quarantine/`
- `source/`
- `characters/`
- `references/`
- `generated/images/`
- `generated/audio/`
- `generated/video/`
- `proxies/`
- `thumbnails/`
- `renders/`
- `exports/`
- `temporary/`
- `archive/`

Actual keys should include opaque tenant/resource identifiers, not user-controlled paths.

## Upload modes

### Small/simple upload
For small permitted files, signed single-object upload can be used.

### Multipart/resumable upload
Required for large video/audio/project imports.

Flow:
`Create Upload Session -> Authorization/Entitlement -> Signed part URLs or resumable protocol -> Upload parts -> Complete -> Verify hash/size -> Quarantine validation -> Canonical asset`

Upload session includes:
- expected size/type;
- part state;
- expiry;
- workspace/project;
- creator;
- quota reservation;
- completion idempotency;
- status.

## Direct upload constraints

Signed upload grant limits:
- exact workspace-derived key;
- maximum size;
- allowed content type/class;
- short expiry;
- method;
- multipart upload ID where relevant.

User cannot choose arbitrary bucket/object paths.

## Validation pipeline

`QUARANTINED -> HASHED -> TYPE_VERIFIED -> PROBED -> SECURITY_CHECKED -> ACCEPTED | REJECTED`

Checks:
- actual bytes vs claimed MIME/extension;
- size limits;
- media parseability;
- dimensions/duration/codec where relevant;
- malware/threat scanning where applicable;
- malformed/container exploit risk;
- metadata policy;
- rights/import declaration requirements.

Rejected uploads do not become routable production assets.

## Media probe

Extract canonical technical metadata:
- duration;
- resolution;
- frame rate;
- codecs;
- channels/sample rate;
- bitrate;
- color space/HDR metadata where relevant;
- orientation;
- timestamps when useful;
- embedded subtitles/tracks;
- basic container integrity.

Probe runs in resource-limited media worker.

## Asset derivation graph

Derived assets preserve lineage:
- source -> proxy;
- source -> thumbnail/poster;
- image -> cropped aspect variants;
- audio -> waveform/normalized preview;
- video -> preview/proxy;
- approved shots -> master render;
- master -> social derivatives.

Never overwrite source asset in place. Every derivative has own ID/hash/type with `derived_from` references.

## Proxy strategy

Use lighter proxies for:
- timeline/editor playback;
- review links;
- mobile preview;
- storyboard/contact sheets.

Proxy policy can vary by source:
- image thumbnail sizes;
- low/medium video proxy;
- audio preview waveform/stream.

Editorial timing references canonical source while UI may play proxy.

## Image delivery

Support:
- thumbnail/list variants;
- preview;
- original/approved source when authorized;
- content disposition download;
- appropriate cache control;
- format optimization only as derived asset, not destructive replacement.

## Video/audio streaming

Initial architecture supports HTTP range requests/signed object delivery through controlled CDN/object storage.

For long-form/high-scale playback, architecture may produce adaptive streaming packages (HLS/DASH or current equivalent) as derived outputs when justified.

Do not require adaptive streaming for every small generated clip.

## CDN

CDN layer may cache public or authenticated signed media.

Rules:
- private assets require time-limited access token/signed URL/cookie strategy;
- cache key cannot leak tenant authorization;
- revocation/deletion considers CDN cache invalidation/expiry;
- public published assets can use separate public delivery policy;
- origin remains non-public where possible for private storage.

## Signed downloads

Signed URL/token includes:
- resource/tenant authorization checked before issuance;
- short expiry;
- allowed method;
- optional content disposition/filename;
- optional response headers;
- never grants bucket-wide access.

For high-risk/share-link assets, additional watermark/download restriction policy may apply.

## Storage quotas

Workspace usage categories:
- active source media;
- generated candidates/takes;
- approved masters;
- proxies/derivatives;
- archive;
- temporary.

Entitlement policy declares what counts toward billable/customer-visible quota. Temporary system derivatives can be excluded or separately accounted but still have operational cost tracking.

Before upload/generation:
- estimate/reserve required storage when material;
- prevent obviously impossible upload above hard limit;
- allow grace/recovery according to commercial policy.

## Egress

Track egress/download/streaming where commercially/operationally relevant.

Prevent abuse:
- rate limiting;
- signed expiry;
- share-link limits;
- anti-hotlink/public asset policy where useful.

## Temporary objects

Temporary objects have explicit TTL/owner job:
- provider handoff input;
- FFmpeg intermediate;
- failed multipart session;
- preview generation scratch;
- export archive.

Cleanup is retryable/idempotent and observable.

No unowned temp object should persist indefinitely.

## Provider handoff

When provider accepts upload or signed URL:
- create provider input reference from canonical asset;
- use least lifetime needed;
- avoid public bucket exposure;
- record which asset/version was sent;
- provider output is downloaded/validated into canonical storage, not treated as permanently hosted by provider.

If provider requires public URL, use controlled expiring access where supported and record risk/capability.

## FFmpeg/media sandbox

Media transformations run in isolated workers with:
- input/output job directories;
- CPU/memory/disk/time limits;
- process limits;
- no arbitrary command injection;
- restricted network;
- validated codecs/parameters;
- cleanup on success/failure/cancel.

## Archival

Archive state is explicit and can move binaries to lower-cost storage tier/back-end.

Archive rules:
- metadata stays queryable;
- generation/editing requiring archived source may trigger restore;
- UI shows restore state/cost/time category without inventing exact completion promise;
- delete during archive still propagates;
- archive storage can have separate entitlement/pricing.

## Restore

`ARCHIVED -> RESTORE_REQUESTED -> RESTORING -> ACTIVE | RESTORE_FAILED`

Restore is idempotent and job-based.

## Project/account export

Export builder creates manifest + eligible binaries:
- checks entitlements/rights;
- streams/assembles without duplicating huge data unnecessarily;
- uses temporary export object with expiry;
- produces checksum/manifest;
- excludes raw secrets/provider tokens;
- can segment oversized exports.

## Deletion

Deletion graph includes:
- canonical object;
- derivatives/proxies/thumbnails;
- multipart remnants;
- CDN invalidation/expiry;
- vector/search references;
- exports;
- archived copies;
- provider temporary references where controllable.

Shared/deduplicated physical objects, if introduced, require reference-count/privacy-safe deletion; initial architecture may avoid cross-tenant physical dedupe to simplify isolation.

## Backup boundary

Object-store versioning/backups are operations-layer controls. User deletion immediately removes active access; physical backup/version expiry follows documented privacy/DR lifecycle.

## Data residency

Storage adapter records region. Workspace residency policy must validate all relevant storage/processing providers before claiming residency.

## Observability

Metrics:
- stored bytes by class/tenant;
- upload success/failure/resume;
- validation/quarantine failure;
- proxy/derivative latency;
- CDN hit/egress;
- signed URL issuance/failure;
- orphan temp objects;
- archive/restore success;
- deletion backlog.

## Testing

- interrupted multipart upload resumes;
- duplicate complete request idempotent;
- wrong MIME/magic rejected;
- malicious filename cannot escape key/path;
- oversized upload blocked;
- tenant cannot sign/download another tenant asset;
- proxy lineage valid;
- deletion removes derivatives/indexes;
- temp cleanup after crash;
- archive/restore preserves hashes/metadata;
- provider output validation catches malformed file;
- FFmpeg worker resource ceilings enforced.

## Acceptance criteria

Implementation can determine:
- storage abstraction/object classes;
- small/multipart upload lifecycle;
- quarantine/probe/security checks;
- derivative/proxy/CDN/streaming design;
- signed access;
- quotas/egress/temp cleanup;
- provider handoff;
- archive/restore/export/delete;
- sandbox/observability/testing requirements.
