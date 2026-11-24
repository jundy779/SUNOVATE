# Nyalakan ulang SUNOVATE di server uji: matikan API dan web lama, pastikan Ollama berjalan,
# lalu nyalakan API (tanpa mulai-ulang otomatis) dan web di dua jendela, dan buka browser.
# Jalankan:  powershell -ExecutionPolicy Bypass -File .\scripts\ops\nyalakan-sunovate.ps1
# Tambahkan -Perbarui untuk mengambil versi terbaru dari GitHub lebih dulu; pustaka dipasang ulang
# hanya bila berkas daftar pustakanya berubah.
param([string]$InstallDir = "C:\SUNOVATE", [switch]$Perbarui)

Write-Host "Mematikan API dan web lama..."
Get-NetTCPConnection -LocalPort 3000,8000 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2

if ($Perbarui) {
    Write-Host "Mengambil versi terbaru dari GitHub..."
    Push-Location $InstallDir
    try {
        $sebelum = (git rev-parse HEAD).Trim()
        git pull --ff-only | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "git pull gagal. Pastikan tidak ada berkas SUNOVATE yang diubah manual di komputer ini." }
        $sesudah = (git rev-parse HEAD).Trim()
        if ($sebelum -eq $sesudah) {
            Write-Host "Sudah versi terbaru."
        } else {
            $berubah = @(git diff --name-only $sebelum $sesudah)
            if ($berubah | Where-Object { $_ -match '(^|/)(package\.json|pnpm-lock\.yaml)$' }) {
                Write-Host "Daftar pustaka web berubah, memasang ulang..."
                # pnpm dapat melapor "Already up to date" dari catatan status yang basi padahal
                # node_modules masih berisi versi lama (ditemukan saat patch 0045). Catatan itu
                # disisihkan agar pnpm memeriksa ulang terhadap pnpm-lock.yaml.
                $state = Join-Path $InstallDir "node_modules\.pnpm-workspace-state-v1.json"
                if (Test-Path $state) { Move-Item $state ($state + ".lama") -Force }
                # Pemberitahuan versi pnpm dimatikan: pengecekannya ke internet dapat mencetak ERR_PNPM
                # sendiri walaupun pemasangan berhasil, dan versi pnpm proyek memang dikunci.
                pnpm install --frozen-lockfile --config.update-notifier=false 2>&1 | Tee-Object -Variable keluaran | Out-Host
                if ($LASTEXITCODE -ne 0 -or (($keluaran | Out-String) -match "ERR_PNPM")) { throw "pnpm install gagal atau melaporkan error ERR_PNPM; lihat pesan di atas." }
            }
            if ($berubah | Where-Object { $_ -match '^apps/api/(uv\.lock|pyproject\.toml)$' }) {
                Write-Host "Daftar pustaka API berubah, memasang ulang..."
                pnpm api:setup | Out-Host
                if ($LASTEXITCODE -ne 0) { throw "pnpm api:setup gagal." }
            }
            Write-Host ("Diperbarui: " + $sebelum.Substring(0, 7) + " -> " + $sesudah.Substring(0, 7)) -ForegroundColor Green
        }
    } catch {
        Write-Host $_.Exception.Message -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
}

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
