# Uji keamanan mandiri

## Tujuan

Memeriksa, dengan satu perintah, bahwa pertahanan keamanan SUNOVATE benar-benar bekerja pada instansi yang sedang berjalan. Uji ini menyerang API di komputer sendiri memakai akun simulasi berprivilegsi rendah, lalu memastikan setiap pertahanan menolak sebagaimana mestinya. Ini bukan serangan ke sistem pihak lain: target dibatasi ke loopback secara bawaan, dan hanya permintaan yang memang harus ditolak yang dikirim, sehingga tidak ada data yang diubah.

Catatan tentang "brute force": halaman masuk pengembangan tidak memakai kata sandi (hanya email akun simulasi), jadi tidak ada kata sandi untuk ditebak paksa. Yang relevan dan diuji adalah pembatas laju pada upaya masuk.

## Menjalankan

```bash
pnpm security:selftest
```

API harus menyala lebih dulu (`pnpm api:dev`). Gunakan `--tanpa-laju` untuk melewati uji pembatas laju masuk (uji itu memblokir upaya masuk sesaat setelah dijalankan). Target non-loopback memerlukan `--izinkan-ip-privat` dan IP privat, mengikuti aturan yang sama dengan probe beban. Keluar dengan kode 1 bila ada pemeriksaan GAGAL.

## Yang diperiksa

| Kelompok | Pemeriksaan |
|---|---|
| Autentikasi dan token | Tanpa token, token sampah, token diubah isinya, tanda tangan diganti, dan token tanpa tanda tangan semuanya ditolak 401; email bukan akun nyata tidak menerbitkan token. |
| Naik hak akses | Pembaca tidak bisa membuat pengetahuan atau hasil kerja; pemeriksa tidak bisa membuat hasil kerja; pembaca dan staf tidak bisa membaca riwayat audit; auditor bisa (kontrol positif). |
| BOLA/IDOR dan clearance | Pembaca membuka entri di luar tim/clearance mendapat 404 (bukan 200 atau 403, agar keberadaan tidak bocor); id tak dikenal 404; pembaca non-penerima tidak bisa membuka halaman dokumen rahasia; pembaca sah pun wajib menyetujui pernyataan kerahasiaan dulu (428). |
| Masukan jahat | Pencarian dengan pola injeksi SQL, XSS, path traversal, bita nol, dan string panjang tidak pernah menghasilkan galat 500; jalur menyimpang dan UUID tak sah ditolak bersih; JSON rusak menghasilkan 400/422. |
| Header dan kebocoran | Header `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, dan `Cross-Origin-Opener-Policy` sesuai; CORS tidak mengizinkan kredensial lintas situs; pesan galat dan endpoint kesehatan tidak membocorkan jejak internal atau rahasia. |
| SAVI AI | Permintaan tanpa token ditolak; walau diperintah mengabaikan aturan dan membuka RAHASIA, SAVI menolak (`REFUSED_POLICY`) dan tidak mengutip sumber di atas clearance penanya. |
| Pembatas laju | Upaya masuk berlebih dari satu alamat ditolak 429. |

## Hasil 2026-11-26

Skrip berisi 33 pemeriksaan bila semua bagian berjalan (6 token, 6 hak akses, 4 BOLA/clearance, 6 masukan jahat, 7 header dan kebocoran, 3 SAVI, 1 pembatas laju); dengan `--tanpa-laju` jumlahnya 32.

| Tempat | Hasil |
|---|---|
| Laptop pengembangan (Linux, backend simulasi), `--tanpa-laju` | 32 lulus, 0 gagal |
| Laptop project lead (Windows, backend simulasi), lengkap | 33 lulus, 0 gagal; 429 pada upaya masuk ke-13 |

Upaya ke berapa yang terkena 429 bergantung pada jumlah masuk sebelumnya dalam menit yang sama (batas 20 per menit). SAVI berjalan dalam mode pengembangan ekstraktif dan menolak perintah jahat dengan keputusan `REFUSED_POLICY`.

Yang masih harus diuji ulang di komputer kantor: perilaku penolakan SAVI dan batas clearance sitasi dengan **model AI sungguhan** (Ollama/Hermes), bukan hanya mode ekstraktif. Jalankan `pnpm security:selftest` di sana setelah SUNOVATE menyala.

## Penyadapan dan keamanan jalur (transport)

- Di komputer kantor, pegawai mengakses SUNOVATE lewat jaringan lokal. Lalu lintas saat ini HTTP; untuk akses di luar loopback, jalur sebaiknya dilindungi TLS (HTTPS) agar tidak dapat disadap di jaringan. Ini keputusan infrastruktur bersama TIK.
- Token adalah bearer token di header Authorization, bukan cookie, sehingga tidak ada permukaan CSRF; namun bila jalur tidak terenkripsi, token dapat disadap. Karena itu TLS penting begitu akses keluar dari komputer tunggal.
- Risiko penyadapan terbesar yang sudah tercatat adalah tunnel publik tanpa Cloudflare Access dan halaman masuk tanpa kata sandi (OQ-34): siapa pun yang memegang tautan dapat memilih akun simulasi. Tunnel tidak boleh dinyalakan tanpa keputusan mentor dan TIK.

## Dokumen terkait

- `docs/10-testing/load-testing.md` — uji beban dan alur kerja, termasuk KL-29 (batas laju gabungan).
- `docs/12-governance/` — keputusan dan pertanyaan terbuka (OQ-34 tunnel).
