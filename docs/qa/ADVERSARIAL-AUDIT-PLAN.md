# Cross-Cutting Adversarial QA Audit Plan

## Authority and baseline

- Issue: #73
- Lane: `CROSS-CUTTING-QA`
- Branch: `agent/cross-cutting-qa-security`
- Baseline: `main@76b91c15752c0b5840cc5094f74d612a43d4499e`
- Authority: audit/planning only
- Executable test changes: not authorized by this slice
- Product/API/schema/provider changes: not authorized
- Active migration reservation: none
- External M03 governance gate: Issue #36 remains open

This plan converts the repository threat model into a reusable adversarial acceptance map without inventing duplicate tests. Existing M03 focused evidence remains authoritative where it already proves a property; future modules inherit only the missing adversarial obligations relevant to their new attack surface.

## Existing M03 safety evidence to reuse

The M03-WP8 acceptance matrix already maps focused evidence for:

- multipart interruption/restart/resume and lost-ack reconciliation;
- cross-project private-delivery and signer denial;
- malformed/MIME-spoof/threat/quarantine fail-closed behavior;
- lineage and content-hash integrity;
- deletion execution and temporary cleanup;
- archive/restore delivery-state safety;
- private export staging;
- deterministic vector/search cleanup.

QA must not create umbrella tests that merely restate these covered properties. New executable coverage is justified only when a later module adds a genuinely new trust boundary or authority path.

## Threat-model scenario map

| # | Threat-model scenario | Current evidence state | QA decision / future owner |
| --- | --- | --- | --- |
| 1 | Retrieved/web content says to ignore policy and publish | **Deferred** — policy exists, but no authorized public-publish executor is in the current M03 source surface | Add an end-to-end authority test when a publish/social action surface exists. Untrusted evidence must never produce A3 publish authority. |
| 2 | Uploaded content contains fake API-key/tool instructions | **Partial** — media validation/quarantine is covered; semantic instruction-to-tool-config isolation is not yet an executable ingestion path | When tool-aware document/media ingestion exists, prove extracted instructions remain evidence and cannot mutate provider/tool configuration. |
| 3 | Social comment asks for prompt/secret disclosure | **Deferred** — social/community execution is not an accepted current module | Future social/community module must prove comments cannot reveal secrets/system policy, mutate credentials, or autonomously elevate reply authority. |
| 4 | Provider/model output returns another tenant/project asset ID | **Partial** — M03 signed-delivery paths already reject foreign project/asset authority | M08/provider-output ingestion must additionally prove an untrusted provider-returned ID is canonical-lookup + tenant-authorized before use. |
| 5 | Persistent provider 429/500 causes runaway retry/spend | **Partial** — core circuit-breaker persistence exists; provider-specific retry/cost behavior is future surface | M08 must bind retries to ceilings, circuit breaker, idempotency and budget reservation; permanent failure must not cause infinite fallback/spend. |
| 6 | Generated output names an unknown tool/action | **Deferred** — threat-model policy exists, but no accepted generic agent tool registry/executor is in scope | Future agent/tool executor must reject unknown action identifiers before side effects and must not infer a substitute privileged tool. |
| 7 | Memory retrieval contains a malicious “admin rule” | **Deferred to M05** | M05 must preserve memory provenance/class, require promotion for canonical rules, and prove retrieved low-trust memory cannot gain policy authority. |
| 8 | AI proposes a paid fallback over budget | **Deferred to provider/spend surface** | M08/later billing-aware execution must fail closed on budget/authority mismatch and require the configured approval class before privileged spend. |
| 9 | User says generic `continue` | **Policy-covered, product-execution test deferred** — repository threat model explicitly says generic `continue` grants no privileged development/publish/security authorization | Every future privileged executor must use explicit deterministic authority rather than conversational continuation as permission. Repository governance must continue preserving this boundary. |
| 10 | Malicious image/audio/video contains textual/inferred instructions | **Partial** — media parsing/quarantine is covered; semantic authority isolation is a future multimodal-agent path | M06/M08/later multimodal ingestion must prove detected/transcribed instructions remain untrusted evidence and cannot redefine policy/tool authority. |

## Cross-cutting invariants for future milestones

Every later module that introduces an applicable surface must preserve these invariants:

