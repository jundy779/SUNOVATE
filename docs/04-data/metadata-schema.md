# Metadata Schema

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-06

## Purpose
Mendefinisikan metadata wajib dan opsional untuk knowledge entry dan dokumen.

## Knowledge entry
| Field (API) | Wajib | Nilai | Catatan |
|---|---|---|---|
| `title` | Ya | 5 sampai 255 karakter | |
| `knowledgeType` | Ya | REGULATION, POLICY, STUDY, SOP, PLAYBOOK, REPORT, MEETING_MATERIAL, CLOSE_OUT_NOTE, LESSON_LEARNED, TACIT_KNOWLEDGE, DECISION_RECORD, ARCHIVE, REFERENCE, OTHER | PROPOSED |
| `summary` | Ya | 10 sampai 2000 karakter | |
| `classificationCode` | Ya | PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL | tidak boleh melebihi clearance pembuat |
| `ownerTeamId` | Ya | UUID tim dalam scope pembuat | |
| `sharingScope` | Tidak | TEAM (default), DIRECTORATE | DIRECTORATE berlaku hanya saat PUBLISHED |
| `tags` | Tidak | maks. 20, masing-masing 1 sampai 48 karakter | |
| `lifecycleStatus` | Sistem | diatur oleh alur submit dan approval | tidak dapat diubah langsung |
| `versionLabel`, `effectiveDate`, `expiresAt`, `sourceNote`, `supersededById` | Opsional | | `effectiveDate` wajib untuk REGULATION (PROPOSED, belum ditegakkan); untuk REGULATION nilainya diturunkan dari tanggal pengundangan dengan tinjauan manusia (lihat "Metadata regulasi") |

## Dokumen dan versi
| Field | Wajib | Catatan |
|---|---|---|
| `provider` | Ya | `LOCAL_REFERENCE` pada pengembangan |
| `providerLocation` | Ya | hanya `local://...` pada pengembangan |
| `versionLabel` | Ya | 1 sampai 64 karakter |
| `checksumSha256` | Ya | 64 hex huruf kecil; duplikat per dokumen ditolak |
| `sizeBytes` | Tidak | >= 0 |
| `extractionStatus` | Sistem | versi baru hasil registrasi tetap `PENDING`; draf simulasi yang berhasil dibagi memakai `EXTRACTED`. Preview yang ditolak mengembalikan `FAILED`/`QUARANTINED` pada respons dan audit tanpa membuat versi dokumen |

## Metadata regulasi (PROPOSED)

Daftar awal (nomor, jenis peraturan, tanggal penetapan, tanggal berlaku, status berlaku, relasi) tidak cukup. Telaah Kompilasi Peraturan SUN menunjukkan kolom tambahan di bawah. Kolom ini **PROPOSED**: belum ada di skema `0001_initial_schema` dan `0002_ordering_columns`, dan menambahnya memerlukan revisi Alembic baru di masa depan (tidak dikerjakan di sini; `0001` dan `0002` tidak diubah). Kolom "Bukti" menunjukkan apa yang **CONFIRMED** ada pada naskah kompilasi (format: `Kompilasi Peraturan SUN, <regulasi>, <bagian>, hal. N`, hal. = halaman PDF 1 sampai 199).

