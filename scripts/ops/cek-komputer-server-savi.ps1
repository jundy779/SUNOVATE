# Cek kesiapan komputer sebagai server uji SUNOVATE + SAVI AI (model AI lokal)
# Hanya MEMBACA informasi. Tidak memasang, mengubah, atau mengirim apa pun ke luar komputer.
# Jalankan di PowerShell:  powershell -ExecutionPolicy Bypass -File .\cek-komputer-server-savi.ps1
# Pemeriksaan TPM butuh PowerShell "Run as administrator"; tanpa itu bagian TPM dilewati.

$ErrorActionPreference = "SilentlyContinue"
$lines = New-Object System.Collections.Generic.List[string]
function Tulis($teks) { Write-Host $teks; $lines.Add($teks) }
function GB($bytes) { [math]::Round($bytes / 1GB, 1) }

Tulis "=== CEK KOMPUTER UNTUK SERVER UJI SUNOVATE ==="
Tulis ("Waktu        : " + (Get-Date -Format "dd-MM-yyyy HH:mm"))
Tulis ("Komputer     : " + $env:COMPUTERNAME)

$os = Get-CimInstance Win32_OperatingSystem
Tulis ("Windows      : " + $os.Caption + " (build " + $os.BuildNumber + ")")

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Tulis ("Prosesor     : " + $cpu.Name.Trim())
Tulis ("Inti/Thread  : " + $cpu.NumberOfCores + " inti / " + $cpu.NumberOfLogicalProcessors + " thread")
Tulis ("Virtualisasi : " + $(if ($cpu.VirtualizationFirmwareEnabled) { "aktif di BIOS" } else { "tidak aktif atau tidak terbaca" }))

$ramTotal = GB (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramFree = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
Tulis ("RAM          : " + $ramTotal + " GB total, " + $ramFree + " GB bebas saat ini")

$gpus = Get-CimInstance Win32_VideoController
foreach ($g in $gpus) {
    $vram = if ($g.AdapterRAM -gt 0) { " (" + (GB $g.AdapterRAM) + " GB)" } else { "" }
    Tulis ("Kartu grafis : " + $g.Name + $vram)
}
$diskretNvidia = $gpus | Where-Object { $_.Name -match "NVIDIA" }

$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
Tulis ("Disk C:      : " + (GB $disk.FreeSpace) + " GB bebas dari " + (GB $disk.Size) + " GB")
if ((GB $disk.FreeSpace) -lt 20) {
    Tulis "PERHATIAN    : ruang kosong di C: kurang dari 20 GB. Model 7B butuh sekitar 5 GB, Hermes Agent dan SUNOVATE beberapa GB lagi."
}

Tulis ""
Tulis "--- Penyimpan kunci (TPM), butir 5 paket tinjauan mentor ---"
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$tpm = $null
if ($isAdmin) { $tpm = Get-Tpm }
if ($null -eq $tpm -or $null -eq $tpm.TpmPresent) {
    Tulis "TPM          : tidak terbaca (jalankan PowerShell sebagai administrator untuk memeriksa)"
} else {
    Tulis ("TPM          : ada=" + $tpm.TpmPresent + ", siap=" + $tpm.TpmReady + ", aktif=" + $tpm.TpmEnabled)
}

Tulis ""
Tulis "--- Perangkat lunak yang sudah terpasang ---"
foreach ($nama in @("git", "node", "pnpm", "python", "uv", "ollama", "wsl")) {
    $cmd = Get-Command $nama
    Tulis ("{0,-12} : {1}" -f $nama, $(if ($cmd) { "ada" } else { "belum ada" }))
}
# wsl.exe writes UTF-16; drop the NUL characters so the text reads normally.
$wsl = ((wsl --status 2>$null) -join " ") -replace "`0", ""
if ($wsl.Trim()) { Tulis ("WSL status   : " + (($wsl -replace "\s+", " ").Trim())) }

Tulis ""
Tulis "--- Port yang dipakai SUNOVATE ---"
foreach ($p in @(3000, 8000, 8642, 11434)) {
    $dipakai = Get-NetTCPConnection -LocalPort $p -State Listen
    Tulis ("Port {0,-6}  : {1}" -f $p, $(if ($dipakai) { "SEDANG DIPAKAI program lain" } else { "kosong" }))
}

Tulis ""
Tulis "--- Rekomendasi model AI lokal (CPU, tanpa kartu grafis khusus) ---"
if ($diskretNvidia) {
    Tulis "Ada kartu grafis NVIDIA: model 7B dapat berjalan jauh lebih cepat. Catat jenisnya untuk tim."
}
if ($ramTotal -ge 15) {
    Tulis "RAM >= 16 GB : coba qwen2.5:7b (sekitar 5 GB). Perkiraan di i5 tanpa GPU: 3-6 kata per detik."
    Tulis "               Cadangan bila terlalu lambat: qwen2.5:3b."
} elseif ($ramTotal -ge 7.5) {
    Tulis "RAM 8 GB     : coba qwen2.5:3b (sekitar 2 GB). Model 7B kemungkinan terlalu berat."
} else {
    Tulis "RAM < 8 GB   : tidak disarankan sebagai server model AI."
}

# Uji kecepatan hanya bila Ollama sudah terpasang dan sedang berjalan.
$tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
if ($tags -and $tags.models) {
    $model = $tags.models[0].name
    Tulis ""
    Tulis ("--- Uji kecepatan model lokal: " + $model + " ---")
    $body = @{ model = $model; prompt = "Jelaskan singkat dalam dua kalimat apa itu Surat Utang Negara."; stream = $false } | ConvertTo-Json
    $mulai = Get-Date
    $hasil = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 300
    $detik = [math]::Round(((Get-Date) - $mulai).TotalSeconds, 1)
    if ($hasil -and $hasil.eval_duration -gt 0) {
        $tps = [math]::Round($hasil.eval_count / ($hasil.eval_duration / 1e9), 1)
        Tulis ("Waktu jawab  : " + $detik + " detik, kecepatan " + $tps + " token per detik")
    } else {
        Tulis "Uji kecepatan gagal; catat pesan error dari jendela Ollama."
    }
} else {
    Tulis ""
    Tulis "Ollama belum berjalan, jadi uji kecepatan model dilewati."
}

$keluaran = Join-Path ([Environment]::GetFolderPath("Desktop")) ("SUNOVATE-cek-server-" + (Get-Date -Format "yyyyMMdd-HHmm") + ".txt")
$lines | Out-File -FilePath $keluaran -Encoding utf8
Write-Host ""
Write-Host ("Laporan disimpan di: " + $keluaran)
Write-Host "Kirim isi berkas laporan itu ke tim SUNOVATE. Berkas ini tidak berisi kata sandi atau data kantor."
