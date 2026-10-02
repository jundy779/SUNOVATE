# Persona Pengguna

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Persona membantu menjaga keputusan desain tetap berpusat pada kebutuhan pengguna. Semua persona di dokumen ini **PROPOSED** dan fiktif. Persona tidak mewakili orang tertentu, tidak memakai nama, dan tidak mencantumkan jabatan di luar kelompok pengguna pada Proposal v2.4, slide 9. Kebutuhan dan hambatan adalah dugaan pengembang yang perlu divalidasi melalui wawancara atau UAT (OQ-03, OQ-20).

## Ringkasan

| ID | Persona | Kelompok pengguna | Peran pengembangan (PROPOSED) | Pengguna simulasi contoh |
|---|---|---|---|---|
| P-01 | Pimpinan | Pimpinan | Belum dipetakan (OPEN QUESTION) | Tidak ada |
| P-02 | Anggota tim kerja | Enam tim kerja dan SME | staff | `sim.staff.pppsun` |
| P-03 | SME / pemilik knowledge | Enam tim kerja dan SME | knowledge_owner | `sim.owner.ppsun` |
| P-04 | Ketua tim kerja | Enam tim kerja dan SME | team_lead | `sim.lead.psun` |
| P-05 | Peninjau | Enam tim kerja dan SME | reviewer | `sim.reviewer.akpsun` |
| P-06 | Pengelola Knowledge | Pengelola Knowledge | knowledge_coordinator | `sim.coordinator` |
| P-07 | Auditor | Auditor / Admin | auditor | `sim.auditor` |
| P-08 | Administrator sistem | Auditor / Admin | system_admin | `sim.admin` |
| P-09 | Pembaca | Enam tim kerja dan SME | read_only | `sim.readonly.dhtv` |

Pengguna simulasi berdomain `@sunovate.local` dan seluruhnya fiktif (`SIMULATED_DATA`).

## P-01 Pimpinan

- **Tujuan:** melihat ringkasan pekerjaan, output, dan pending matters tim yang menjadi kewenangannya.
- **Kebutuhan:** dashboard ringkas, status tenggat yang jelas, akses cepat ke dokumen pendukung.
- **Hambatan dugaan:** informasi tersebar; laporan disusun manual.
- **Batasan:** cakupan data dan peran sistem untuk persona ini belum ditetapkan (OQ-10). Dashboard tidak memberi rekomendasi keputusan keuangan.

## P-02 Anggota Tim Kerja

- **Tujuan:** menemukan regulasi, SOP, playbook, dan bahan rapat dengan cepat; memperbarui tugas sendiri.
- **Kebutuhan:** pencarian yang memahami istilah domain SUN, Hermes dengan sitasi, daftar tugas dengan tenggat.
- **Hambatan dugaan:** tidak tahu dokumen mana versi terbaru; tidak tahu tim mana pemilik dokumen.
- **Hak contoh:** membuat dan mengajukan knowledge, memperbarui tugas, bertanya ke Hermes.

## P-03 SME / Pemilik Knowledge

- **Tujuan:** mendokumentasikan pengetahuan tacit, Close Out Note, dan playbook agar tidak hilang saat rotasi.
- **Kebutuhan:** formulir knowledge yang ringkas, registrasi versi dokumen, notifikasi status review.
- **Hambatan dugaan:** waktu terbatas untuk mendokumentasikan.
- **Hak contoh:** membuat, memperbarui, mengajukan knowledge; mendaftarkan versi dokumen. Tidak dapat mempublikasikan sendiri.

## P-04 Ketua Tim Kerja

- **Tujuan:** memantau work output, tugas, milestone, dan pending matters tim; meninjau knowledge tim.
- **Kebutuhan:** tampilan per tim, status tenggat, persetujuan atas permintaan anggota tim.
- **Batasan:** apakah team_lead boleh mempublikasikan knowledge adalah OPEN QUESTION (OQ-12).

## P-05 Peninjau

- **Tujuan:** meninjau knowledge sebelum publikasi dan memberi permintaan perubahan.
- **Kebutuhan:** antrean review, perbandingan versi, alasan penolakan yang tercatat.
- **Batasan:** tidak dapat memutuskan permintaan yang ia ajukan sendiri (separation of duties).

## P-06 Pengelola Knowledge

- **Tujuan:** menjaga kualitas dan konsistensi repository lintas tim; memutuskan publikasi melalui approval.
- **Kebutuhan:** daftar data quality issue, metadata wajib, akses lintas tim (`scope:all_teams`) yang tetap tunduk pada klasifikasi.
- **Hambatan dugaan:** metadata tidak lengkap menurunkan kualitas retrieval (R-11).

## P-07 Auditor

- **Tujuan:** menelusuri siapa melakukan apa dan kapan, termasuk akses yang ditolak dan pertanyaan ke Hermes.
- **Kebutuhan:** audit log yang tidak dapat diubah, filter berdasarkan aksi dan waktu.
- **Batasan:** hanya membaca; tidak membuat atau memutuskan konten.

## P-08 Administrator Sistem

- **Tujuan:** mengelola pengguna, tim, peran, dan melihat status provider.
- **Kebutuhan:** tampilan konfigurasi provider yang menunjukkan provider produksi nonaktif.
- **Batasan:** apakah administrator boleh membaca isi konten adalah OPEN QUESTION. Clearance contoh hanya INTERNAL.

## P-09 Pembaca

- **Tujuan:** membaca dan mencari konten yang diizinkan, bertanya ke Hermes.
- **Batasan:** tidak membuat atau mengubah data.

## Persona yang Tidak Dibuat

- **OPEN QUESTION** Persona khusus SUN Tematik tidak dibuat karena fungsinya belum diketahui (OQ-01).
- **PROPOSED** Persona pengguna eksternal (Dealer Utama, investor, publik) tidak dibuat karena SUNOVATE dirancang untuk tim kerja Dit. SUN; perlu dikonfirmasi mentor.

## Related Documents

- [stakeholder-map.md](../00-project/stakeholder-map.md)
- [user-stories.md](user-stories.md)
- [permission-matrix.md](../06-security/permission-matrix.md)

## Last Updated

2026-10-01
