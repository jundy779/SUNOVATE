# User Stories

**Status:** PROPOSED
**Last Updated:** 2026-10-02

## Purpose

Dokumen ini memuat user story SUNOVATE yang dikelompokkan per epic. Semua story **PROPOSED**. Prioritas mengikuti Proposal v2.4, slide 11 (P0 MVP, P1, P2). Petunjuk penerimaan bersifat ringkas; skenario Given/When/Then rinci ada di [acceptance-criteria.md](acceptance-criteria.md), dan requirement terkait di [functional-requirements.md](functional-requirements.md).

Format: "Sebagai [persona], saya ingin [kebutuhan], agar [manfaat]." Persona merujuk [user-personas.md](user-personas.md).

## Epic 1: Akses

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-01 | Sebagai pengguna simulasi, saya ingin masuk dengan akun pengembangan, agar dapat mencoba fitur sesuai peran. | `POST /api/v1/auth/dev/login` mengembalikan token; endpoint mengembalikan 404 `DEV_AUTH_DISABLED` di luar development. | P0 |
| US-02 | Sebagai pengguna, saya ingin melihat profil, tim, peran, dan clearance saya, agar paham batas akses saya. | `GET /api/v1/auth/me` mengembalikan data principal. | P0 |
| US-03 | Sebagai pengguna, saya ingin ditolak dengan jelas ketika membuka fitur tanpa izin, agar tidak bingung. | API mengembalikan 403 `PERMISSION_DENIED`; UI mengarahkan ke `/unauthorized`. | P0 |
| US-04 | Sebagai pemilik data, saya ingin record yang tidak boleh dibaca orang lain tidak terlihat sama sekali, agar keberadaannya tidak bocor. | Record di luar scope atau di atas clearance menghasilkan 404, bukan 403. | P0 |

## Epic 2: Knowledge Hub

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-05 | Sebagai anggota tim, saya ingin membuat knowledge entry berstatus DRAFT, agar pengetahuan dapat mulai didokumentasikan. | `POST /knowledge` membuat entri dengan `revision` 1 dan entri audit CREATE. | P0 |
| US-06 | Sebagai pemilik knowledge, saya ingin memperbarui draf tanpa menimpa perubahan orang lain, agar data tetap konsisten. | `PATCH /knowledge/{id}` dengan revision basi menghasilkan 409 `REVISION_CONFLICT`. | P0 |
| US-07 | Sebagai pemilik knowledge, saya ingin mengajukan draf untuk review, agar dapat dipublikasikan. | `POST /knowledge/{id}/submit` mengubah status ke IN_REVIEW dan mencatat audit SUBMIT; publikasi hanya terjadi melalui approval request `KNOWLEDGE_PUBLICATION` yang disetujui. | P0 |
| US-08 | Sebagai peninjau, saya ingin menyetujui atau menolak permintaan publikasi, agar hanya konten tervalidasi yang terbit. | `POST /approvals/{id}/decision`; pengaju tidak dapat memutuskan permintaannya sendiri. | P0 |
| US-09 | Sebagai pemilik knowledge, saya ingin mendaftarkan versi baru dokumen dengan checksum, agar riwayat versi terjaga. | `POST /documents/{id}/versions`; checksum ganda menghasilkan 409 `DUPLICATE_CHECKSUM`. | P0 |
| US-10 | Sebagai Pengelola Knowledge, saya ingin melihat relasi antarperaturan, agar tahu peraturan mana yang mengubah atau mencabut yang lain. | Relasi AMENDS, REVOKES, IMPLEMENTS, REFERENCES, SUPERSEDES tampil di detail regulasi. | P1 |
| US-11 | Sebagai SME, saya ingin template Close Out Note dan playbook, agar pengetahuan tacit tertangkap dengan format konsisten. | Template tersedia setelah disetujui (OQ-09, OQ-16). | P1 |

## Epic 3: Pencarian

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-12 | Sebagai anggota tim, saya ingin mencari dengan kata kunci, agar menemukan dokumen relevan dengan cepat. | `GET /search?q=` hanya mengembalikan konten PUBLISHED yang boleh dibaca. | P0 |
| US-13 | Sebagai anggota tim, saya ingin menyaring hasil berdasarkan tipe knowledge dan tim, agar hasil lebih fokus. | Usulan filter tipe dan tim; parameter filter belum menjadi bagian kontrak `GET /search` saat ini (lihat [endpoint-catalog.md](../07-api/endpoint-catalog.md)). | P0 |
| US-14 | Sebagai anggota tim, saya ingin pencarian semantik, agar pertanyaan dengan istilah berbeda tetap menemukan dokumen. | Aktif setelah model embedding disetujui (OQ-11). | P0, tertunda |

