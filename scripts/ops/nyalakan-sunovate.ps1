# Nyalakan ulang SUNOVATE di server uji: matikan API dan web lama, pastikan Ollama berjalan,
# lalu nyalakan API (tanpa mulai-ulang otomatis) dan web di dua jendela, dan buka browser.
# Jalankan:  powershell -ExecutionPolicy Bypass -File .\scripts\ops\nyalakan-sunovate.ps1
param([string]$InstallDir = "C:\SUNOVATE")

Write-Host "Mematikan API dan web lama..."
Get-NetTCPConnection -LocalPort 3000,8000 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
[IO.File]::WriteAllText((Join-Path $InstallDir "apps\web\.env.local"), "SUNOVATE_API_URL=http://127.0.0.1:8000`r`n", (New-Object Text.UTF8Encoding $false))

try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 3 | Out-Null }
catch {
    if (Get-Command ollama -ErrorAction SilentlyContinue) { Write-Host "Menyalakan Ollama..."; Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden }
}

Write-Host "Menyalakan API..."
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", ("Set-Location '" + $InstallDir + "'; uv run --directory apps/api --extra dev uvicorn sunovate_api.main:app --port 8000")
$ok = $false
for ($i = 0; $i -lt 60 -and -not $ok; $i++) {
    Start-Sleep -Seconds 2
    try { $ok = (Invoke-RestMethod http://127.0.0.1:8000/api/v1/health -TimeoutSec 3).data.status -eq "ok" } catch { }
}
if (-not $ok) { Write-Host "API belum menyala. Lihat pesan di jendela API." -ForegroundColor Red; exit 1 }
Write-Host "API siap." -ForegroundColor Green

Write-Host "Menyalakan web (bisa 1-3 menit)..."
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", ("Set-Location '" + $InstallDir + "'; pnpm dev")
$ok = $false
for ($i = 0; $i -lt 100 -and -not $ok; $i++) {
    Start-Sleep -Seconds 3
    try { Invoke-WebRequest http://localhost:3000/login -UseBasicParsing -TimeoutSec 30 | Out-Null; $ok = $true } catch { }
}
if ($ok) { Write-Host "Web siap: http://localhost:3000" -ForegroundColor Green; Start-Process "http://localhost:3000/login" }
else { Write-Host "Web belum menyala. Lihat pesan di jendela web." -ForegroundColor Red; exit 1 }