| Kolom usulan | Bukti dari naskah kompilasi | Catatan |
|---|---|---|
| `jenis` | Kompilasi memuat satu UU, satu PP, dan delapan PMK (indeks, hal. 2). Perpres, Keppres, dan peraturan lain hanya muncul sebagai rujukan. | Rujukan ke jenis lain disimpan sebagai target relasi, bukan entri |
| `nomor_lengkap`, `nomor`, `kode_unit`, `tahun` | Format bervariasi: "Nomor 24 Tahun 2002" pada UU (indeks, hal. 2) dan "128/PMK.08/2012" pada kepala naskah (hal. 168) | Simpan `nomor_lengkap` sebagai teks. Jangan menyusun ulang kode unit yang tidak terlihat di teks. Kunci unik memuat tahun dan kode unit, karena PMK 168/PMK.08/2019 (lelang, hal. 140-167) berbeda dari PMK 168/PMK.08/2021 (disebut PMK 111/2024, Pasal 30 angka 2, hal. 47) |
| `judul` dan `judul_indeks` | Indeks hal. 2 tidak memuat judul untuk beberapa PMK; judul berasal dari kepala naskah. Judul PMK 165/2022 pada naskah (hal. 49) berbeda dari indeks (hal. 2) | `judul` diambil dari kepala naskah; `judul_indeks` disimpan hanya bila berbeda. Judul resmi: **NEEDS LEGAL CONFIRMATION** (OQ-27) |
| `tanggal_penetapan`, `tanggal_pengundangan` (dua kolom) | Naskah menulis "Ditetapkan di Jakarta" dan "Diundangkan di Jakarta" terpisah; kedua tanggal dapat berbeda hari (contoh: PMK 27/2020, hal. 197) | Dua kolom, bukan satu |
| `register_jenis`, `register_nomor` | Lembaran Negara dan Tambahan Lembaran Negara pada UU; Berita Negara pada PMK (contoh: PMK 128/PMK.08/2012, hal. 168) | PMK 111/2024: tanggal pengundangan dan nomor Berita Negara tidak terbaca (hal. 48). Biarkan kosong dengan penanda **NEEDS LEGAL CONFIRMATION** (OQ-28) |
| `klausul_mulai_berlaku` dan `effectiveDate` (turunan) | Semua 10 regulasi menyatakan mulai berlaku pada tanggal diundangkan (contoh: UU 24/2002, Pasal 22, hal. 10; PP 76/2005, Pasal 17, hal. 28; PMK 111/2024, Pasal 31, hal. 47; PMK 128/PMK.08/2012, Pasal 17, hal. 175) | Simpan teks klausul beserta Pasalnya, lalu turunkan `effectiveDate` dari `tanggal_pengundangan` dengan tinjauan manusia. Pencabutan atau perubahan setelahnya tidak tercakup: **OPEN QUESTION** |
| `ada_penjelasan` | Penjelasan hanya ada pada UU 24/2002 (hal. 11-20) dan PP 76/2005 (hal. 29-33); delapan PMK tidak memuat Penjelasan di kompilasi | Menentukan pipeline chunking ([chunking-strategy](../05-ai-rag/chunking-strategy.md)) |
| `ada_lampiran` | Lampiran ada pada PMK 51/2019, PMK 215/2019, PMK 114/2023, PMK 168/2019, dan PMK 27/2020; tidak ada pada UU dan PP | Lampiran adalah bagian tidak terpisahkan dari peraturan (contoh: PMK 51/2019, Pasal 6 ayat (4), hal. 68) |
| `pejabat_penetap` | Jabatan penanda tangan tercantum pada bagian penetapan (contoh: PMK 128/PMK.08/2012, hal. 175) | Simpan jabatan, bukan nama orang, kecuali ada persetujuan |
| `rentang_halaman_pdf` | Setiap regulasi menempati rentang halaman PDF yang berurutan (3 sampai 199 untuk 10 regulasi) | Halaman PDF dan nomor cetak peraturan disimpan terpisah; nomor cetak berbeda dari halaman PDF (contoh: halaman PDF 4 UU 24/2002 memuat "- 2 -") |
| `teks_butuh_verifikasi`, `catatan_kualitas_teks` | Ekstraksi teks mencatat galat OCR, mis. "PMK.OS" untuk "PMK.08" dan nomor PMK 27/2020 yang terbaca rusak (kepala naskah, hal. 176) | Tandai sampai teks dibandingkan dengan PDF atau sumber resmi (OQ-32) |
| `status_dinyatakan_teks` | Kompilasi tidak menyatakan status berlaku saat ini untuk regulasi mana pun. Yang ada hanya pernyataan relasional antarteks (contoh: PMK 111/2024, Pasal 30, hal. 47) | Lihat "Status hukum" di bawah |
| `relations[]` | Jenis yang terbukti ada di teks: `REFERENCES`, `REVOKES`, `SUPERSEDES` (dari konsiderans Menimbang), dan satu `IMPLEMENTS` (PP 76/2005 terhadap UU 24/2002, Pasal 18, hal. 21). Tidak ada contoh `AMENDS` antarnaskah di dalam kompilasi | Desain kolom cakupan dan dasar relasi ada di [logical-data-model](logical-data-model.md) |

