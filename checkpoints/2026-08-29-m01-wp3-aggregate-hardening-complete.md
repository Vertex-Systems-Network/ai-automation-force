# M01 / WP3 — Aggregate Validation Hardening Complete

Date: 2026-08-29

Status: `M01_DEVELOPMENT_IN_PROGRESS`

Work package: `WP3 — Aggregate validation hardening`

## Result

WP3 is implementation-complete and verified on Python 3.12.

`ProjectBundle` now rejects structurally invalid project graphs deterministically while preserving provider neutrality and long-form/multi-track compatibility.

## Hardened invariants

- `Project.active_timeline_id`, when set, must reference the loaded Timeline;
- TimelineTrack IDs are unique;
- project character/world/prop references cannot contain duplicate IDs;
- hierarchy membership lists cannot hide duplicate references behind set equality;
- Acts/Sequences/Scenes/Shots must resolve to their declared parent hierarchy;
- orphan Shots are rejected explicitly;
- Take IDs and Shot Take membership remain exact and selected Takes must be loaded;
- CharacterVersions must belong to loaded Characters;
- Character version numbers are unique per Character;
- CharacterLook IDs are unique and lock look pins resolve inside the pinned CharacterVersion;
- project and scene CharacterLock targets resolve to the current graph;
- Shot characters must be declared by both the Scene and Project;
- declared/used props resolve and Shot props must be project-declared;
- used Locations resolve, their Worlds resolve, and used Worlds must be project-declared;
- a Shot cannot silently switch away from its Scene's continuous Location;
- canonical primary-video track item IDs must resolve to Shots and remain unique;
- only the explicit `primary-video` track receives strict chronological/non-overlap validation;
- B-roll/overlay-style parallel Shot timing remains allowed because the timeline architecture supports parallel tracks.

## Long-form / performance note

Per-Shot scene lookups use indexed dictionaries instead of repeated linear scans. This avoids introducing an avoidable O(shots × scenes) validation path for long-form projects with potentially thousands of Shots.

## Compatibility fixtures

The test suite explicitly verifies:

- a valid 2-minute project graph remains accepted;
- a valid 90-minute project graph remains accepted;
- primary-video overlap is rejected;
- parallel B-roll overlap is accepted;
- cross-scene primary-video time reversal is rejected;
- invalid character/version/look/lock/world/location/prop ownership cases fail with actionable errors.

## Verification evidence

GitHub Actions workflow: `Core Domain Contracts`

Run: `33217875292`

Job: `99005474118`

Verified successful gates:

- Ruff;
- strict mypy;
- unit tests;
- generated-schema synchronization;
- Python compile/import check.

## Scope boundary preserved

WP3 did **not** implement provider APIs, Temporal workflows, PostgreSQL persistence/migrations, FastAPI/UI, publishing, object storage/FFmpeg runtime, or M02+ behavior.

## Next authorized work

Within the existing M01 consent:

`WP4 — Legacy CNT content importer boundary`
