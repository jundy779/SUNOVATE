# Start the API in a new PowerShell window and the web app in this one.
$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\..\.."
Start-Process pwsh -WorkingDirectory $root -ArgumentList "-NoExit", "-Command", "pnpm api:dev"
Set-Location $root
pnpm dev
