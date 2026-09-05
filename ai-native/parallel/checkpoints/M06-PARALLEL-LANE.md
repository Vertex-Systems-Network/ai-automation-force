# M06 Parallel Lane Checkpoint

## Authority

- Issue: #85 — M06 planning hardening — voice rights and provider trust constraints
- Lane: `M06-PARALLEL-LANE`
- Branch: `agent/m06-audio-production`
- Planning baseline: `main@496cff2fe7aa4dbf5777b4a5b4cb5616a29ae432`
- Broadcast state: sequence 14 synchronized
- Consent scope: planning-only-until-new-scope-approved
- Executable M06 authority: **not granted**
- Migration reservation: none
- Product/API/schema/provider/test implementation: not authorized by this checkpoint

## Planning work completed

- Reconciled `docs/milestones/M06/PLAN.md` with the cross-cutting adversarial QA audio threat map.
- Made executable dependency acceptance, explicit M06 executable consent and fresh governance/write/migration/provider revalidation mandatory entry gates.
- Added voice/likeness consent and immutable VoiceProfile version-pinning requirements.
- Recorded that provider IDs, URLs, transcripts, status, licensing claims and other returned metadata are untrusted until canonical validation.
- Added tenant/project/provider-asset isolation requirements for voices, music, SFX, stems and imported/generated audio.
- Required malformed audio and parser/probe/transcode failures to fail closed.
- Kept raw provider/OAuth/signing credentials outside prompts, generated artifacts, manifests, ledgers and logs.
- Added rights/consent/provenance continuity through generation and deterministic mixing.
- Added bounded retries/fallback/fan-out/spend with idempotent attempt semantics to prevent duplicate billing.
- Created this previously missing M06 planning checkpoint.

## Current evidence classification

- M06 executable surface: `DEFERRED_MODULE` — not authorized yet.
- Upstream executable dependency chain: not satisfied by planning promotions.
- Explicit M06 executable consent: absent.
- M03 live protected-main governance: `EXTERNAL_NOT_VERIFIED` — Issue #36 remains open.
- Cross-cutting QA audio obligations: planning-integrated.
- M06 schema/migrations: not reserved/not implemented.
- Paid/provider/production evidence: not required and not produced by this planning slice.

## Mandatory executable entry recheck

Before any M06 implementation branch or migration reservation is created, the Supervisor must verify all of the following against then-current main:

1. M01–M05 are accepted at the executable truth levels required by the milestone chain; planning checkpoints are insufficient.
2. Explicit M06 executable consent exists; generic conversational continuation is insufficient.
3. Current upstream governance requirements, including Issue #36 where applicable to the accepted chain, are satisfied at their required truth level rather than assumed from source CI.
4. M06 branch/write ownership is freshly assigned with no collision.
5. Current migration head is audited and any required revision is reserved before schema writes.
6. Broadcast/dependency state is synchronized.
7. Current audio/TTS/music provider APIs, licensing and commercial-use constraints are revalidated.
8. Voice/likeness consent and pinned voice-profile version authority are canonical and provider output cannot bypass them.
9. Provider IDs/URLs/transcripts/licensing claims remain untrusted until schema/canonical validation.
10. Raw secrets remain outside ordinary audio records, prompts, generated metadata, manifests, logs and ledgers.
11. Audio parser/probe/transcode failure semantics remain fail closed.
12. Provider attempts/fallbacks/fan-out/cost use configured ceilings, idempotency and applicable budget authority.
13. No production credential, paid call or public side effect is introduced unless separately authorized.

## Downstream hold

- M07 cannot treat this planning checkpoint as completed executable M06.
- Planning synchronization, green CI, deterministic fakes or a completed checkpoint do not satisfy executable dependency gates.

## Next authorized action

Submit this planning-only two-file change for ordinary exact-head Repository Governance, Core Domain Contracts and Durable Control Plane CI. If merged, close Issue #85 as planning complete and keep executable M06 on hold until the mandatory entry criteria above are satisfied.

Work Done and Submitted
