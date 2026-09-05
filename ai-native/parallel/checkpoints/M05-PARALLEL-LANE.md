# M05 Parallel Lane Checkpoint

## Authority

- Issue: #81 — M05 planning hardening — memory authority and poisoning constraints
- Lane: `M05-PARALLEL-LANE`
- Branch: `agent/m05-content-memory`
- Planning baseline: `main@a7aa25e86bd5092ab9979f26765d48a7b3f34ffc`
- Broadcast state: sequence 13 synchronized
- Consent scope: planning-only-until-new-scope-approved
- Executable M05 authority: **not granted**
- Migration reservation: none
- Product/API/schema/provider/test implementation: not authorized by this checkpoint

## Planning work completed

- Reconciled `docs/milestones/M05/PLAN.md` with the cross-cutting adversarial QA memory/retrieval threat map.
- Made executable M04 completion and explicit M05 executable consent mandatory entry gates; M04 planning completion does not satisfy the dependency.
- Added planning obligations for deterministic memory promotion authority, provenance/source-class/freshness/contradiction/expiry visibility, tenant/project/series isolation, correction/forget behavior, secret exclusion, external-research distrust, provider/model-output distrust and bounded retries/cost.
- Recorded that low-trust observations, hypotheses, retrieved instructions, model output or malicious “admin rules” cannot become canonical policy or approval state without configured deterministic promotion authority.
- Recorded that correction/forget must remove future retrieval authority while preserving required audit/history evidence.
- Created this previously missing M05 planning checkpoint.

## Current evidence classification

- M05 executable surface: `DEFERRED_MODULE` — not authorized yet.
- Executable M04 dependency: not satisfied; only M04 planning hardening is complete.
- M03 live protected-main governance: `EXTERNAL_NOT_VERIFIED` — Issue #36 remains open.
- Cross-cutting QA memory obligations: planning-integrated.
- M05 schema/migrations: not reserved/not implemented.
- Paid/provider/production evidence: not required and not produced by this planning slice.

## Mandatory executable entry recheck

Before any M05 implementation branch or migration reservation is created, the Supervisor must verify all of the following against then-current main:

1. Executable M04 is completed/accepted at its required truth level; a planning checkpoint is insufficient.
2. Explicit M05 executable consent exists; generic conversational continuation is insufficient.
3. Current upstream governance/dependency requirements, including Issue #36 where applicable to the repository's accepted milestone chain, are satisfied at their required truth level rather than assumed from source CI.
4. M05 branch/write ownership is freshly assigned with no collision.
5. Current migration head is audited and any required revision is reserved before schema writes.
6. Broadcast/dependency state is synchronized.
7. The exact proposed research/memory/generation surface is re-evaluated against `docs/qa/ADVERSARIAL-AUDIT-PLAN.md` and receives only targeted missing adversarial evidence.
8. Raw secrets remain outside ordinary memory/embedding/prompt/log payloads.
9. Provider/research/model attempts, fan-out and cost use configured bounds and applicable budget authority.
10. No production credential, paid call or public side effect is introduced unless separately authorized.

## Downstream hold

- M07 cannot treat this planning checkpoint as completed executable M05.
- M08 remains dependent on executable M04/M07 completion.
- Branch synchronization, planning completion or green planning CI does not satisfy executable dependency gates.

## Next authorized action

Submit this planning-only two-file change for ordinary exact-head Repository Governance, Core Domain Contracts and Durable Control Plane CI. If merged, close Issue #81 as planning complete and keep executable M05 on hold until the mandatory entry criteria above are satisfied.

Work Done and Submitted
