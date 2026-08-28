# M01 Development Preflight Audit — 2026-08-29

Status: `M01_APPROVED_IN_PROGRESS`

This audit was performed immediately before and during the start of M01/WP1 after explicit operator approval. It rechecks the planned architecture against current provider/API behavior and the existing repository contracts. It does not authorize M02+ work or provider integration inside M01.

## External research findings

### Google Gemini / generative media

Current Google AI documentation (checked 2026-08-29) states that the Interactions API became the default Gemini interface in June 2026 and `generateContent` is now legacy for new agent/model integrations.

Google also lists older Imagen 4 models as shut down/deprecated in August 2026 in favor of current Gemini image-generation models, and older Veo generations have already moved to newer Veo 3.1 routes.

Implication: provider/model IDs and API method families are volatile registry facts. Later adapters must bind to a verified capability snapshot instead of hard-coding planning-era model IDs.

Evidence:
- https://ai.google.dev/gemini-api/docs
- https://ai.google.dev/gemini-api/docs/deprecations
- https://ai.google.dev/gemini-api/docs/image-generation

### Multi-model gateways

Pika's August 2026 API Club publicly describes one API surface exposing 100+ media/LLM models. Replicate is another API transport that can execute models owned by other vendors.

Implication: `provider` can no longer safely mean both API transport/billing party and underlying model vendor. M01 contracts now distinguish transport provider from model provider so cost, rights, provenance and incident analysis remain unambiguous.

Evidence:
- https://experiment.pika.art/blog/pika-api-club
- https://replicate.com/docs

### Async provider completion and output persistence

Replicate documents that webhook deliveries can be duplicated and, in rare cases, arrive out of order. It also documents that API prediction files may be automatically deleted after a limited retention window unless persisted elsewhere.

Implication for later milestones: callbacks must be idempotent/terminal-state-aware, and provider output URLs are never canonical storage. This confirms the existing durable-workflow and object-storage architecture.

Evidence:
- https://replicate.com/docs/topics/webhooks/
- https://replicate.com/docs/topics/webhooks/receive-webhook/

### PostgreSQL identifiers

PostgreSQL 18 provides native UUIDv7 generation and UUID storage. M01 keeps stable external audit/business IDs separate from future internal DB primary keys. External numeric IDs are widened now to a minimum-six-digit scalable suffix to avoid a later schema-breaking exhaustion limit.

Evidence:
- https://www.postgresql.org/docs/18/release-18.html
- https://www.postgresql.org/docs/18/datatype-uuid.html

### Alembic and legacy content import

Alembic's current cookbook explicitly distinguishes schema migration from general data migration and recommends separate migration scripts for many data-migration cases.

Implication: the legacy `CNT-*` importer remains an explicit idempotent application/maintenance operation in M01/WP4; it will not be hidden inside an Alembic schema migration.

Evidence:
- https://alembic.sqlalchemy.org/en/latest/cookbook.html#data-migrations-general-techniques

## Repository contract defects found before freeze

1. `schema_version` was an ordinary integer default, so incompatible versions could validate.
2. JSON Schema IDs still used the historical `schemas.lullabies.local` namespace.
3. Distribution/import naming still exposed the historical Lullabies product name as the only package identity.
4. CI generated schemas but did not fail on committed-schema drift.
5. strict mypy configuration existed but CI did not execute mypy.
6. machine taxonomy allowed registry values such as `custom`, cast `none/custom`, and `trailer-teaser` that core enums could reject.
7. taxonomy was declared registry-owned while the executable Project/Content contract hard-coded the accepted set.
8. important normalized states such as attempt status, approval decision, commercial-use status and execution mode used unbounded strings.
9. paid cost/free-credit fields allowed negative values.
10. audit/attempt timestamps did not reject reverse chronology or timezone-naive values.
11. exact six-digit external-ID patterns created an avoidable future namespace ceiling.
12. provider provenance could not distinguish a gateway/transport from the underlying model vendor.

## M01/WP1 implementation decisions

- `schema_version` is a literal version contract, not a loose integer.
- stable canonical statuses use typed enums.
- registry-owned audience/cast/content taxonomy fields remain strings structurally so configured future taxonomy additions do not require a core-schema release; built-in enums remain convenience constants.
- external IDs preserve existing six-digit values but permit 6–20 numeric suffix digits.
- persisted/audit timestamps require timezone-aware datetimes and enforce chronology where both endpoints exist.
- monetary/credit quantities are non-negative.
- provider route records distinguish `provider_id` (transport/billing API) from `model_provider_id` (underlying model vendor); direct routes normalize both to the same provider.
- generated JSON Schemas use deterministic `urn:ai-automation-force:schema:v1:*` IDs plus a hash manifest.
- canonical Python distribution/import surface becomes `ai-automation-force-core` / `ai_automation_force_core`; `lullabies_core` remains a temporary compatibility import for repository history.
- CI must run Ruff, mypy, pytest, schema drift verification and compile/import checks on Python 3.12.

## Explicit non-decisions / M01 boundaries

This audit does not select or implement current Gemini, Veo, Pika, Runway, Luma, Hailuo, Kling, Replicate, Stability, BFL or ElevenLabs adapters. Those are later provider milestones and must revalidate current API, pricing, rights and model availability at implementation time.

M01 also does not implement Temporal, FastAPI product endpoints, object storage, FFmpeg production rendering, web/mobile UI, auth, billing, social publishing or public deployment.

## Preflight verdict

`PASS_WITH_WP1_HARDENING`

No architectural blocker prevents M01. The defects above are contract-freeze defects and are being corrected in WP1 before persistence work begins. This reduces later migration, provenance and API/client drift risk without expanding beyond the approved M01 scope.
