# Paket Demo Satu Komputer

**Status:** PROPOSED — NOT ACTIVATED

**Data:** `SIMULATED_DATA` only

Paket ini menyiapkan Nginx, web, API Python, dan PostgreSQL untuk pengujian pada satu komputer. Port pengguna hanya diikat ke `127.0.0.1`; API dan PostgreSQL tidak dipublikasikan ke host.

## Gate wajib

Jangan jalankan pada komputer kantor atau mengaktifkan tunnel sebelum mentor serta TIK/keamanan menyetujui host, Docker, akun administrator, domain, daftar pengguna, login, backup, firewall, egress, TLS, logging, masa demo, dan kill switch. Data asli tetap dilarang.

## Validasi paket

1. Salin `demo.env.example` ke `demo.env` dan ganti seluruh placeholder dengan rahasia acak. `demo.env` tidak boleh masuk Git.
2. Pada Linux, batasi izin berkas dengan `chmod 600 deploy/demo/demo.env`.
3. Jalankan preflight statis dan environment. Pemeriksaan ini tidak menyalakan container atau tunnel:

   ```bash
   pnpm demo:preflight -- --env-file deploy/demo/demo.env
   ```

4. Tinjau `docker-compose.demo.yml`, `nginx/nginx.conf`, dan image yang dipakai bersama administrator.
5. Jalankan pemeriksaan konfigurasi Docker:

   ```bash
   docker compose --env-file deploy/demo/demo.env \
     -f deploy/demo/docker-compose.demo.yml config --quiet
   ```

6. Setelah seluruh gate disetujui, administrator dapat membangun dan menjalankan paket. Aktivasi Cloudflare tetap langkah terpisah dan tidak disediakan sebagai perintah otomatis.

`cloudflared.example.yml` hanya kerangka tanpa kredensial. Konfigurasi tersebut memakai domain `.invalid` dan tidak dapat menjadi akses publik yang berfungsi.

Preflight tanpa `--env-file` hanya memeriksa scaffold yang dilacak Git. Status
`environmentFile: NOT_CHECKED` berarti secret dan kesesuaian URL database nyata belum diperiksa.
Access log Nginx hanya menyimpan metode dan path, bukan query string, agar istilah pencarian tidak
masuk log proxy.

## Batas teknis

- Konfigurasi ini belum membuktikan kapasitas komputer kantor.
- Login development hanya untuk data simulasi dan bukan autentikasi produksi.
- Timeout Nginx menghentikan koneksi klien, tetapi tidak dianggap pembatalan transaksi backend.
- Circuit breaker baru diterapkan ketika provider eksternal resmi sudah dipilih dan disetujui.
- Load test host aktual, backup/restore drill, security review, serta UAT tetap wajib.
