# Pasang server uji SUNOVATE + SAVI AI (Jalur A: SUNOVATE langsung ke model lokal lewat Ollama)
# Memasang yang belum ada: Git, Node.js 22, pnpm 11.4.0, uv, Ollama + model, lalu SUNOVATE di C:\SUNOVATE,
# mengatur SAVI ke model lokal, dan menyalakan aplikasinya. Hanya data contoh; tidak ada data kantor.
# Jalankan di PowerShell "Run as administrator":
#   powershell -ExecutionPolicy Bypass -File .\pasang-server-uji-savi.ps1
# Pilihan: -Model qwen2.5:1.5b (lebih ringan)  -InstallDir D:\SUNOVATE  -NoStart (tidak menyalakan aplikasi)
# Rujukan: docs/11-operations/office-server-trial.md (DEC-20261113-03)

param(
    [string]$Model = "qwen2.5:3b",
    [string]$InstallDir = "C:\SUNOVATE",
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # unduhan di PowerShell 5.1 jauh lebih cepat tanpa progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    Write-Host "Jalankan PowerShell dengan 'Run as administrator', lalu ulangi perintah ini." -ForegroundColor Red
    exit 1
}

$stamp = Get-Date -Format "yyyyMMdd-HHmm"
$desktop = [Environment]::GetFolderPath("Desktop")
$logFile = Join-Path $desktop ("SUNOVATE-pasang-" + $stamp + ".txt")
Start-Transcript -Path $logFile | Out-Null

$tmp = Join-Path $env:TEMP "sunovate-pasang"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$hasil = [ordered]@{}
$modelSiap = $false
$kecepatan = "belum diukur"

function Segarkan-Path {
    $mesin = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = $mesin + ";" + $user + ";" + (Join-Path $HOME ".local\bin")
}
function Ada([string]$perintah) { return [bool](Get-Command $perintah -ErrorAction SilentlyContinue) }
function Unduh([string]$url, [string]$tujuan) { Invoke-WebRequest -Uri $url -OutFile $tujuan -UseBasicParsing }
function Langkah([string]$nama, [scriptblock]$aksi) {
    Write-Host ""
    Write-Host ("=== " + $nama + " ===") -ForegroundColor Cyan
    try {
        $catatan = & $aksi | Select-Object -Last 1
        if ($catatan) { $hasil[$nama] = "OK - " + $catatan } else { $hasil[$nama] = "OK" }
    } catch {
        $hasil[$nama] = "GAGAL - " + $_.Exception.Message
        Write-Warning ($nama + " gagal: " + $_.Exception.Message)
    }
}
function Atur-Env([string]$berkas, [string]$kunci, [string]$nilai) {
    $baris = [System.Collections.Generic.List[string]]([IO.File]::ReadAllLines($berkas))
    $ketemu = $false
    for ($i = 0; $i -lt $baris.Count; $i++) {
        if ($baris[$i] -match ("^" + [regex]::Escape($kunci) + "=")) { $baris[$i] = $kunci + "=" + $nilai; $ketemu = $true }
    }
    if (-not $ketemu) { $baris.Add($kunci + "=" + $nilai) }
    [IO.File]::WriteAllLines($berkas, $baris, (New-Object Text.UTF8Encoding $false))   # tanpa BOM
}
function Acak([int]$panjang) {
    $bytes = New-Object byte[] $panjang
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return (($bytes | ForEach-Object { $_.ToString("x2") }) -join "").Substring(0, $panjang)
}

$ramBebas = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
Write-Host ("RAM bebas saat mulai: " + $ramBebas + " GB")
if ($ramBebas -lt 3) { Write-Warning "RAM bebas kurang dari 3 GB. Tutup browser, Teams, dan Outlook agar model AI dapat berjalan." }
Segarkan-Path

Langkah "Git" {
    if (Ada "git") { return "sudah ada: " + (git --version) }
    try {
        $rilis = Invoke-RestMethod -Uri "https://api.github.com/repos/git-for-windows/git/releases/latest" -UseBasicParsing
    } catch {
        throw "daftar rilis Git tidak dapat dibaca (batas akses GitHub atau jaringan). Pasang Git manual dari git-scm.com, lalu jalankan ulang skrip ini"
    }
    $aset = $rilis.assets | Where-Object { $_.name -match '^Git-[\d.]+-64-bit\.exe$' } | Select-Object -First 1
    if (-not $aset) { throw "berkas pemasang Git tidak ditemukan di rilis terbaru" }
    $berkas = Join-Path $tmp $aset.name
    Unduh $aset.browser_download_url $berkas
    $p = Start-Process -FilePath $berkas -ArgumentList "/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-" -PassThru
    $p.WaitForExit()   # hanya proses pemasang; -Wait ikut menunggu aplikasi yang dinyalakan pemasang
if ($p.ExitCode -ne 0) { throw ("pemasang Git keluar dengan kode " + $p.ExitCode) }
    Segarkan-Path
    if (-not (Ada "git")) { throw "git belum terdeteksi setelah dipasang" }
    return "dipasang: " + (git --version)
}

