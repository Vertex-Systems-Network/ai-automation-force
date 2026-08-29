# M02 Governance Reconciliation — 2026-08-29

## Decision

M02 executable continuation is authorized from the fresh operator instruction:

`Milestone 2 development approve — start.`

Historical WP1-WP5 executable merges remain historical facts. No prior checkpoint or PR is rewritten to claim retroactive consent.

## Technical baseline decision

WP1-WP5 remain the accepted technical baseline because each work package was merged only after its scoped implementation had green CI evidence on the exact PR head. A fresh regression will continue to run as part of subsequent M02 candidate heads, beginning with WP6.

If later regression evidence finds a defect in an already-merged work package, it will be remediated normally; governance reconciliation is not a waiver of technical correctness.

## Manual merge gate while `main` is unprotected

Until repository protection/rulesets enforce equivalent requirements automatically, every executable M02 merge requires:

1. exact candidate head identified;
2. Core Domain Contracts GREEN when applicable;
3. Durable Control Plane GREEN;
4. migration upgrade/downgrade acceptance when schema changes;
5. retained Temporal history replay for workflow changes;
6. no real provider credential/network/spend outside explicitly approved future scope;
7. checkpoint/evidence update after merge.

A mechanically mergeable GitHub PR is not sufficient evidence for merge.

## Delivery semantics

M02 does not claim exactly-once network/workflow delivery. The durable contract is at-least-once execution plus idempotency, immutable evidence, stale/duplicate suppression and transactional persistence boundaries.

## Remaining milestone boundary

WP6 -> WP7 -> WP8 remains the required order. M03 executable development still requires a fresh explicit consent checkpoint after M02 closure.
