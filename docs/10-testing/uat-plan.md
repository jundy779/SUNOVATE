# Rencana User Acceptance Test (UAT)

**Status:** NEEDS MENTOR VALIDATION

**Last Updated:** 2026-10-09

## Purpose

Menyusun kerangka UAT SUNOVATE: skenario per persona, peserta, lingkungan, sign-off, dan formulir umpan balik.

## Status

- **PROPOSED**: UAT direncanakan pada Bulan 6 (Implementasi) bersama security test, bug fixing, dokumentasi, dan handover (sumber: Proposal v2.4, slide 21).
- **OPEN QUESTION**: Peserta UAT dan pengguna uji yang ditunjuk (OQ-20).
- **OPEN QUESTION**: Lingkungan UAT (OQ-20) dan hosting (OQ-07).
- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: Pilot mencakup "6 tim" (OQ-03); nama tim dianggap enam tim brief (PROPOSED, OQ-02), ditambah MONEV sejak 2026-10-20 (DEC-20261020-01). **OPEN QUESTION**: proses yang dipilot dan pengakuan mentor (OQ-24).
- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: Hosting pilot adalah komputer tersendiri sebagai server (OQ-07); lingkungan UAT dan persyaratan server tetap OPEN QUESTION (OQ-20, OQ-23).

## Prinsip

- **PROPOSED (project lead, 2026-10-09):** cohort demo/UAT sekitar 25 pengguna. Angka ini target perencanaan, bukan daftar pengguna yang sudah ditunjuk atau klaim kapasitas.
- **NEEDS APPROVAL:** penggunaan komputer kantor dan Cloudflare Tunnel/Access mengikuti OQ-20, OQ-23, dan OQ-34. Hanya `SIMULATED_DATA` yang boleh dipakai.
- Sebelum UAT, load test harus mengukur latency, error rate, CPU, RAM, disk, dan koneksi database pada host aktual; backup/restore serta kill switch tunnel harus diuji.

- **CONFIRMED**: UAT memakai data `SIMULATED_DATA` saja; data internal atau data keuangan asli tidak dipakai (sumber: brief sesi 2026-10-01, AGENTS.md).
- **PROPOSED**: Peserta memakai akun uji yang dipetakan ke role pengembangan; role adalah usulan dan bukan jabatan resmi (sumber: brief sesi 2026-10-01).
- **PROPOSED**: Setiap skenario dinilai Lulus, Lulus dengan catatan, atau Gagal; temuan dicatat di register bug dengan severity P0–P3.

## Skenario per Persona (PROPOSED)

Persona dan role mengikuti role pengembangan usulan. Pengguna simulasi di kolom terakhir dipakai bila peserta belum ditunjuk.

