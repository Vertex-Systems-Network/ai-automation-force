# Latest Checkpoint

Current checkpoint: `checkpoints/2026-08-28-m1-ready-for-consent.md`

Current milestone: **Milestone 1 — Core domain model and repository migration boundary**

Status: **PLANNING_READY_FOR_CONSENT**

Development consent policy: `ai-native/DEVELOPMENT-CONSENT-GATE.md`

Development brief awaiting operator approval: `docs/architecture/M1-DEVELOPMENT-CONSENT-BRIEF.md`

Detailed execution plan: `docs/architecture/M1-EXECUTION-PLAN.md`

Planning is now refined into ordered work packages:
1. contract freeze + generated schemas;
2. full lineage fixtures;
3. aggregate validation hardening;
4. legacy content importer boundary;
5. PostgreSQL persistence architecture;
6. reversible migration scaffold;
7. persistence repositories + short/long project round trips;
8. Milestone 1 verification.

Next executable action: WP1 only after explicit operator consent.

Do not start or modify executable code, schemas, migrations, dependencies, CI behavior, provider integrations, Temporal, generation pipelines, UI, publishing or later milestones without applicable development consent.
