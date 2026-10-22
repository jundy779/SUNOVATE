# Pedoman Bahasa Antarmuka SUNOVATE

## Prinsip Wajib

Antarmuka yang dibaca pegawai, mentor, pimpinan, serta pengguna Telegram atau WhatsApp harus memakai bahasa kerja yang jelas. Istilah implementasi pengembang tidak boleh ditampilkan kepada pengguna.

Aturan ini berlaku untuk halaman publik, halaman masuk, ruang kerja, pesan kesalahan, status, tabel, formulir, notifikasi, hasil SAVI, dan laporan yang dihasilkan sistem.

## Pemisahan Bahasa

| Konteks | Ketentuan |
|---|---|
| Antarmuka pengguna | Bahasa Indonesia yang jelas dan sesuai konteks pekerjaan |
| Pesan kesalahan | Menjelaskan keadaan dan langkah pengguna tanpa rincian teknis |
| Dokumentasi pengembang | Boleh memakai nama kode, endpoint, permission, dan istilah arsitektur |
| Kode, log teknis, dan pengujian | Boleh mempertahankan enum serta istilah internal |
| Dokumen resmi | Mengikuti istilah yang sah pada sumber dan tidak boleh diparafrasekan secara menyesatkan |

## Padanan Utama

| Istilah internal | Bahasa antarmuka |
|---|---|
| `SIMULATED_DATA` | Data contoh |
| `PROPOSED` | Usulan / masih menunggu pemeriksaan |
| `BLOCKED` | Belum dapat digunakan |
| runtime | penggunaan sistem |
| API / endpoint | layanan SUNOVATE |
| permission | kewenangan |
| scope | cakupan akses |
| clearance | batas akses informasi |
| Knowledge Hub | Basis Pengetahuan |
| pending matter | hal yang perlu ditindaklanjuti |
| milestone | tahapan penting |
| approval | persetujuan |
| feedback | penilaian atau masukan |
| audit log | riwayat aktivitas |
| retrieval | pencarian sumber |
| embedding | representasi pencarian, hanya bila penjelasan teknis diperlukan |
| SME validation | pemeriksaan substansi |
| legal validation | pemeriksaan dasar hukum |
| escalation | diteruskan kepada pegawai berwenang |

## Larangan

- Jangan menampilkan enum, raw permission code, nama kelas, ID teknis, jalur penyimpanan, atau pesan kesalahan layanan kepada pengguna.
- Jangan memakai istilah bahasa Inggris jika tersedia padanan Indonesia yang lebih jelas, kecuali nama resmi produk atau istilah resmi sumber.
- Jangan mengganti SAVI AI dengan nama internal `Hermes` pada antarmuka.
- Jangan menampilkan detail yang dapat membantu pemetaan infrastruktur atau membingungkan pengguna.
- Jangan menerjemahkan istilah hukum secara bebas apabila perubahan istilah dapat mengubah makna.

## Panduan Singkat

- Isi panduan di `apps/web/src/lib/guides.ts` memakai label yang sama persis dengan tombol dan judul di layar (misalnya "Kirim pertanyaan", "Unduh Excel", "Beri akses baca"). Bila label layar berubah, panduan wajib ikut diperbarui.
- Setiap panduan berisi tiga sampai empat langkah, kalimat pendek, dan tanpa istilah teknis; test `guides.test.ts` menolak istilah seperti API, endpoint, database, token, Hermes, RAG, upload, dan dashboard.
- Panduan hanya ditampilkan bila pengguna memiliki kewenangan terkait, sehingga tidak ada pengguna yang diarahkan ke halaman yang tidak dapat dibukanya.

## Pemeriksaan Sebelum Rilis

1. Telusuri seluruh teks yang dapat terlihat pengguna.
2. Pastikan kode status internal diterjemahkan melalui pemetaan terpusat.
3. Periksa pesan kesalahan pada keadaan gagal dan akses ditolak.
4. Periksa desktop, mobile, hasil cetak, Telegram, dan WhatsApp.
5. Uji bersama pengguna nonteknis dan catat istilah yang masih membingungkan.