1. **Authority is external to model prose.** Model/provider/retrieval outputs cannot mint roles, approvals, budgets, publish rights or security authority.
2. **Tenant/project IDs are re-authorized canonically.** A returned or remembered resource ID is never trusted because a model/provider supplied it.
3. **Secrets are references, not ordinary prompt data.** Raw provider/OAuth credentials must not become model memory, decision-ledger payloads or public logs.
4. **Low-trust content cannot self-promote.** Web, upload, transcript, social, provider and generated intermediate content remain evidence unless a deterministic promotion path authorizes a stronger class.
5. **Retries and fallbacks are bounded.** Attempts, time, fan-out and cost require ceilings, idempotency and circuit-breaking.
6. **Paid/external/public side effects require matching authority.** Budget, publish, account/security and destructive actions cannot be inferred from generic continuation or a model recommendation.
7. **Provider outputs are untrusted.** IDs, URLs, file metadata, JSON and instructions require schema validation, canonical lookup and policy checks.
8. **Rights/provenance survive reuse.** M04+ entity/reference/voice/media reuse must preserve exact version lineage, ownership/consent state and cross-tenant isolation.
9. **Adversarial evidence is fail-closed.** Parser/scanner/provider/tool ambiguity must never silently upgrade an asset/action into an accepted/privileged state.
10. **No synthetic security success.** Missing real provider/admin/publish evidence remains `NOT_VERIFIED`; source mocks/fakes may prove contracts but not production truth states.

## Module-specific adversarial hooks

### M04 — Character and Entity Library

Planning target only while M03 governance entry criteria remain unresolved:

- cross-tenant entity/version/look/reference access denial;
- hard/project/look/scene lock mutation rejection;
- append/version semantics so new looks cannot silently mutate pinned prior projects;
- rights/consent/provenance required for imported likeness/voice/reference material;
- reference-pack foreign asset IDs rejected by canonical project/tenant authority;
- export/import manifest cannot bypass ownership or rights validation.

### M05 — Content Intelligence and Memory

- malicious memory cannot become `APPROVED_RULE` without promotion authority;
- retrieved observation/hypothesis cannot override system/product policy;
- contradiction/expiry/source-class behavior stays visible;
- forget/correction removes future retrieval authority without corrupting audit history;
- no raw secrets in memory payloads.

### M06 — Hybrid Audio Production

- transcripts/metadata remain untrusted evidence;
- voice-profile rights/version pinning cannot be bypassed by provider output;
- audio parser/probe failures fail closed;
- provider credentials remain out of generated prompt/ledger artifacts;
- paid synthesis retries/fallbacks are bounded when executable scope later exists.

### M07 — Storyboard and Timeline

- generated scene/timeline text cannot create tool/publish authority;
- asset/entity references are canonical and tenant-scoped;
- later edits preserve pinned version/reference lineage;
- malformed generated structures fail schema validation before downstream execution.

### M08 — Provider Router

- provider-returned IDs/URLs are untrusted until canonical validation;
- retry/fallback/circuit breaker and cost reservation are bounded;
- unknown provider/model capability cannot be silently substituted for a privileged operation;
- secret handles are resolved outside ordinary model/provider-visible state;
- provider output cannot grant tenant, budget, publish or security authority;
- deterministic fakes remain sufficient for source acceptance unless real-provider evidence is explicitly required by a later gate.

## Evidence classification

QA findings use only these states:

- `COVERED_CURRENT` — explicit focused current test/evidence proves the property.
- `PARTIAL_CURRENT` — a lower-layer property is covered but the future authority path does not yet exist.
- `DEFERRED_MODULE` — test is invalid to implement before its owning surface exists.
- `GAP_ACTIONABLE` — current accepted surface exists and lacks required evidence.
- `EXTERNAL_NOT_VERIFIED` — requires live admin/provider/publish/production evidence unavailable to source CI.

Do not relabel `DEFERRED_MODULE` or `EXTERNAL_NOT_VERIFIED` as passing merely to make a milestone appear complete.

## Promotion rule

When a future module requests executable promotion, QA must re-run this map against the exact proposed surface and add only the minimum targeted adversarial tests for newly reachable authority paths. All tests must run without production credentials or paid side effects unless an explicit higher-authority release gate requires real external evidence.

## Current audit result

No current M03 source defect is identified by this planning pass. Existing M03 focused tests cover the accepted M03 attack surface listed above. The remaining scenarios are either partially covered lower-layer contracts or correctly deferred to modules that have not yet introduced the relevant authority/tool/provider/memory/social surface.

Issue #36 remains independently `EXTERNAL_NOT_VERIFIED` and is not satisfied by this QA plan.
