# Run the same checks expected before handoff. Reports actual exit codes.
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$steps = @("lint", "typecheck", "test", "build", "db:sql")
$failed = @()
foreach ($step in $steps) {
    Write-Host "==> pnpm $step"
    pnpm $step | Out-Host
    if ($LASTEXITCODE -ne 0) { $failed += $step }
}
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "==> pnpm compose:check"
    pnpm compose:check | Out-Host
    if ($LASTEXITCODE -ne 0) { $failed += "compose:check" }
} else {
    Write-Host "SKIPPED compose:check: docker is not installed on this machine."
}
if ($failed.Count) { Write-Error "Failed: $($failed -join ', ')" } else { Write-Host "All checks passed." }
