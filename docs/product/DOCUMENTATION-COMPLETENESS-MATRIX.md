# Documentation Completeness Matrix

Status vocabulary:
- `PLANNED` — requirement is known but not yet fully specified.
- `DOCUMENTED` — architecture/process is described.
- `OPTION_COMPLETE` — user-facing and machine-facing options/decisions are enumerated with defaults/dependencies.
- `DEVELOPMENT_READY` — behavior, states, edge cases, inputs/outputs, QA and acceptance criteria are sufficiently specified to begin implementation after consent.

This matrix is the planning source for determining whether product/AI systems are ready for development. Development consent remains separately required by `ai-native/DEVELOPMENT-CONSENT-GATE.md`.

| Area | Status | Canonical docs | Remaining planning before development |
|---|---|---|---|
| Platform scope | DEVELOPMENT_READY | `ai-native/PLATFORM-SCOPE.md`, `ai-native/MASTER-PLAN.md` | Keep synchronized as scope changes |
| Engineering constitution | DEVELOPMENT_READY | `ai-native/ENGINEERING-CONTRACT.md` | None for current architecture |
| Development consent gate | DEVELOPMENT_READY | `ai-native/DEVELOPMENT-CONSENT-GATE.md` | None |
| Development roadmap | DEVELOPMENT_READY | `docs/architecture/DEVELOPMENT-PLAN.md` | Milestone briefs are created before each development phase |
| Technology stack | DEVELOPMENT_READY | `docs/architecture/TECH-STACK.md` | Revalidate mutable versions at implementation time |
| Core domain model | DEVELOPMENT_READY for M1 | `docs/architecture/DOMAIN-MODEL.md` | Persistence mapping is part of approved M1 scope |
| Project options | OPTION_COMPLETE | `docs/product/PROJECT-OPTIONS.md` | New Project Wizard behavior documented separately |
| New Project Wizard | DEVELOPMENT_READY | `docs/product/NEW-PROJECT-WIZARD.md` | Implementation requires consent |
| Character library/locking | DEVELOPMENT_READY | `docs/product/CHARACTER-LOCK-SYSTEM.md` | Provider-specific reference adapters later |
| Content formats/types | DEVELOPMENT_READY | `docs/product/CONTENT-TYPE-BIBLE.md` | Additional custom types remain registry-extensible |
| AI agent roles | DEVELOPMENT_READY | `docs/product/AI-AGENT-ROLES.md` | Provider/model implementation later |
| Audio production | DEVELOPMENT_READY conceptually | `ai-native/AUDIO-ROUTER.md`, `docs/product/AUDIO-PRODUCTION-BIBLE.md` | Provider-specific API contracts later |
| Visual/cinematic system | DEVELOPMENT_READY conceptually | `docs/product/VISUAL-CINEMATIC-BIBLE.md` | Provider implementation later |
| Storyboard/shot planning | DEVELOPMENT_READY conceptually | `docs/product/STORYBOARD-SHOT-SPEC.md` | Timeline engine integration later |
| Timeline/sequence/rhythm | DEVELOPMENT_READY conceptually | `docs/product/TIMELINE-SEQUENCE-ENGINE.md` | OTIO/runtime integration later |
| Video continuity | DOCUMENTED | `ai-native/VIDEO-CONTINUITY.md` | Dedicated continuity QA spec still required |
| Provider abstraction/router | DOCUMENTED | `ai-native/FREE-TIER-ROUTER.md`, `ai-native/MASTER-PLAN.md` | Dedicated provider contract & retry/fallback spec required |
| Free/paid cost policy | DOCUMENTED | `config/execution-policy.yaml`, `ai-native/FREE-TIER-ROUTER.md` | UI/budget approval UX still required |
| Memory/originality | DOCUMENTED | `ai-native/MEMORY-BANK.md` | Generalized media-memory and analytics feedback spec still required |
| Asset/media library | PLANNED | `ai-native/MASTER-PLAN.md`, `docs/architecture/TECH-STACK.md` | Dedicated asset/media-management spec required |
| Review/approval | PLANNED | `ai-native/MASTER-PLAN.md`, consent docs | Dedicated review/approval workflow spec required |
| Localization/dubbing | PLANNED | `ai-native/MASTER-PLAN.md` | Dedicated localization spec required |
| Publishing | PLANNED | `ai-native/MASTER-PLAN.md` | Dedicated publishing spec required |
| Analytics/learning | PLANNED | `ai-native/MASTER-PLAN.md` | Dedicated learning-loop spec required |
| Rights/consent/provenance | DOCUMENTED | `ai-native/ENGINEERING-CONTRACT.md`, `ai-native/MASTER-PLAN.md` | Dedicated rights/provenance operations spec required |
| 3-hour long-form production | DOCUMENTED | `docs/product/TIMELINE-SEQUENCE-ENGINE.md`, `docs/architecture/DEVELOPMENT-PLAN.md` | Dedicated long-form context/recovery/render strategy required |
| Project templates/presets | PLANNED | `docs/product/PROJECT-OPTIONS.md` | Dedicated preset/template catalogue required |
| Web UI/UX IA | PLANNED | `docs/architecture/TECH-STACK.md` | Dedicated application IA + screen behavior spec required |
| Admin/settings | PLANNED | master plan/tech stack | Dedicated settings/admin spec required |
| Daily provider scout | DOCUMENTED | `docs/operations/DAILY-PROVIDER-SCOUT.md` | Runtime verification still required; executable changes need consent |

## Documentation-completion rule

A system should not be treated as `DEVELOPMENT_READY` merely because its name appears in the master plan. It reaches `DEVELOPMENT_READY` only when the implementation team can determine without hidden chat context:
- purpose and ownership;
- user/operator inputs;
- AI-autonomous decisions;
- defaults and overrides;
- state transitions;
- data/asset inputs and outputs;
- validation and QA gates;
- failure/retry behavior;
- rights/cost/security constraints;
- persistence/history requirements;
- acceptance criteria;
- explicit out-of-scope behavior.

## Current documentation lane

Before additional executable development beyond already planned M1 stabilization, finish the remaining `PLANNED` and high-impact `DOCUMENTED` systems in priority order:
1. provider contract + retry/recovery;
2. continuity QA;
3. asset/media library;
4. review/approval;
5. rights/provenance;
6. localization;
7. publishing;
8. analytics/learning;
9. long-form hardening;
10. web IA/admin/presets.