## Epic 4: Hermes

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-15 | Sebagai anggota tim, saya ingin bertanya ke Hermes tentang dokumen yang saya boleh akses, agar mendapat jawaban bersitasi. | Keputusan `ANSWERED` selalu memiliki minimal satu sitasi valid. | P0 |
| US-16 | Sebagai pengguna, saya ingin Hermes menyatakan bila bukti tidak cukup, agar tidak menerima jawaban karangan. | Keputusan `INSUFFICIENT_EVIDENCE` tanpa jawaban substantif. | P0 |
| US-17 | Sebagai pemilik data, saya ingin Hermes menolak pertanyaan di luar domain, coding umum, dan upaya jailbreak, agar tidak disalahgunakan. | Keputusan `REFUSED_OUT_OF_SCOPE`, `REFUSED_GENERAL_CODING`, atau `REFUSED_POLICY`. | P0 |
| US-18 | Sebagai pengguna, saya ingin permintaan aksi tulis lewat Hermes masuk ke persetujuan manusia, agar tidak ada perubahan otomatis. | Keputusan `REQUIRES_HUMAN_APPROVAL` dan approval request `HERMES_WRITE_ACTION` berstatus PENDING. | P0 |
| US-19 | Sebagai pengguna, saya ingin memberi umpan balik atas jawaban Hermes, agar kualitas dapat dievaluasi. | `POST /hermes/messages/{id}/feedback` dan entri audit AI_FEEDBACK. | P0 |

## Epic 5: Monitoring Kerja

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-20 | Sebagai ketua tim, saya ingin melihat work output, tugas, dan milestone tim, agar tahu kemajuan pekerjaan. | `GET /work-outputs`, `/tasks`, `/milestones` dibatasi team scope. | P0 |
| US-21 | Sebagai anggota tim, saya ingin memperbarui status tugas, agar kemajuan tercatat. | `PATCH /tasks/{id}` dengan kontrol revision. | P0 |
| US-22 | Sebagai ketua tim, saya ingin melihat pending matters dan follow-up, agar tidak ada hal yang terlewat. | `GET /pending-matters`, `/follow-ups`. | P0 |
| US-23 | Sebagai pengguna, saya ingin status tenggat dihitung konsisten, agar tidak ada perbedaan antar tampilan. | Status SAFE, DUE_SOON, DUE_TODAY, OVERDUE, COMPLETED hanya dihitung backend. | P0 |

## Epic 6: Dashboard

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-24 | Sebagai pengguna, saya ingin dashboard ringkas sesuai hak akses, agar melihat gambaran pekerjaan dan knowledge. | `GET /dashboard/summary` hanya menghitung record yang boleh dibaca. | P0 |
| US-25 | Sebagai Pimpinan, saya ingin laporan yang dapat diekspor, agar dapat dipakai dalam rapat. | Format menunggu OQ-10. | P1 |

## Epic 7: Administrasi dan Audit

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-26 | Sebagai auditor, saya ingin membaca audit log, agar aktivitas dapat ditelusuri. | `GET /audit-logs` memerlukan `audit:read`; log tidak dapat diubah atau dihapus. | P0 |
| US-27 | Sebagai administrator, saya ingin melihat daftar pengguna, tim, peran, izin, dan klasifikasi, agar konfigurasi dapat diperiksa. | `GET /users`, `/teams`, `/roles`, `/permissions`, `/classifications`. | P0 |
| US-28 | Sebagai administrator, saya ingin melihat status provider, agar jelas integrasi mana yang aktif. | `GET /providers` menunjukkan provider produksi nonaktif. | P0 |
| US-29 | Sebagai Pengelola Knowledge, saya ingin melihat data quality issue, agar metadata dapat diperbaiki. | `GET /data-quality-issues` memerlukan `data_quality:read`. | P0 |
| US-30 | Sebagai pengguna, saya ingin notifikasi dalam aplikasi untuk review dan tenggat, agar tidak melewatkan tindakan. | Notifikasi in-app tanpa kanal eksternal. | P1 |

## Epic 8: Document Automation (P1)

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-31 | Sebagai anggota tim, saya ingin membuat draf dokumen dari template yang disetujui, agar penyusunan lebih cepat dan konsisten. | Hanya template berstatus disetujui yang dapat dipakai (OQ-16). | P1 |
| US-32 | Sebagai pemilik template, saya ingin hasil otomatis selalu ditinjau manusia, agar tidak ada dokumen terbit tanpa pemeriksaan. | Hasil berstatus draf dan masuk alur review. | P1 |

## Epic 9: Kanal Telegram/WhatsApp (P2)

**OUT OF SCOPE** untuk MVP. Story dicatat hanya agar abstraksi provider tetap memadai. OQ-08 sudah dijawab knowledge owner ("bisa"); pelaksanaan tetap P2 dan menunggu kajian keamanan.

| ID | Story | Petunjuk penerimaan | Prioritas |
|---|---|---|---|
| US-33 | Sebagai anggota tim, saya ingin menerima pengingat tenggat melalui kanal pesan yang disetujui instansi. | Hanya setelah kanal diizinkan dan provider divalidasi. | P2 |
| US-34 | Sebagai anggota tim, saya ingin bertanya ke Hermes melalui kanal pesan yang disetujui dengan otorisasi yang sama seperti web. | Otorisasi tetap melalui HermesGateway; tidak ada jalur pintas. | P2 |

## Story yang Tidak Dibuat

- **OPEN QUESTION** Story khusus SUN Tematik (OQ-01).
- **OUT OF SCOPE** Story terkait transaksi, lelang, yield, atau setelmen SUN (ADR-013).

## Related Documents

- [prd.md](prd.md)
- [functional-requirements.md](functional-requirements.md)
- [acceptance-criteria.md](acceptance-criteria.md)

## Last Updated

2026-10-02
