# Install web (pnpm) and API (uv) dependencies. Development only.
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

pnpm install
pnpm api:setup

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example (placeholder values only)."
}
Write-Host "Setup complete. Run: pnpm api:dev (terminal 1) and pnpm dev (terminal 2)."
