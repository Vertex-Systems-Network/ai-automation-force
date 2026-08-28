# Technical Stack and Language Decision

## Decision summary

Do not force the entire product into one programming language.

Use two primary languages:

- **Python 3.12+** for the AI/media backend, orchestration, provider adapters, research, QA and automation.
- **TypeScript** for the web UI and future mobile application.

This split follows the strengths of the ecosystems while keeping the public API contract language-neutral.

## Backend/API — Python + FastAPI

Use Python for:
- AI provider SDKs/adapters
- research/scouting
- content intelligence
- semantic/vector operations
- audio/media analysis
- FFmpeg orchestration
- QA pipelines
- durable workflow activities
- provider/cost routing
- automation scripts

Use FastAPI as the HTTP API/control plane because it is OpenAPI/JSON-Schema based and supports generated clients and interactive API documentation.

FastAPI must not be treated as the durable job engine for multi-hour/day workflows.

## Durable workflow orchestration — Temporal

Use Temporal for production workflows that can:
- take minutes/hours/days;
- wait for provider jobs;
- wait for free quota reset;
- retry after network/provider failure;
- pause for a manual-free handoff;
- pause for budget/human approval;
- resume after worker/process/server restart;
- fan out scene/shot jobs and join them safely.

Core examples:
- `ContentProductionWorkflow`
- `AudioProductionWorkflow`
- `VideoProjectWorkflow`
- `SceneWorkflow`
- `ShotGenerationWorkflow`
- `PublishWorkflow`
- `ProviderScoutWorkflow` where appropriate outside GitHub Actions

Use Temporal activities for external side effects. Keep workflow code deterministic according to Temporal SDK rules.

## Operational database — PostgreSQL

Use PostgreSQL as the application runtime database once the API/UI product begins.

Store:
- projects
- users/workspaces later
- characters/entities
- content versions
- jobs/workflow references
- scenes/shots/takes
- provider registry snapshots
- cost/quota ledger
- assets/provenance
- QA results
- publishing records
- analytics
- approvals

Use `pgvector` for semantic similarity/originality memory and reference retrieval when needed, rather than adding a separate vector database at the beginning.

### Repository vs database source of truth

Current architecture is repository-first while the product is documentation/agent driven.

When the application runtime is introduced:
- Git remains canonical for engineering policy, schemas, prompts, ADRs, research evidence, provider-source definitions and exported/auditable manifests;
- PostgreSQL becomes canonical operational state for live projects/jobs/users/assets;
- important production snapshots/manifests can be exported to Git/object storage for audit and recovery.

Do not make normal UI operations commit directly to Git as the primary runtime database.

This transition must be implemented through a documented migration rather than silently changing the current repository-first contract.

## Semantic memory — PostgreSQL + pgvector

Use embeddings for:
- content duplicate checks
- concept similarity
- character/reference retrieval
- research retrieval
- prior failure retrieval
- analytics hypothesis lookup

Embeddings are one signal, not the sole originality decision.

## Media/object storage

Large media must not live in ordinary Git history.

Use an S3-compatible object-storage abstraction for:
- audio stems/masters
- images/keyframes/references
- video takes/shots
- final masters
- thumbnails
- subtitle files
- temporary provider inputs/outputs

Development may use local filesystem or a local S3-compatible service. Production adapters can target the selected cloud object store without changing business logic.

Every stored object gets:
- stable asset ID
- content hash
- size/MIME
- storage URI
- source/provider
- project/content lineage
- rights/license state
- created timestamp
- retention class

## Timeline/edit model — OpenTimelineIO + project extensions

Adopt OpenTimelineIO (OTIO) as the editorial interchange foundation where practical.

OTIO represents editorial timing such as:
- timelines
- tracks
- clips
- transitions
- markers
- metadata

and references media externally rather than embedding the media.

The project should keep its richer AI-specific data model for:
- character states
- continuity states
- provider generations
- prompt versions
- QA
- cost
- keyframe references

and map approved editorial state to/from OTIO for editor interoperability and robust timeline handling.

Do not force every AI-specific field into the core OTIO schema; use namespaced metadata or separate linked manifests.

## Media processing — FFmpeg

FFmpeg is the deterministic render/processing engine for:
- concat/trim
- audio mixing/ducking
- loudness normalization
- format conversion
- overlays
- subtitles
- transitions/filtergraphs
- thumbnails/poster frames
- proxies
- final encodes

