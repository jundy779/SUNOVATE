# Kerangka Panduan Pengguna

**Status:** PROPOSED

**Last Updated:** 2026-10-01

## Purpose

Menyusun kerangka bab panduan pengguna SUNOVATE yang akan ditulis lengkap setelah alur dan hak akses divalidasi. Dokumen ini hanya kerangka; isi bab belum ditulis.

## Status

- **PROPOSED**: Kerangka disusun dari fitur yang ada pada scaffold dan prioritas P0 MVP (sumber: Proposal v2.4, slide 11; implementasi scaffold sesi 2026-10-01).
- **PROPOSED**: Panduan lengkap ditulis pada Bulan 6 bersama dokumentasi dan handover (sumber: Proposal v2.4, slide 21).
- **OPEN QUESTION**: Mekanisme login final (OQ-07), sehingga Bab 2 belum dapat ditulis lengkap.
- **OPEN QUESTION**: Bab untuk SUN Tematik belum disusun karena fungsinya belum dikonfirmasi (OQ-01).

## Kerangka Bab

### Bab 1. Pengenalan SUNOVATE

- Tujuan SUNOVATE dan batasannya: tidak menggantikan sistem transaksi SUN resmi, tidak mengambil keputusan keuangan, tidak memberikan akses dokumen tanpa otorisasi (sumber: brief sesi 2026-10-01).
- Perbedaan SUNOVATE dengan SUN Job Monitor.
- Arti label klasifikasi dan label data.

### Bab 2. Masuk dan Keluar

- Cara login (menunggu OQ-07).
- Sesi berakhir dan login ulang.
- Halaman tidak berwenang (`/unauthorized`).

### Bab 3. Navigasi dan Dashboard

- Struktur menu (lihat [navigation.md](../09-ui-ux/navigation.md)).
- Dashboard sesuai hak akses dan arti setiap indikator (menunggu OQ-10).

### Bab 4. Knowledge Repository

- Jenis knowledge: regulasi, kebijakan, kajian, SOP, playbook, laporan, bahan rapat, close out note, lesson learned, tacit knowledge, decision record, arsip, referensi.
- Membuat draft, memperbarui, dan mengajukan review.
- Status siklus hidup: DRAFT, IN_REVIEW, PUBLISHED, SUPERSEDED, ARCHIVED.
- Menangani pesan konflik pembaruan.

### Bab 5. Dokumen dan Versi

- Dokumen sebagai referensi ke lokasi provider, bukan file yang diunggah ke SUNOVATE.
- Melihat riwayat versi dan mendaftarkan versi baru.
- Pesan duplikasi checksum.

### Bab 6. Pencarian

- Menulis kata kunci yang efektif.
- Mengapa sebagian dokumen tidak muncul (hak akses dan status terbit).

### Bab 7. Hermes AI Knowledge Assistant

- Apa yang dapat dan tidak dapat ditanyakan.
- Membaca sitasi dan memeriksa sumber.
- Arti setiap jenis jawaban: dijawab, bukti tidak cukup, di luar cakupan, ditolak kebijakan, perlu persetujuan manusia, diblok penjaga output.
- Memberi umpan balik.
- Pengingat: jawaban Hermes bukan keputusan dan harus diverifikasi ke sumber.

### Bab 8. Monitoring Pekerjaan

- Output kerja, tugas, milestone, pending matters, dan follow-up.
- Arti status tugas dan deadline state (ambang menunggu OQ-15).

### Bab 9. Review dan Approval

- Mengajukan, meninjau, dan memutuskan permintaan approval.
- Aturan tidak dapat memutuskan permintaan sendiri.
- Alur publikasi knowledge (menunggu OQ-12).

### Bab 10. Peran dan Hak Akses

- Ringkasan role dan apa yang dapat dilakukan (menunggu validasi matriks).
- Cara meminta perubahan akses.

### Bab 11. Bantuan dan Pelaporan Masalah

- Cara melaporkan masalah dengan `X-Request-ID`.
- Kontak pengelola (OPEN QUESTION).

### Lampiran

- Glosarium (rujuk [glossary.md](../00-project/glossary.md)).
- Pertanyaan yang sering diajukan.

## Aturan Penulisan Panduan

- **PROPOSED**: Bahasa Indonesia formal dan ringkas; tangkapan layar hanya memakai data `SIMULATED_DATA`.
- **PROPOSED**: Tidak memuat nama pegawai, jabatan, nomor surat tugas, atau angka SUN asli.
- **PROPOSED**: Setiap bab diperbarui bila perilaku fitur berubah.

## Related Documents

- [user-personas.md](../01-product/user-personas.md)
- [information-architecture.md](../09-ui-ux/information-architecture.md)
- [uat-plan.md](../10-testing/uat-plan.md)