Langkah "Node.js 22" {
    if (Ada "node") {
        $mayor = [int]((node -v).TrimStart("v").Split(".")[0])
        if ($mayor -ge 22) { return "sudah ada: " + (node -v) }
    }
    $daftar = (Invoke-WebRequest -Uri "https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt" -UseBasicParsing).Content
    $baris = ($daftar -split "`n") | Where-Object { $_ -match 'node-v22\.[\d.]+-x64\.msi\s*$' } | Select-Object -First 1
    if (-not $baris) { throw "pemasang Node.js 22 tidak ditemukan" }
    $bagian = $baris.Trim() -split '\s+'
    $berkas = Join-Path $tmp $bagian[1]
    Unduh ("https://nodejs.org/dist/latest-v22.x/" + $bagian[1]) $berkas
    if ((Get-FileHash $berkas -Algorithm SHA256).Hash -ne $bagian[0].ToUpper()) { throw "sidik SHA-256 Node.js tidak cocok; berkas tidak dipasang" }
    $p = Start-Process -FilePath "msiexec.exe" -ArgumentList ('/i "' + $berkas + '" /qn /norestart') -PassThru
    $p.WaitForExit()   # hanya proses pemasang; -Wait ikut menunggu aplikasi yang dinyalakan pemasang
if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) { throw ("pemasang Node.js keluar dengan kode " + $p.ExitCode) }
    Segarkan-Path
    return "dipasang: " + (node -v) + ", sidik SHA-256 cocok"
}

Langkah "pnpm 11.4.0" {
    if ((Ada "pnpm") -and ((pnpm -v) -eq "11.4.0")) { return "sudah ada: 11.4.0" }
    if (-not (Ada "npm")) { throw "npm tidak ditemukan; Node.js belum terpasang" }
    npm install -g pnpm@11.4.0 | Out-Host
    if ($LASTEXITCODE -ne 0) { throw ("npm keluar dengan kode " + $LASTEXITCODE) }
    Segarkan-Path
    return "dipasang: " + (pnpm -v)
}

Langkah "uv" {
    if (Ada "uv") { return "sudah ada: " + (uv --version) }
    $berkas = Join-Path $tmp "uv-install.ps1"
    Unduh "https://astral.sh/uv/install.ps1" $berkas
    & powershell -NoProfile -ExecutionPolicy Bypass -File $berkas | Out-Host
    Segarkan-Path
    if (-not (Ada "uv")) { throw "uv belum terdeteksi setelah dipasang" }
    return "dipasang: " + (uv --version)
}

Langkah "Ollama" {
    if (-not (Ada "ollama")) {
        $berkas = Join-Path $tmp "OllamaSetup.exe"
        Unduh "https://ollama.com/download/OllamaSetup.exe" $berkas
        $p = Start-Process -FilePath $berkas -ArgumentList "/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES" -PassThru
        $p.WaitForExit()   # hanya proses pemasang; -Wait ikut menunggu aplikasi yang dinyalakan pemasang
if ($p.ExitCode -ne 0) { throw ("pemasang Ollama keluar dengan kode " + $p.ExitCode + " (Windows 10 versi 1909 mungkin terlalu lama)") }
        Segarkan-Path
        if (-not (Ada "ollama")) { throw "ollama belum terdeteksi setelah dipasang" }
    }
    $jalan = $false
    try { Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3 | Out-Null; $jalan = $true } catch { }
    if (-not $jalan) {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        for ($i = 0; $i -lt 30 -and -not $jalan; $i++) {
            Start-Sleep -Seconds 2
            try { Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3 | Out-Null; $jalan = $true } catch { }
        }
    }
    if (-not $jalan) { throw "Ollama terpasang tetapi tidak mau berjalan (kemungkinan karena versi Windows)" }
    return "berjalan di 127.0.0.1:11434"
}

