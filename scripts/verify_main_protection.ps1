[CmdletBinding()]
param(
    [string]$Repository = "Vertex-Systems-Network/ai-automation-force",
    [string]$Branch = "main",
    [Parameter(Mandatory = $true)]
    [ValidateSet("independent", "solo-self-review")]
    [string]$ReviewMode
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    throw "Main protection verification failed: $Message"
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Fail "GitHub CLI is not installed."
}

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    Fail "GitHub CLI is not authenticated."
}

$json = gh api `
    -H "Accept: application/vnd.github+json" `
    -H "X-GitHub-Api-Version: 2022-11-28" `
    "repos/$Repository/branches/$Branch/protection"
if ($LASTEXITCODE -ne 0 -or -not $json) {
    Fail "live branch protection could not be read."
}

$protection = $json | ConvertFrom-Json -Depth 20

if ($protection.required_status_checks.strict -ne $true) {
    Fail "required status checks are not strict/up-to-date."
}

$contexts = @($protection.required_status_checks.contexts)
foreach ($required in @("core-domain-contracts", "durable-control-plane")) {
    if ($contexts -notcontains $required) {
        Fail "required check '$required' is not enforced."
    }
}

if ($contexts -contains "validate") {
    Fail "ambiguous legacy check context 'validate' is still configured as a required context."
}

if ($protection.enforce_admins.enabled -ne $true) {
    Fail "administrator enforcement is disabled."
}
if ($protection.required_conversation_resolution.enabled -ne $true) {
    Fail "conversation resolution is not required."
}
if ($protection.allow_force_pushes.enabled -eq $true) {
    Fail "force pushes are allowed."
}
if ($protection.allow_deletions.enabled -eq $true) {
    Fail "branch deletion is allowed."
}

$reviews = $protection.required_pull_request_reviews
if ($null -eq $reviews) {
    Fail "pull-request review protection is absent."
}
if ($reviews.dismiss_stale_reviews -ne $true) {
    Fail "stale review dismissal is disabled."
}

if ($ReviewMode -eq "independent") {
    if ([int]$reviews.required_approving_review_count -lt 1) {
        Fail "independent review mode requires at least one approving review."
    }
    if ($reviews.require_last_push_approval -ne $true) {
        Fail "independent review mode requires last-push approval protection."
    }
}
else {
    if ([int]$reviews.required_approving_review_count -ne 0) {
        Fail "solo SELF REVIEW exception expected zero required approving reviews."
    }
    Write-Warning "Live protection uses the explicit solo SELF REVIEW exception; this is not independent review authority."
}

Write-Host "PASS: live main protection is effective for $Repository/$Branch."
Write-Host "Strict required checks: core-domain-contracts, durable-control-plane"
Write-Host "PR-only integration: enforced"
Write-Host "Admin enforcement: enabled"
Write-Host "Conversation resolution: required"
Write-Host "Force pushes: blocked"
Write-Host "Branch deletion: blocked"
Write-Host "Review mode: $ReviewMode"
