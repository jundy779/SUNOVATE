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