Generative AI should not be used for tasks FFmpeg can perform deterministically and reproducibly.

## Web frontend — TypeScript + React + Next.js App Router

Use TypeScript for the web product.

Recommended:
- Next.js App Router
- React
- generated typed API client from FastAPI OpenAPI
- server-state/query library only when justified
- WebSocket/SSE progress channels for long-running jobs

Primary UI areas:
- dashboard/projects
- project wizard
- character/entity library
- storyboard
- timeline/editor
- shot inspector
- provider/take comparison
- audio mixer controls
- cost/quota dashboard
- QA/continuity review
- publishing
- analytics
- provider/research admin

The web frontend never contains provider secrets.

## Mobile app — TypeScript + React Native + Expo

Future mobile app uses React Native + Expo with TypeScript.

The mobile client consumes the same versioned HTTP/OpenAPI APIs as the web client.

Initial mobile scope should focus on:
- project/status monitoring
- approvals
- reviewing characters/keyframes/takes
- changing safe project options
- provider/cost alerts
- publication approval

Do not attempt to duplicate a professional desktop timeline editor on mobile in the first release.

## Shared contracts

The backend owns API schemas through OpenAPI.

Generate TypeScript API types/client for web/mobile so request/response contracts do not drift.

Version public APIs when breaking changes are unavoidable.

## Monorepo target

```text
/
  apps/
    api/                 # FastAPI application
    worker/              # Temporal workers / media workers
    web/                 # Next.js TypeScript
    mobile/              # Expo/React Native later
  packages/
    python-core/         # domain models/services shared by API/workers
    contracts/           # generated API artifacts/schema exports
    web-ui/              # reusable web UI where justified
  automation/            # provider scout and repo automation
  infra/                 # containers/deployment/IaC later
  config/
  schemas/
  prompts/
  docs/
  research/
  tests/
```

Exact package boundaries may evolve during implementation; dependency direction must remain explicit.

## API style

Primary external API: REST/JSON with OpenAPI.

Add:
- idempotency keys for mutating generation operations
- cursor pagination
- request IDs
- structured errors
- API versioning
- OAuth/session/auth later according to deployment needs
- signed asset upload/download URLs instead of proxying huge media through ordinary JSON endpoints
- webhooks/event endpoints where providers require them
- SSE/WebSocket job updates for UI

Avoid GraphQL initially. Add it only if real product needs justify its operational complexity.

## Worker types

Separate queues/task classes by resource behavior:
- light orchestration/research
- provider network calls
- CPU media analysis
- FFmpeg rendering
- GPU/local-model tasks if later enabled

Do not allow one long FFmpeg render to starve lightweight API/provider jobs.

## Development/testing stack

Python:
- pytest
- Ruff
- mypy or equivalent strict type checking where practical
- JSON Schema/OpenAPI validation

TypeScript:
- TypeScript strict mode
- ESLint
- Vitest/Jest as selected during scaffold
- Playwright for web E2E

System:
- contract tests for every provider adapter
- fixture/fake providers to test without spending credits
- FFmpeg integration tests on small fixtures
- workflow replay/idempotency tests
- database migration tests

## Why not TypeScript-only backend?

A TypeScript-only stack can work, but this product is unusually heavy in AI/provider integration, media processing, scientific/semantic tooling and automation. Python reduces friction in those areas. Forcing the backend into TypeScript mainly for language uniformity would not outweigh the ecosystem advantage.

## Why not Python UI?

Python UI frameworks are not the best foundation for the intended rich storyboard/timeline web app plus future mobile client. TypeScript/React provides a more suitable long-term interaction ecosystem.

## Performance language later

Do not add Rust/C++ at the start. FFmpeg already handles heavy media primitives. Add a native/high-performance component only after profiling proves a Python/FFmpeg boundary is a material bottleneck.

## Final recommendation

**Backend/orchestration/AI/media: Python.**

**Web frontend: TypeScript + Next.js/React.**

**Mobile: TypeScript + React Native/Expo.**

**Database: PostgreSQL + pgvector.**

**Durable workflows: Temporal.**

**Editorial interchange: OpenTimelineIO.**

**Media processing: FFmpeg.**

**Large assets: S3-compatible object storage.**