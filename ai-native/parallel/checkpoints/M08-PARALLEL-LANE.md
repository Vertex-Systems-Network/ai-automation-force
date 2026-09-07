# M08 Parallel Lane Checkpoint

- Task: `M08-PARALLEL-LANE`
- Issue: #93
- Agent role: provider planning-contract
- Branch: `agent/m08-video-provider-router`
- Synchronized baseline before planning write: `main@ba97ccbe9ebaa8df3a864ea7a98e2aa3389e4165`
- Broadcast acknowledged: 16
- Authority: planning-only
- Migration reservation: none
- Executable M08 authority: **false**

## Bounded write scope

This slice changes only:

- `docs/milestones/M08/**`
- `ai-native/parallel/checkpoints/M08-PARALLEL-LANE.md`

No product/API/schema/provider adapter/test implementation, migration, credential, paid provider call, media generation, publication, security-setting mutation or production data access is authorized.

## Reconciliation performed

The existing M08 provider-router plan was audited against:

- broadcast-16 / M07 planning promotion constraints;
- `docs/qa/ADVERSARIAL-AUDIT-PLAN.md` provider-router obligations;
- current Supervisor dependency/consent holds;
- M07 canonical reference/version/rights/provenance requirements.

The previous plan already included provider-neutral requests/attempts, quotas, fallback, budgets, rights and ambiguous-completion reconciliation, but it did not state the latest authority/trust boundaries strongly enough and had no M08 checkpoint.

Planning was hardened to require:

1. provider/model returned IDs, URLs, metadata, JSON, moderation labels, OCR/transcripts and instructions remain untrusted until schema validation and canonical lookup/policy checks;
2. every M07/provider-supplied entity/asset/shot/audio/keyframe/reference/version ID is re-authorized for the active workspace/project and pinned to exact lineage;
3. generated/imported text or media cannot mint tool, publish, budget, approval, account or security authority;
4. raw provider/OAuth/signing secrets remain server-side references outside prompts, model memory, generated artifacts, manifests, decision/attempt ledgers and logs;
5. rights, consent, commercial-use eligibility and provenance survive routing, regeneration and cross-provider handoff;
6. retries/fallbacks/fan-out/time/cost remain bounded by idempotency, circuit breaking and budget reservation;
7. ambiguous external completion reconciles before retry/fallback and cannot trigger duplicate paid work;
8. unsupported/unknown/stale capability fails explicitly rather than silently substituting another privileged operation;
9. eligible provider outputs must be validated and canonically ingested before accepted reuse;
10. deterministic fakes prove source contracts only and cannot be relabeled as live provider/admin/production truth.

## Executable entry gates preserved

Future executable M08 remains blocked until the then-current repository proves all applicable gates, including:

- executable M04 acceptance;
- executable M07 acceptance;
- explicit M08 executable consent;
- Issue #36/live protected-main governance where required by the accepted dependency chain;
- collision-free write ownership and migration reservation where required;
- fresh official-source revalidation of provider APIs/auth/scopes/model availability/prices/quotas/moderation/rights/licensing/output-use constraints;
- applicable exact-head QA/security acceptance for the newly reachable provider/router attack surface.

Planning completion, green planning CI, synchronization, mocks/fakes or generic `continue` do not satisfy these gates.

## Data / provider / cost impact

- Schema/migration change: none.
- Provider credential use: none.
- Paid/free provider execution: none.
- Media generated/downloaded/published: none.
- Production data used: none.
- Security/admin setting mutation: none.

## Review target

Supervisor review should verify:

- changed files remain inside the claimed M08 planning surfaces;
- executable dependency/consent/governance gates remain closed;
- no provider-specific hidden state became canonical authority;
- M07 pinned reference/version and rights/provenance constraints survive cross-provider fallback;
- retry/fallback/budget and ambiguous-completion rules fail closed;
- ordinary exact-head repository/source regression CI is green.

## Completion signal

Work Done and Submitted