if ($hasil["Ollama"] -like "OK*") {
    Langkah ("Model " + $Model) {
        ollama pull $Model | Out-Host
        if ($LASTEXITCODE -ne 0) { throw ("ollama pull keluar dengan kode " + $LASTEXITCODE) }
        $modelfile = Join-Path $tmp "Modelfile"
        [IO.File]::WriteAllLines($modelfile, @(("FROM " + $Model), "PARAMETER num_ctx 8192"), (New-Object Text.UTF8Encoding $false))
        ollama create savi-uji -f $modelfile | Out-Host
        if ($LASTEXITCODE -ne 0) { throw ("ollama create keluar dengan kode " + $LASTEXITCODE) }
        $body = @{ model = "savi-uji"; prompt = "Jelaskan singkat dalam dua kalimat apa itu Surat Utang Negara."; stream = $false } | ConvertTo-Json
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 600
        if ($r.eval_duration -gt 0) {
            $script:kecepatan = ([math]::Round($r.eval_count / ($r.eval_duration / 1e9), 1)).ToString() + " token per detik"
        }
        $script:modelSiap = $true
        return "savi-uji (dari " + $Model + ", konteks 8192), kecepatan " + $kecepatan
    }
}

Langkah "SUNOVATE" {
    if (-not (Ada "git")) { throw "git belum terpasang" }
    if (Test-Path (Join-Path $InstallDir ".git")) {
        git -C $InstallDir pull --ff-only | Out-Host
    } else {
        git clone https://github.com/jundy779/SUNOVATE.git $InstallDir | Out-Host
    }
    if ($LASTEXITCODE -ne 0) { throw ("git keluar dengan kode " + $LASTEXITCODE) }
    $envFile = Join-Path $InstallDir ".env"
    if (-not (Test-Path $envFile)) { Copy-Item (Join-Path $InstallDir ".env.example") $envFile }
    if (-not ((Get-Content $envFile) -match "^DEV_AUTH_SECRET=.{32,}")) { Atur-Env $envFile "DEV_AUTH_SECRET" (Acak 48) }
    if ($modelSiap) {
        Atur-Env $envFile "HERMES_MODE" "hermes_agent"
        Atur-Env $envFile "HERMES_AGENT_BASE_URL" "http://127.0.0.1:11434/v1"
        Atur-Env $envFile "HERMES_AGENT_API_KEY" (Acak 24)
        Atur-Env $envFile "HERMES_AGENT_MODEL" "savi-uji"
        Atur-Env $envFile "HERMES_AGENT_TIMEOUT_SECONDS" "180"
    } else {
        Atur-Env $envFile "HERMES_MODE" "development"
    }
    Push-Location $InstallDir
    try {
        pnpm install | Out-Host
        if ($LASTEXITCODE -ne 0) { throw ("pnpm install keluar dengan kode " + $LASTEXITCODE) }
        pnpm api:setup | Out-Host
        if ($LASTEXITCODE -ne 0) { throw ("pnpm api:setup keluar dengan kode " + $LASTEXITCODE) }
    } finally { Pop-Location }
    if ($modelSiap) { return "terpasang di " + $InstallDir + ", SAVI memakai model lokal" }
    return "terpasang di " + $InstallDir + ", SAVI mode pengembangan (model belum siap)"
}

if (-not $NoStart -and $hasil["SUNOVATE"] -like "OK*") {
    Langkah "Menyalakan aplikasi" {
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", ("Set-Location '" + $InstallDir + "'; pnpm api:dev")
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", ("Set-Location '" + $InstallDir + "'; pnpm dev")
        $siap = $false
        for ($i = 0; $i -lt 90 -and -not $siap; $i++) {
            Start-Sleep -Seconds 2
            try { Invoke-WebRequest -Uri "http://127.0.0.1:3000/login" -UseBasicParsing -TimeoutSec 10 | Out-Null; $siap = $true } catch { }
        }
        if (-not $siap) { throw "halaman belum terbuka dalam 3 menit; periksa dua jendela PowerShell yang baru terbuka" }
        Start-Process "http://127.0.0.1:3000"
        return "terbuka di http://127.0.0.1:3000"
    }
}

Write-Host ""
Write-Host "=== RINGKASAN ===" -ForegroundColor Cyan
foreach ($k in $hasil.Keys) { Write-Host ("{0,-22}: {1}" -f $k, $hasil[$k]) }
Write-Host ""
Write-Host "Masuk sebagai sim.staff.pppsun@sunovate.local, buka SAVI AI, lalu ajukan lima pertanyaan uji di panduan bagian 6."
Write-Host "Untuk mematikan: tutup dua jendela PowerShell aplikasi. Untuk kembali ke mode tanpa model: ubah HERMES_MODE=development di .env."
Stop-Transcript | Out-Null
Write-Host ("Log lengkap: " + $logFile + "  (kirim berkas ini ke tim SUNOVATE)")
