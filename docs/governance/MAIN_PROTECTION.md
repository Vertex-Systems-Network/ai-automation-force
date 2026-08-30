# Main Protection Governance

Status: **IMPLEMENTATION READY — LIVE READ-BACK REQUIRED**

Linear: `ABD-265`
Repository: `Vertex-Systems-Network/ai-automation-force`
Protected branch target: `main`

## Why this gate exists

`main` was verified unprotected during the Universal Master Prompt adoption audit. Process-only discipline is not sufficient for production-grade promotion: the repository must enforce the integration boundary itself.

A second defect was found during implementation: both canonical workflows previously published the same GitHub check-run context, `validate`. Requiring that ambiguous context cannot prove that both Core Domain Contracts and Durable Control Plane passed.

The governance hardening therefore establishes stable distinct job contexts:

- `core-domain-contracts`
- `durable-control-plane`

Both workflows are configured to run on **every pull request**, so required checks cannot remain permanently `Expected` on documentation/governance-only PRs.

## Target live policy

The idempotent applicator `scripts/apply_main_protection.ps1` configures:

- pull-request-only integration;
- strict/up-to-date required checks;
- required contexts `core-domain-contracts` and `durable-control-plane`;
- administrator enforcement;
- stale-review dismissal;
- required conversation resolution;
- force-push denial;
- branch-deletion denial;
- no repository/user/team push restrictions beyond the PR boundary;
- no undocumented bypass actors.

## Review modes

The applicator requires an explicit review mode; there is no silent default.

### `independent`

Use where another qualified reviewer is available.

- at least one approving review is required;
- stale approvals are dismissed;
- approval after the latest push is required;
- SELF REVIEW cannot be represented as independent approval.

### `solo-self-review`

Use only as an explicit solo-operator exception where an independent reviewer is genuinely unavailable.

- repository-required approving-review count is zero;
- stale-review protection remains configured;
- every implementation/security/data/migration promotion must record `SELF REVIEW` honestly in PR/checkpoint evidence;
- green CI plus SELF REVIEW is not described as independent review;
- this mode does not weaken the required exact-head checks, conversation resolution, PR-only integration, admin enforcement, force-push or deletion controls.

Changing review mode is a governance change and must be deliberate.

## Application

From an authenticated admin workstation with GitHub CLI:

```powershell
pwsh scripts/apply_main_protection.ps1 -ReviewMode independent
```

or, only for the explicit solo exception:

```powershell
pwsh scripts/apply_main_protection.ps1 -ReviewMode solo-self-review
```

The script is intentionally an admin action. It never stores tokens or credentials in the repository.

## Certification / read-back

Documentation intent and a successful API write are not acceptance evidence by themselves. Run:

```powershell
pwsh scripts/verify_main_protection.ps1 -ReviewMode independent
```

or the matching solo mode.

The verifier reads live GitHub protection and fails unless it observes the expected policy, including both distinct required contexts. It also rejects the legacy ambiguous required context `validate`.

`ABD-265` must remain open until live read-back passes and the effective protection is independently re-read through GitHub evidence.

## WP4 interaction

This hardening lane is repository governance only and must remain separate from M03/WP4 implementation PR #33.

WP4 may remain code-complete and CI-green while this gate is unresolved, but it must not be promoted as production-grade governance until live protection is certified or a separately approved governance exception explicitly accepts the residual risk.