### Status hukum

- **PROPOSED**: Status berlaku saat ini tidak pernah diturunkan sistem dari teks regulasi atau dari ketiadaan relasi. Status hukum ditentukan pemilik konten, bukan sistem (OQ-09, OQ-26, BR-40). `status_dinyatakan_teks` hanya memuat apa yang dinyatakan teks lain di dalam repository.
- **OPEN QUESTION**: Status berlaku PMK 128/PMK.08/2012 dan apakah "PMK 128 tahun 2019" salah ketik atau regulasi lain (OQ-17). Kompilasi hanya menyatakan penggantian tanpa alasan (catatan sampul, hal. 1).
## Asal Data dan Metadata Intake (jawaban knowledge owner)

- **CONFIRMED (implementasi)**: Setiap record membawa `data_origin` dengan nilai `SIMULATED_DATA`, `USER_ENTERED`, atau `INTEGRATION` (CHECK pada model). Seed memakai `SIMULATED_DATA`; record yang dibuat lewat API memakai `USER_ENTERED`.
- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: Dokumen yang boleh masuk adalah "semua dokumen yang diusulkan tim kerja" (OQ-04). Metadata wajib di atas, terutama `classificationCode` dan `ownerTeamId`, tetap harus terisi; klasifikasi tidak boleh melebihi clearance pembuat.
- **PROPOSED**: Dokumen asli hanya boleh dimuat setelah klasifikasi resmi ditetapkan (OQ-05) dan persetujuan eksplisit tercatat (FR-53, BR-35). Nilai `USER_ENTERED` saja tidak membuktikan bahwa isi record bukan data asli; gerbang intake belum ada.
- **OPEN QUESTION**: Tempat mencatat persetujuan intake per dokumen (memakai `approval_requests` yang ada, tipe baru lewat migrasi, atau catatan di luar sistem). Tidak ada field baru yang diusulkan atau ditambahkan di sini.
- **PROPOSED**: Pemilik metadata adalah ketua tim dan PIC yang ditunjuk per tim (OQ-09). Pencatatan penunjukan dibahas di [logical-data-model.md](logical-data-model.md).

## Open Questions
OQ-04 jenis dokumen yang boleh masuk (PARTIAL: cakupan dijawab, syarat masuk belum); OQ-05 klasifikasi per jenis (PARTIAL: hanya siapa yang boleh mengubah/mengunggah dijawab); OQ-09 pemilik metadata (ANSWERED, knowledge owner: ketua tim dan PIC yang ditunjuk; penunjukan orang dan role di OQ-25). Metadata regulasi: OQ-17 (status PMK 128), OQ-26 (status berlaku terkini), OQ-27 (sumber acuan judul dan nomor), OQ-28 (pengundangan PMK 111/2024), OQ-30 (rujukan tak bernomor), OQ-32 (validasi teks ekstraksi).

## Related Documents
- [document-classification.md](document-classification.md)
- [data-quality.md](data-quality.md)
- [document-lifecycle.md](../02-business/document-lifecycle.md)
- [logical-data-model.md](logical-data-model.md)
- [citation-policy.md](../05-ai-rag/citation-policy.md)