| ID | Persona (role) | Skenario | Hasil yang diharapkan | Pengguna simulasi |
|---|---|---|---|---|
| UAT-01 | staff | Membuat draft knowledge lalu mengajukan review. **Bertentangan dengan jawaban knowledge owner** (hak ubah/unggah hanya ketua tim, kasubdit PMP, Kasi MP, PIC; PD-1). Berlaku hanya pada matriks saat ini; setelah PD-1 diganti UAT-12 dan UAT-13 | Status `IN_REVIEW`, tercatat di audit (matriks saat ini) | `sim.staff.pppsun` |
| UAT-02 | staff | Mencari dokumen dan membuka hasil | Hanya hasil yang boleh dibaca yang tampil | `sim.staff.pppsun` |
| UAT-03 | knowledge_owner | Memperbarui knowledge yang sedang dibuka pengguna lain | Konflik terdeteksi, tidak ada perubahan yang tertimpa diam-diam | `sim.owner.ppsun` |
| UAT-04 | knowledge_owner | Mendaftarkan versi dokumen baru | Versi tercatat dengan checksum; duplikasi ditolak | `sim.owner.ppsun` |
| UAT-05 | reviewer | Meninjau dan memutuskan permintaan approval | Keputusan tercatat; tidak dapat memutuskan permintaan sendiri | `sim.reviewer.akpsun` |
| UAT-06 | team_lead | Memantau output, tugas, dan pending matters tim | Deadline state tampil sesuai backend; hanya data tim sendiri | `sim.lead.psun` |
| UAT-07 | knowledge_coordinator | Melihat knowledge lintas tim dan menerbitkan lewat approval | Publikasi hanya melalui approval yang disetujui | `sim.coordinator` |
| UAT-08 | auditor | Membaca audit log dan isu kualitas data | Audit tampil; tidak ada aksi ubah data | `sim.auditor` |
| UAT-09 | read_only | Membuka dashboard dan bertanya ke Hermes | Jawaban bersitasi atau penolakan yang jelas; tidak ada tombol ubah | `sim.readonly.dhtv` |
| UAT-10 | staff | Bertanya ke Hermes di luar domain SUN dan meminta aksi tulis | Ditolak atau `REQUIRES_HUMAN_APPROVAL`; tidak ada aksi dieksekusi | `sim.staff.pppsun` |
| UAT-11 | system_admin | Melihat pengguna, tim, role, dan status provider | Data tampil sesuai permission; provider produksi berstatus nonaktif | `sim.admin` |
| UAT-12 | staff (setelah PD-1) | Mencoba membuat atau mengajukan knowledge | Ditolak dengan pesan jelas; hanya membaca, mencari, bertanya ke Hermes, dan memperbarui tugas. PLANNED, hari ini akan gagal | `sim.staff.pppsun` |
| UAT-13 | team_lead atau knowledge_owner | Membuat dan mengajukan knowledge tim sendiri; mencoba tim lain | Tim sendiri berhasil; tim lain ditolak. Ketua tim dan PIC menjadi reviewer satu sama lain, bukan atas unggahan sendiri | `sim.lead.psun`, `sim.owner.ppsun` |
| UAT-14 | Tujuh tim | Peserta tiap tim membuka daftar, pencarian, dashboard, dan Hermes | Hanya data timnya dan konten direktorat terbit; pengguna SUN_TEMATIK tanpa data tim lain. PLANNED, memerlukan pengguna simulasi tambahan | Pengguna per tim (usulan) |
| UAT-15 | Semua | Membuka `/dashboard` | Indikator yield dan kepemilikan SBN tidak berangka; tampil "sumber data belum tersedia". PLANNED, teks belum ada | Semua |
| UAT-16 | system_admin / administrator server | Latihan backup dan restore serta pemeriksaan paparan di server pilot | Restore berhasil; hanya port web atau proxy terjangkau. PLANNED, server belum ada (OQ-23) | `sim.admin` |

- **OPEN QUESTION**: Skenario untuk SUN Tematik tidak disusun karena fungsinya belum dikonfirmasi (OQ-01).
- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: Knowledge owner dan reviewer pada setiap tim adalah ketua tim dan PIC yang ditunjuk (OQ-09); penunjukan orangnya **OPEN QUESTION**. Alur persetujuan publikasi tetap **OPEN QUESTION** (OQ-12).
- **OPEN QUESTION**: Indikator dashboard yang benar-benar dibutuhkan (OQ-10).

## Kriteria Penerimaan (PROPOSED)

- Seluruh skenario prioritas P0 MVP berstatus Lulus atau Lulus dengan catatan (sumber prioritas: Proposal v2.4, slide 11).
- Tidak ada bug P0 terbuka; bug P1 terbuka hanya dengan keputusan tertulis mentor.
- Seluruh skenario wajib keamanan sudah diuji (lihat [security-testing.md](security-testing.md)).

## Sign-off

- **PROPOSED**: Sign-off UAT dilakukan oleh mentor Dit. SUN. Pejabat lain yang ikut menandatangani belum ditetapkan (OPEN QUESTION).
- **PROPOSED**: Dokumen sign-off mencatat versi aplikasi, tanggal, daftar skenario dan hasilnya, bug terbuka, serta keputusan (diterima, diterima dengan syarat, ditolak).

## Formulir Umpan Balik (PROPOSED)

| Field | Keterangan |
|---|---|
| ID skenario | Mis. UAT-05 |
| Tanggal dan waktu | Waktu pengujian |
| Role peserta | Role uji, bukan nama atau jabatan |
| Halaman atau fitur | Mis. `/hermes` |
| Langkah yang dilakukan | Urutan langkah ringkas |
| Hasil yang diharapkan | Dari tabel skenario |
| Hasil aktual | Yang terjadi |
| Status | Lulus, Lulus dengan catatan, Gagal |
| Usulan severity | P0, P1, P2, P3 |
| Request ID | Nilai `X-Request-ID` atau `requestId` bila ada error |
| Kemudahan penggunaan | Skala 1–5 |
| Catatan dan saran | Teks bebas, tanpa data asli atau data pribadi |

## Related Documents

- [test-strategy.md](test-strategy.md)
- [bug-severity.md](bug-severity.md)
- [user-personas.md](../01-product/user-personas.md)
- [acceptance-criteria.md](../01-product/acceptance-criteria.md)
- [open-questions.md](../00-project/open-questions.md)
