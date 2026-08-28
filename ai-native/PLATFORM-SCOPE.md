# Platform Scope and Precedence

## Current scope

The repository started as an AI-native children's content studio. That historical work remains valid and is preserved as the first content-policy profile.

The current product scope is broader:

**A provider-agnostic AI-native media production platform with a kids-first initial niche.**

The platform can support:
- baby/child/family projects governed by child-specific age/safety policy;
- general/adult-audience projects;
- human and non-human casts;
- songs, poems, stories, educational video, episodes, short films, movies, documentaries, compilations and registered future formats;
- projects from 60 seconds up to the configured 10,800-second/3-hour maximum;
- locked reusable characters/entities;
- free and paid providers;
- web/API and future mobile clients.

## Precedence rule

Where older documentation describes the entire product as children-only, interpret that wording as the original/initial profile rather than a restriction on the core platform.

For scope conflicts, use this order:
1. `AGENTS.md`
2. `ai-native/PLATFORM-SCOPE.md`
3. `config/project-taxonomy.yaml`
4. `docs/product/PROJECT-OPTIONS.md`
5. `docs/architecture/DEVELOPMENT-PLAN.md`
6. `ai-native/MASTER-PLAN.md` for foundational modules and principles
7. older kids-specific documents for the child-directed profile

Do not delete the kids-specific age/content/safety rules; apply them whenever a project is child-directed.

## Architecture invariant

Generalizing the platform must not create separate duplicate kids/adult pipelines.

Use one domain/orchestration system with policy profiles and registries.

Examples:
- child project -> child age/safety/content policy attached;
- adult/general project -> general profile attached;
- same Character Library/versioning mechanism;
- same Scene/Shot/Take hierarchy;
- same provider router;
- same rights/provenance/cost/QA infrastructure;
- different policy/creative constraints where required.

## Repository naming

The GitHub repository may remain named `lullabies` while the product architecture grows. Do not perform a repository rename merely to match broader scope unless the operator explicitly decides product/repository naming later.