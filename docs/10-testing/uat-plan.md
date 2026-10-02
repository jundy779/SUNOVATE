# Rencana User Acceptance Test (UAT)

**Status:** NEEDS MENTOR VALIDATION

**Last Updated:** 2026-10-01

## Purpose

Menyusun kerangka UAT SUNOVATE: skenario per persona, peserta, lingkungan, sign-off, dan formulir umpan balik.

## Status

- **PROPOSED**: UAT direncanakan pada Bulan 6 (Implementasi) bersama security test, bug fixing, dokumentasi, dan handover (sumber: Proposal v2.4, slide 21).
- **OPEN QUESTION**: Peserta UAT dan pengguna uji yang ditunjuk (OQ-20).
- **OPEN QUESTION**: Lingkungan UAT (OQ-20) dan hosting (OQ-07).
- **OPEN QUESTION**: Tim kerja dan proses yang menjadi pilot pertama (OQ-03).

## Prinsip

- **CONFIRMED**: UAT memakai data `SIMULATED_DATA` saja; data internal atau data keuangan asli tidak dipakai (sumber: brief sesi 2026-10-01, AGENTS.md).
- **PROPOSED**: Peserta memakai akun uji yang dipetakan ke role pengembangan; role adalah usulan dan bukan jabatan resmi (sumber: brief sesi 2026-10-01).
- **PROPOSED**: Setiap skenario dinilai Lulus, Lulus dengan catatan, atau Gagal; temuan dicatat di register bug dengan severity P0–P3.

## Skenario per Persona (PROPOSED)

Persona dan role mengikuti role pengembangan usulan. Pengguna simulasi di kolom terakhir dipakai bila peserta belum ditunjuk.

| ID | Persona (role) | Skenario | Hasil yang diharapkan | Pengguna simulasi |
|---|---|---|---|---|
| UAT-01 | staff | Membuat draft knowledge lalu mengajukan review | Status `IN_REVIEW`, tercatat di audit | `sim.staff.pppsun` |
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

- **OPEN QUESTION**: Skenario untuk SUN Tematik tidak disusun karena fungsinya belum dikonfirmasi (OQ-01).
- **OPEN QUESTION**: Siapa knowledge owner dan reviewer pada setiap tim (OQ-09) dan alur persetujuan publikasi (OQ-12).
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
