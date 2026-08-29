# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m03-wp2-complete.md`

Current phase: **M03 — Asset Storage and Provenance**

Status: **M03_WP2_COMPLETE_WP3_ACTIVE**

## Completed baseline

- M01 complete: `424b76214ab8eb94d3205a2eba2d75cf4ffa0cc7`
- M02 complete/closure checkpoint merge: `acf8d30f04124290cab97eab702c2cca6b9e3dcb`
- M02 final executable WP8 merge: `bb82c3bd115723504cf233e0cab93ca9513d10a8`
- M03 WP1 accepted merge: `b2cdad89f514ca905c66c71f44835ca8fbac9a51`
- M03 WP2 accepted merge: `ff7005b127f0c83df481ae04b85fd763d207a67f`

## M03 development consent

Fresh explicit operator authorization received on 2026-08-29:

`Milestone 3 development approve — start.`

M03 consent checkpoint:
`checkpoints/2026-08-29-m03-development-approved.md`

Current stack revalidation:
`docs/architecture/M03-CURRENT-STACK-REVALIDATION-2026-08-29.md`

WP1 completion checkpoint:
`checkpoints/2026-08-29-m03-wp1-complete.md`

WP2 completion checkpoint:
`checkpoints/2026-08-29-m03-wp2-complete.md`

## M03 WP2 verified acceptance

Accepted executable head:
`6c63ca083ac48b0b1127610f66fb0bce60223f22`

Accepted replacement PR:
`#30`

Canonical merge:
`ff7005b127f0c83df481ae04b85fd763d207a67f`

Fresh exact-head CI:
- Core Domain Contracts #166 — run `33266539978` / job `99137479531` — GREEN
- Durable Control Plane #104 — run `33266539983` / job `99137479679` — GREEN

WP2 now provides stable `UPS-*` upload sessions, canonical quarantine upload keys, exact size/MIME/object binding, direct S3 upload grants, resumable multipart state, durable backend `UploadId` binding/recovery, semantic part replay, complete/abort/expiry idempotency, destructive-overwrite protection, lost-completion acknowledgement reconciliation, reversible migration `20260829_0009`, PostgreSQL acceptance coverage and synchronized generated schema.

Upload completion remains transfer completion only; quarantine/media-security acceptance and canonical Asset promotion are not part of WP2.

## Current executable target

**M03-WP3 — Quarantine, media probe and upload security** / Linear `ABD-202`

Required WP3 scope:

- quarantine lifecycle after upload transfer completion;
- claimed MIME versus actual file magic/type verification;
- exact size/type policy and fail-closed rejection;
- resource-limited media probe hook for media metadata/structural validation;
- malware/threat scanning hook and provider-neutral scan outcome contract;
- explicit accepted/rejected security lifecycle;
- malformed/malicious fixtures fail closed;
- rejected objects never become routable canonical assets;
- parser/FFmpeg/probe execution occurs outside deterministic workflow code;
- external process invocation is bounded and non-shell-injectable;
- deterministic fixtures/no real provider spend for acceptance;
- exact-head Core + Durable regression gates before merge.

WP3 does not implement Asset↔StorageObject provenance/rights linkage (WP4), derivatives (WP5), signed media delivery (WP6), lifecycle orchestration (WP7), or M04+.

## Linear M03 execution chain

- WP1 `ABD-200` — Done
- WP2 `ABD-201` — Done
- WP3 `ABD-202` — next active target
- WP4 `ABD-203` — blocked by WP3
- WP5 `ABD-204` — blocked by WP4
- WP6 `ABD-205` — blocked by WP5
- WP7 `ABD-206` — blocked by WP6
- WP8 `ABD-207` — blocked by WP7

## Consent boundary

M03 authorization does not authorize M04+ executable work. Generic continuation commands may continue already-authorized M03 work but cannot expand beyond M03 or authorize M04.

GitHub remains canonical for engineering contracts, implementation evidence and checkpoints. Linear mirrors verified execution state.
