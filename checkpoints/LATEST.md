# Latest Checkpoint

Current checkpoint: `checkpoints/2026-08-28-documentation-core-complete.md`

Current milestone: **Milestone 1 — Core domain model and repository migration boundary**

Status: **PLANNING_READY_FOR_CONSENT**

Core product/AI documentation status:
- complete enough for staged implementation;
- tracked in `docs/product/DOCUMENTATION-COMPLETENESS-MATRIX.md`;
- includes project options/wizard, content types, AI roles, prompts, characters, audio, visual/cinematic, image generation + approval + reuse, image-to-video reference handoff, storyboard/timeline, provider routing/recovery, continuity QA, memory, assets, approvals, rights, localization, publishing, analytics, 3-hour long-form architecture, web IA, presets/admin.

Image generation planning is canonical in `docs/product/IMAGE-GENERATION-REUSE-SYSTEM.md` and is exposed as an explicit New Project Wizard strategy. Approved still images may become reusable character/world/style/keyframe/reference assets and may drive first-frame/end-frame/image-to-video workflows while retaining provider-independent lineage and continuity state.

Development consent policy: `ai-native/DEVELOPMENT-CONSENT-GATE.md`

Development brief awaiting operator approval: `docs/architecture/M1-DEVELOPMENT-CONSENT-BRIEF.md`

Detailed execution plan: `docs/architecture/M1-EXECUTION-PLAN.md`

M1 planned work packages:
1. contract freeze + generated schemas;
2. full lineage fixtures;
3. aggregate validation hardening;
4. legacy content importer boundary;
5. PostgreSQL persistence architecture;
6. reversible migration scaffold;
7. persistence repositories + short/long project round trips;
8. Milestone 1 verification.

Next executable action: WP1 only after explicit operator development consent.

A generic `continue`, `next`, or `resume` does not authorize development.

Do not start or modify executable code, schemas, migrations, dependencies, CI behavior, provider integrations, Temporal, generation pipelines, UI, publishing or later milestones without applicable development consent.
