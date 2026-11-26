# Pengujian Beban Demo

**Status:** IN PROGRESS

**Last Updated:** 2026-10-19

## Tujuan

Menyediakan probe berulang untuk target demo sekitar 25 pengguna tanpa menganggap satu hasil lokal sebagai jaminan kapasitas komputer kantor.

## Implementasi

`scripts/validation/demo_load_test.py` menggunakan pustaka standar Python dan secara default menjalankan:

- 25 pengguna virtual;
- 4 request per pengguna atau 100 request total;
- target health check pada `127.0.0.1:8080`;
- ambang usulan error rate maksimal 1% dan p95 maksimal 1.500 ms;
- tanpa token, dokumen, pertanyaan SAVI, data pribadi, atau data keuangan.

Target publik dan hostname eksternal selalu ditolak. Target non-loopback hanya dapat berupa IP privat literal dan memerlukan flag `--allow-private-target`.

```bash
pnpm demo:load
```

Contoh untuk host privat yang sudah disetujui:

```bash
pnpm demo:load --target http://192.168.1.50:8080/api/v1/health --allow-private-target
```

## Baseline lokal 2026-10-19

Probe dijalankan langsung ke FastAPI lokal pada port sementara menggunakan backend simulasi, bukan melalui Nginx, web, PostgreSQL, Cloudflare, atau komputer kantor.

| Metrik | Hasil satu kali |
|---|---:|
| Pengguna virtual | 25 |
| Total request | 100 |
| Respons berhasil | 100 |
| Error rate | 0% |
| p50 | 33,50 ms |
| p95 | 41,26 ms |
| p99 | 42,69 ms |
| Throughput | 645,30 request/detik |

Hasil ini hanya memvalidasi alat probe dan baseline API pada mesin pengembangan. Hasil tersebut bukan SLA, bukan benchmark aplikasi penuh, dan bukan bukti kapasitas 25 pengguna pada komputer kantor.

## Uji alur kerja (`pnpm demo:workload`, 2026-11-26)

`scripts/validation/demo_workload_test.py` melengkapi probe di atas dengan skenario steady pada nomor 3: setiap pengguna virtual masuk dengan akun simulasi (lima akun dipakai bergiliran), lalu berulang kali membuka Ringkasan, Basis Pengetahuan, Pencarian, dan Monitoring Kerja dengan jeda acak (bawaan 2 sampai 5 detik); sebagian pengguna bertanya satu kali ke SAVI AI. Skrip mencetak median, P95, dan maksimum per aksi, jumlah gagal, jumlah ditolak hak akses, dan jumlah ditolak pembatas laju (429), lalu menyimpan laporan JSON (bawaan di Desktop). Target dibatasi seperti probe: loopback secara bawaan, IP privat hanya dengan `--izinkan-ip-privat`. Kriteria layak: P95 halaman biasa paling lama 1.500 ms, gagal kurang dari 1%, dan tidak ada 429.

```bash
pnpm demo:workload --pengguna 25 --durasi 120
```

Permintaan sengaja dikirim dari satu komputer, karena di server kantor semua pegawai menghubungi API lewat server web yang sama sehingga API melihat satu alamat. Hasil di laptop pengembangan (Linux, backend simulasi, tanpa model AI):

| Skenario | Permintaan per menit | P95 halaman biasa | Gagal | Ditolak 429 |
|---|---:|---:|---:|---:|
| 25 pengguna, jeda 2 sampai 5 detik, 3 bertanya ke SAVI | 395 | 9 ms | 0 | 0 |
| 25 pengguna, jeda 0,5 sampai 1,5 detik | 1.434 | 8 ms | 0 | 449 dari 986 (45%) |

API sendiri cepat; penolakan pada skenario kedua seluruhnya berasal dari batas gabungan `API_GLOBAL_RATE_LIMIT` (bawaan 600 per menit per alamat IP), yang dibagi seluruh pegawai karena semuanya terbaca sebagai alamat server web. Lihat KL-29. Angka di komputer kantor masih harus diukur.

## Skenario host aktual yang masih wajib

1. Smoke: 1 pengguna, 10 request.
2. Ramp-up: 1 ke 25 pengguna selama periode yang disepakati.
3. Steady: 25 pengguna pada alur landing, login yang disetujui, dashboard, pencarian, dan SAVI dengan data simulasi.
4. Spike: peningkatan sementara dengan batas yang disetujui administrator.
5. Recovery: pastikan respons pulih dan tidak ada koneksi database tertinggal.

Catat CPU, RAM, disk, koneksi database, p50/p95/p99, throughput, status HTTP, error rate, log request ID, dan kondisi setelah uji. Jangan melakukan uji pada tunnel atau alamat publik tanpa persetujuan tertulis TIK/keamanan.

## Gate selesai TASK-013

- spesifikasi komputer dan sistem operasi dicatat;
- Compose/Nginx berhasil dibangun dan diperiksa;
- skenario serta SLA disetujui;
- pengujian melalui seluruh jalur aplikasi lulus pada host aktual;
- CPU/RAM/disk/koneksi database tercatat;
- tidak ada data asli;
- hasil ditinjau mentor dan administrator.
