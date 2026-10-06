# Simulated Data Policy

**Status:** CONFIRMED (prinsip), PROPOSED (detail)
**Last Updated:** 2026-10-06

## Purpose
Aturan pembuatan dan penggunaan data contoh.

## Confirmed Information
- **CONFIRMED** Seluruh seed harus berlabel `SIMULATED_DATA`; tidak boleh memakai data SUN asli (sumber: brief sesi 2026-10-01).
- **CONFIRMED** Tidak boleh mengarang angka SUN, struktur jabatan, atau fungsi SUN Tematik (sumber: brief sesi 2026-10-01).

## Aturan
1. Satu sumber dataset: `apps/api/sunovate_api/store/dataset.py`, dipakai oleh store runtime dan seed PostgreSQL.
2. Setiap record memiliki `data_origin = SIMULATED_DATA`; judul diawali `SIMULASI -`; email memakai domain `@sunovate.local`; nama pengguna generik ("Staf Simulasi PPPSUN").
3. Tidak ada angka keuangan, yield, nilai lelang, nomor surat, NIK, atau nama orang.
4. Isi knowledge contoh menggambarkan proses umum knowledge management, bukan isi peraturan resmi.
5. Deskripsi tim mengikuti Proposal v2.4 slide 10 dan diberi `validation_status = NEEDS_MENTOR_VALIDATION`; SUN Tematik `OPEN_QUESTION` tanpa record kerja atau knowledge.
6. Kasus uji khusus disengaja: entri CONFIDENTIAL (K6), draf (K4), entri IN_REVIEW (K7), dan satu passage injeksi prompt (K5 bagian "Lampiran").
7. Seed menolak berjalan bila `APP_ENV=production`.
8. Respons API selalu membawa `meta.dataLabel = SIMULATED_DATA` dan UI menampilkan label yang sama.
9. File sumber biner di root tidak di-commit (ADR-014) dan tidak dipakai sebagai seed.

## Jawaban Knowledge Owner dan Data Simulasi

- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: Dokumen yang boleh masuk repository dan RAG adalah "semua dokumen yang diusulkan tim kerja" (OQ-04). Ini jawaban cakupan dan **tidak** mencabut aturan di atas: data asli tetap tidak boleh ditambahkan tanpa persetujuan eksplisit (AGENTS.md), dan klasifikasi resmi belum ada (OQ-05). Semua data pengembangan dan pilot tetap `SIMULATED_DATA` sampai gerbang intake dan persetujuan ada (FR-53, BR-35).
- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: Indikator "yield" dan "kepemilikan SBN" diminta (OQ-10). Aturan nomor 3 tetap berlaku: tidak ada angka yield atau kepemilikan, termasuk angka contoh yang menyerupai data nyata. Placeholder tata letak hanya boleh kosong dan berlabel `SIMULATED_DATA` (OQ-21).
- **PROPOSED**: Pengguna simulasi tambahan untuk uji otorisasi (ketua tim dan PIC pada tim yang sama, PIC tiap tim, pengguna tim SUN_TEMATIK tanpa data) hanya memakai sebutan generik, mis. "Knowledge Owner Simulasi PSUN"; tidak ada nama orang, jabatan resmi, atau jumlah anggota tim. Daftarnya ada di [logical-data-model.md](logical-data-model.md) dan belum ditambahkan ke dataset.
- **PROPOSED**: Pengujian dengan dokumen asli hanya setelah persetujuan eksplisit tertulis dan klasifikasi ada; prosedurnya di [rag-testing.md](../10-testing/rag-testing.md). Dokumen asli tidak menjadi fixture, seed, atau isi repository Git (ADR-014, OQ-18).

## Isi dataset
8 pengguna, 6 tim, 8 role, 32 permission, 4 klasifikasi, 8 knowledge entry dengan dokumen, versi, dan 12 chunk, 5 output, 7 tugas, 3 milestone, 3 pending matter, 2 tindak lanjut, 1 approval, 2 isu kualitas data.

## Related Documents
- [glossary.md](../00-project/glossary.md)
- [rag-evaluation.md](../05-ai-rag/rag-evaluation.md)
