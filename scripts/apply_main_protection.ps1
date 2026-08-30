[CmdletBinding()]
param(
    [string]$Repository = "Vertex-Systems-Network/ai-automation-force",
    [string]$Branch = "main",
    [Parameter(Mandatory = $true)]
    [ValidateSet("independent", "solo-self-review")]
    [string]$ReviewMode
)

$ErrorActionPreference = "Stop"
$GitHubActionsAppId = 15368
$ApiVersion = "2026-03-10"

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Install/authenticate GitHub CLI before applying repository protection."
    }
}

Require-Command "gh"

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated."
}

$requiredApprovals = if ($ReviewMode -eq "independent") { 1 } else { 0 }
$requireLastPushApproval = $ReviewMode -eq "independent"

$payload = [ordered]@{
    required_status_checks = [ordered]@{
        strict = $true
        contexts = @()
        checks = @(
            [ordered]@{ context = "core-domain-contracts"; app_id = $GitHubActionsAppId },
            [ordered]@{ context = "durable-control-plane"; app_id = $GitHubActionsAppId }
        )
    }
    enforce_admins = $true
    required_pull_request_reviews = [ordered]@{
        dismiss_stale_reviews = $true
        require_code_owner_reviews = $false
        required_approving_review_count = $requiredApprovals
        require_last_push_approval = $requireLastPushApproval
        dismissal_restrictions = @{}
        bypass_pull_request_allowances = @{}
    }
    restrictions = $null
    required_conversation_resolution = $true
    required_linear_history = $false
    allow_force_pushes = $false
    allow_deletions = $false
    block_creations = $false
    lock_branch = $false
    allow_fork_syncing = $false
}

$temp = New-TemporaryFile
try {
    $payload | ConvertTo-Json -Depth 10 | Set-Content -Path $temp -Encoding utf8
    gh api `
        --method PUT `
        -H "Accept: application/vnd.github+json" `
        -H "X-GitHub-Api-Version: $ApiVersion" `
        "repos/$Repository/branches/$Branch/protection" `
        --input $temp
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub rejected the branch-protection update."
    }
}
finally {
    Remove-Item $temp -Force -ErrorAction SilentlyContinue
}

Write-Host "Applied protected-$Branch policy to $Repository."
Write-Host "Required GitHub Actions checks: core-domain-contracts, durable-control-plane (app_id=$GitHubActionsAppId)"
if ($ReviewMode -eq "independent") {
    Write-Host "Review mode: at least one independent approving review; stale approvals dismissed; last-push approval enforced."
}
else {
    Write-Warning "Review mode: explicit solo SELF REVIEW exception. Independent approval is not claimed; review provenance must remain explicit in PR/checkpoint evidence."
}
Write-Host "Run scripts/verify_main_protection.ps1 with the same ReviewMode to certify live read-back before closing the governance gate."
