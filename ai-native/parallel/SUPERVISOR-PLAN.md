# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03-WP8 Review | `supervisor-agent` | `supervisor/m03-wp8-review` | active review/promotion authority only |
| M03-WP8 Acceptance | `acceptance-agent` | `agent/m03-wp8-acceptance-v2` | active source acceptance |
| M04 Character | `character-agent` | `agent/m04-character-library` | sync-required planning-only |
| M05 Content | `content-agent` | `agent/m05-content-memory` | sync-required planning-only |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | sync-required planning-only |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | sync-required planning-only |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | sync-required planning-only |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | sync-required audit/planning |

The earlier `agent/m03-wp8-acceptance` branch is retired for executable work after a partial pre-reconciliation slot edit. It is not promotion authority and will not be force-reset. `agent/m03-wp8-acceptance-v2` is the clean current-main acceptance branch.

## M03 transition state

PR #65 closed WP7 at `main@38b182f4ea886b48c4249aacf362fb58546bd3f5`. Broadcast 10 records that merge and unblocks bounded WP8 source acceptance. Migrations `20260901_0015` and `20260901_0016` remain landed; there is no active M03 migration reservation.

WP8 may create only the canonical acceptance matrix/checkpoint and genuinely missing acceptance tests if the evidence audit proves a gap. Existing focused evidence already covers multipart restart/resume and lost-ack recovery, cross-project delivery denial and signer mismatch, malicious/MIME-spoof quarantine rejection, provenance/hash integrity, archive/restore, deletion propagation, temporary cleanup, export staging, and vector/index cleanup hooks.

No product/API/schema/provider expansion, external provider credential, production bucket, or cost-bearing action is authorized by WP8.

## External governance boundary

Issue #36 remains open because live GitHub repository ruleset read-back does not prove protected `main`. WP8 source acceptance may be merged when its exact-head source checks are green, but that merge must not claim final M03 protected-main governance completion while Issue #36 is unresolved.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. The acceptance agent owns only:

- `docs/milestones/M03/WP8-ACCEPTANCE-MATRIX.md`
- `ai-native/parallel/checkpoints/M03-WP8.md`

The Supervisor review lane owns only `ai-native/parallel/checkpoints/M03-WP8-REVIEW.md`. Other lanes remain disjoint and sync-required by broadcast 10.

## Merge order

1. `supervisor/m03-wp8-review` coordination reconciliation
2. fast-forward `agent/m03-wp8-acceptance-v2` to the resulting current main
3. `agent/m03-wp8-acceptance-v2` source acceptance submission
4. Supervisor exact-head review and merge when all required source checks are green
5. final M03 governance close only after Issue #36 live protection evidence is satisfied

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
