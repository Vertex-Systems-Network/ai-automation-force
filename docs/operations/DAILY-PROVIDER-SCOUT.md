# Daily Provider Scout and Safe Self-Update

## Goal

Once per day, research current AI provider/API capabilities and newly relevant providers, compare them with the repository registry, preserve evidence, create a pull request when a material change exists, and merge only the low-risk change classes allowed by policy.

## Workflow

File: `.github/workflows/provider-scout.yml`

Schedule:
- every day at 03:17 Asia/Karachi;
- manual `workflow_dispatch` is also supported.

High-level flow:

`validate -> AI research with web grounding -> compare registry -> classify changes -> write evidence -> validate -> branch -> PR -> conditionally merge safe Class A/B`

## Required secret

Create repository or organization secret:

`GEMINI_API_KEY`

The scout defaults to a configurable Gemini Flash-Lite model and uses Google Search + URL Context to research current official sources.

The exact model/free quota is a provider fact and is itself subject to the provider registry/update process.

## Optional variables

`PROVIDER_SCOUT_MODEL`
- default in workflow: `gemini-2.5-flash-lite`
- allows model changes without editing workflow code.

`PROVIDER_SCOUT_RUNNER`
- default: `ubuntu-latest`
- set to an appropriate self-hosted label when a persistent self-hosted runner should be used.

## Optional authentication token

`PROVIDER_SCOUT_APP_TOKEN`

Recommended when the organization wants pull requests created by the scout to trigger normal downstream CI without the special workflow-created-PR approval behavior of the repository `GITHUB_TOKEN`.

Prefer a narrowly scoped GitHub App installation token over a broad personal token for production automation.

If the optional token is absent, the workflow uses `github.token`/`GITHUB_TOKEN`.

## GitHub repository setting

For `GITHUB_TOKEN` to create pull requests, repository/organization Actions settings must permit GitHub Actions to create/approve pull requests as appropriate.

Path in GitHub UI:
`Settings -> Actions -> General -> Workflow permissions`

If policy prevents creation/merge, the scout must fail/leave the PR open rather than bypass repository rules.

## Private-repository runner cost

This repository is private.

GitHub-hosted standard runners consume the account/organization's included private-repository Actions minutes. A short daily scout should normally be small relative to the included allowance, but it is not conceptually unlimited.

A self-hosted runner does not consume GitHub-hosted Actions minutes. Infrastructure/electricity/network costs remain the operator's responsibility.

## Change classes

### Class A — research/evidence
Examples:
- dated research report;
- official-source evidence;
- non-behavioral scout state.

Can auto-merge after validation.

### Class B — high-confidence provider facts
Examples:
- provider's current model ID;
- free API true/false;
- documented clip length;
- reference/keyframe capability;
- documented watermark/commercial-use fact.

Can auto-merge only when all requirements in `config/update-policy.yaml` pass.

### Class C — architecture/integration recommendation
Examples:
- new provider discovered;
- new adapter recommended;
- new production technique;
- architecture improvement.

Create PR/research proposal but do not auto-merge the architectural change.

### Class D — executable/risky changes
Examples:
- workflow/code;
- schemas/migrations;
- auth/security;
- budget behavior;
- publishing behavior;
- destructive behavior.

Never blindly self-merge from discovery. Require ordinary CI and review policy.

## Why new providers are not auto-enabled

Discovering a new AI API is not enough to safely route production to it.

Before production enablement require:
- official API verification;
- terms/license review;
- pricing/quota verification;
- provider adapter;
- mock/contract tests;
- failure normalization;
- cost accounting;
- provenance handling;
- QA capability validation;
- privacy/security review.

New providers therefore begin as discovery/evaluation records.

## Scout files

- `automation/provider_scout.py` — research/compare/apply engine
- `automation/requirements-scout.txt` — minimal dependency set
- `config/provider-sources.json` — official source registry + discovery queries
- `config/update-policy.yaml` — self-update governance
- `config/provider-registry.yaml` — current machine-readable provider facts
- `research/provider-updates/YYYY-MM-DD.{md,json}` — evidence/report
- `memory/provider-source-state.json` — last successful scout checkpoint once a material update is recorded

## Merge behavior

For a safe Class A/B result, the workflow opens a PR and attempts a normal squash merge.

It does **not** use an admin bypass.

If required reviews/checks/permissions block merge, the merge command is allowed to fail and the PR stays open.

The repository currently does not need GitHub's separate `auto_merge` feature for this direct post-validation merge attempt. If a future ruleset requires checks to complete asynchronously, prefer a GitHub App token and configured auto-merge/merge-queue policy rather than weakening rules.

## No-change behavior

If the scout reports no material change, it does not create a noise PR.

## Failure behavior

Examples:
- missing Gemini key -> workflow fails visibly;
- API/search outage -> no registry mutation;
- malformed model JSON -> fail;
- invalid registry YAML -> fail before PR;
- low-confidence change -> review-required PR or no automatic registry patch;
- merge blocked -> PR remains open;
- provider evidence conflict -> do not guess.

## Security

- Secrets are passed only through Actions secrets/environment.
- The API key is sent in an HTTP header, not committed or placed in report files.
- Generated AI output is untrusted; only an allowlist of registry fields may be patched.
- A model cannot edit arbitrary repository paths through the scout.
- No new provider becomes routing-enabled merely through daily discovery.
- No admin merge bypass is used.

## Future improvements

After the executable application exists, consider:
- signed research attestations;
- schema-driven provider source adapters;
- independent second-model verification for high-impact pricing/license changes;
- provider changelog/RSS/webhook inputs;
- security advisory feed integration;
- GitHub App authentication;
- merge queue integration;
- automated adapter compatibility test matrix;
- cost-drift alerts.
