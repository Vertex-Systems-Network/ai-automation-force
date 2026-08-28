# Legacy Content Import Boundary

Status: M01/WP4 implementation contract  
Mapping version: `legacy-content-v1-to-core-v1`

## Purpose

Migrate the repository's legacy `schemas/content-package.schema.json` v1 metadata shape into the generalized M01 `Content` / `ContentVersion` domain without mutating legacy source files, inventing canonical identities, or performing persistence inside the mapper.

The importer is a pure compatibility boundary. PostgreSQL persistence begins in later M01 work packages.

## Inputs

The importer receives two explicit inputs:

1. parsed legacy metadata payload;
2. the exact resolved content/performance text referenced by legacy `paths.content`.

It does **not** read `paths.*` itself. Callers resolve files and pass bytes/text explicitly so path traversal, hidden I/O, repository assumptions, and persistence side effects do not enter the domain mapping function.

## Source validation

`LegacyContentPackageV1` mirrors legacy top-level schema v1 and rejects unknown top-level fields.

Legacy nested objects intentionally permit additional properties because the historical JSON Schema did not set `additionalProperties: false` on those nested objects.

Mapping rejects safely when:

- required legacy fields are absent or malformed;
- `content_id` is not `CNT-######`;
- exact content text is empty;
- `approved_at` precedes `created_at`;
- duration cannot satisfy the canonical 60..10800 second boundary;
- metadata cannot be deterministically serialized as canonical JSON.

No duration is guessed or clamped. Legacy schema allowed durations from one second, while current canonical contracts require at least 60 seconds; incompatible legacy input must therefore be repaired or intentionally migrated by a future operator-controlled policy rather than silently rewritten.

## Stable identity mapping

Legacy identity is preserved:

- `CNT-000321` -> `Content.content_id = CNT-000321`;
- first imported canonical version -> `CTV-000321`;
- `Content.active_version_id = CTV-000321`;
- imported canonical version number = `1`.

A changed source package using the same legacy `CNT-*` identity does **not** automatically overwrite `CTV-*`. Reconciliation reports a conflict so a future versioning/migration decision is explicit.

## Field mapping

| Legacy | Canonical | Rule |
| --- | --- | --- |
| `content_id` | `Content.content_id` | preserved |
| `status` | `Content.status` | preserved source state |
| `paths.package` | `Content.source_legacy_package_path` | preserved provenance path |
| `title` | `ContentVersion.title` | preserved |
| `content_type` | `ContentVersion.content_format` | identity-preserved except safe lullaby mode refinement |
| `language` | `ContentVersion.language` | preserved |
| `target_duration_seconds` | same | must already satisfy canonical range |
| `objective.*` | `ContentVersion.objective.*` | preserved |
| `creative.premise` | `ContentVersion.premise` | preserved |
| `creative.hook` | `ContentVersion.hook` | preserved |
| resolved `paths.content` text | `script_or_lyrics` | exact text, no rewrite |
| `creative.tags + creative.topics` | `tags` | stable de-duplicated union |
| `fingerprints.exact_text` | `originality_fingerprint` | preserved when present; otherwise SHA-256 of exact content text |
| `created_at` | audit created time | preserved |
| `approved_at` | audit updated time | used when present; otherwise `created_at` |

### Lullaby refinement

The current Content Type Bible explicitly distinguishes spoken and sung lullabies. Therefore:

- legacy `lullaby + speech` -> `spoken-lullaby`;
- legacy `lullaby + music` -> `sung-lullaby`;
- legacy `lullaby + chant` -> `sung-lullaby`.

No provider-specific behavior is inferred from this refinement.

## Deliberately unmapped legacy fields

Legacy `creative.characters` contains free-text names, not canonical `CHR-*` identities. The importer records them in `unmapped_character_names` and never fabricates Character IDs.

Legacy `creative.setting` is free text. It is recorded as `unmapped_setting`; the importer never fabricates World/Location IDs.

Legacy age-band and detailed audio routing metadata remain source metadata/warnings because project/audience and audio production migration are outside WP4.

## Fingerprint and import key

The importer computes SHA-256 over:

`deterministically serialized metadata + exact content text`

and produces:

`legacy-content-v1-to-core-v1:<CNT-ID>:<sha256>`

The source payload is not mutated while computing this value.

## Reconciliation contract

`reconcile_legacy_content_import(...)` is pure and performs no database write.

It returns one of:

- `create`: neither canonical Content nor ContentVersion exists;
- `noop`: exact deterministic canonical records already exist;
- `conflict`: partial state, identity mismatch, changed import key/source, or canonical record drift exists.

A conflict is intentionally fail-closed. The importer never overwrites existing canonical data automatically.

WP5/WP6/WP7 persistence code may consume this decision inside a database transaction, but must preserve the same semantics.

## Idempotency

Repeating the same metadata and exact content text yields the same:

- `CNT-*` identity;
- `CTV-*` identity;
- canonical Content and ContentVersion values;
- source SHA-256;
- import key;
- reconciliation result (`noop`) once those exact records are persisted.

This is the M01 idempotency boundary; it does not imply that the pure mapper itself stores anything.

## Current repository evidence

At implementation time `memory/content-index.json` contains no legacy catalogue items. Therefore WP4 does not claim a real production catalogue migration has already run.

Acceptance uses a schema-faithful representative fixture. When actual legacy packages become available, the same deterministic importer/reconciliation contract is used and each result must be recorded as migration evidence.

## Non-goals / scope boundary

WP4 does not:

- mutate or delete legacy files;
- traverse repository paths;
- write PostgreSQL;
- create Characters/Worlds/Locations from free text;
- call AI/media providers;
- run Temporal workflows;
- publish content;
- migrate audience policy, audio production state, or generation history;
- authorize M02+ behavior.
