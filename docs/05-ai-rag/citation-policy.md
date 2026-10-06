# Citation Policy

**Status:** PROPOSED
**Last Updated:** 2026-10-06

## Purpose

Menetapkan aturan sitasi jawaban Hermes agar setiap pernyataan dapat ditelusuri ke sumber yang boleh dibaca pengguna.

## Confirmed Information

- **CONFIRMED** Hermes dengan sitasi termasuk prioritas P0 MVP (sumber: Proposal v2.4, slide 11; status usulan).
- **CONFIRMED** Sitasi keliru termasuk skenario uji wajib (sumber: Proposal v2.4, slide 20).
- **CONFIRMED** `CitationValidator` pada scaffold memeriksa bahwa setiap penanda `[n]` merujuk ke chunk yang diambil dan diotorisasi, dengan minimal satu sitasi (sumber: fact sheet bagian 9).

## Aturan sitasi

1. **PROPOSED** Setiap kalimat faktual dalam jawaban wajib diakhiri penanda sitasi `[n]`. Kalimat penghubung atau penjelasan batas jawaban (mis. "Sumber yang tersedia tidak membahas hal X") tidak memerlukan sitasi.
2. **IMPLEMENTED** Setiap `[n]` harus memetakan ke chunk yang benar-benar diambil oleh `RetrievalService` untuk permintaan tersebut dan lolos otorisasi.
3. **IMPLEMENTED** Jawaban harus memiliki minimal satu sitasi valid.
4. **IMPLEMENTED** Jika aturan 2 atau 3 gagal, jawaban tidak ditampilkan dan decision menjadi `INSUFFICIENT_EVIDENCE`.
5. **PROPOSED** Penanda yang merujuk ke nomor yang tidak ada, ke chunk yang tidak diambil, atau ke chunk di luar hak akses diperlakukan sebagai kegagalan validasi, bukan dihapus diam-diam.
6. **PROPOSED** Satu kalimat boleh memiliki lebih dari satu sitasi, mis. `[1][3]`.
7. **PROPOSED** Hermes tidak boleh mengutip dokumen yang tidak ada dalam konteks, termasuk dari pengetahuan umum model.

## Informasi yang ditampilkan per sitasi

| Elemen | Sumber data | Status |
|---|---|---|
| Nomor sitasi `[n]` | Urutan chunk dalam konteks | IMPLEMENTED |
| Judul knowledge atau dokumen | `knowledge_entries`, `document_references` | PROPOSED tampilan lengkap |
| Versi dokumen | `document_versions` | PROPOSED |
| Label bagian (Pasal, ayat, langkah, bagian) | Metadata chunk, lihat [chunking-strategy.md](./chunking-strategy.md) | PROPOSED |
| Rentang halaman | Metadata chunk | PROPOSED |
| Klasifikasi | `classification_code` | PROPOSED |
| Tautan ke halaman detail knowledge | Route `/knowledge/[id]` | PROPOSED |

Tautan detail tetap melewati otorisasi API; sitasi tidak memberikan akses tambahan. Sitasi disimpan di `ai_citations` pada desain PostgreSQL; pada scaffold data berada di simulated store.

## Status regulasi pada sitasi (PROPOSED)

Untuk knowledge berjenis REGULATION, sitasi menampilkan status berlaku:

| Tampilan | Dasar |
|---|---|
| Berlaku | Tidak ada relasi `REVOKES` atau `SUPERSEDES` yang mengarah ke regulasi tersebut, dan status knowledge PUBLISHED. Ini bukan bukti bahwa regulasi berlaku; lihat catatan di bawah tabel |
| Diubah | Ada relasi `AMENDS` yang mengarah ke regulasi tersebut; tampilkan regulasi pengubah |
| Dicabut atau digantikan | Ada relasi `REVOKES` atau `SUPERSEDES` yang mencakup seluruh regulasi, atau status knowledge SUPERSEDED. Pencabutan sebagian ditangani oleh catatan di bawah tabel |

- **PROPOSED** Bila sitasi menunjuk regulasi yang dicabut atau digantikan, jawaban wajib menyebutkannya secara eksplisit dan menampilkan regulasi penggantinya bila tersedia di konteks terotorisasi.
- **OPEN QUESTION** Penetapan status hukum suatu regulasi pada repository memerlukan validasi pemilik konten (OQ-09, OQ-26). Status berlaku saat ini tidak dapat diturunkan dari kompilasi: kompilasi tidak menyatakan status berlaku saat ini untuk regulasi mana pun (sumber: telaah Kompilasi Peraturan SUN, 2026-10-06).
- **PROPOSED** Tampilan "Berlaku" hanya berarti tidak ada pencabutan yang tercatat di repository. Selama pemilik konten belum memvalidasi, sitasi menyertakan keterangan "status berlaku belum diverifikasi". Ketiadaan relasi tidak membuktikan regulasi berlaku; contoh: PMK 128/PMK.08/2012 tidak memiliki relasi dengan regulasi lain di kompilasi, tetapi status berlakunya tidak diketahui (BR-40).
- **PROPOSED** Pencabutan sebagian tidak diperlakukan sebagai pencabutan seluruh regulasi. Sitasi menampilkan "Dicabut sebagian (Pasal/ayat ...)" dengan cakupan dari relasi. Contoh CONFIRMED: PMK 111/2024 mencabut ketentuan tertentu pada PMK 168/2019, PMK 165/2022, dan PMK 114/2023 (sumber: Kompilasi Peraturan SUN, PMK 111/2024, Pasal 30 angka 2 sampai 4, hal. 47). Ketentuan peralihan (contoh: PMK 168/2019, Pasal 28, hal. 154-155) tidak menurunkan status menjadi "dicabut" dan tidak menjadi bukti "berlaku". Status akhir: **NEEDS LEGAL CONFIRMATION** (OQ-29).
- **OPEN QUESTION** PMK 128/PMK.08/2012 (penjualan SUN dalam valuta asing di pasar perdana domestik dengan cara bookbuilding, hal. 168-175) adalah regulasi yang dimuat kompilasi sebagai pengganti "PMK 128 tahun 2019". Kompilasi tidak menjelaskan penggantian itu (catatan sampul, hal. 1). Hermes tidak boleh menyajikan "PMK 128 tahun 2019" sebagai regulasi yang ada; status penggunaan adalah OQ-17.
- **CONFIRMED** Relasi yang tersedia: AMENDS, REVOKES, IMPLEMENTS, REFERENCES, SUPERSEDES (sumber: fact sheet bagian 6).

## Format sitasi regulasi (PROPOSED)

- **PROPOSED** Label bagian untuk knowledge berjenis REGULATION memuat regulasi, Pasal, ayat bila ada, dan halaman: `<regulasi>, Pasal X ayat (Y), hal. N`. Contoh untuk kompilasi: `Kompilasi Peraturan SUN, UU 24/2002, Pasal 3 ayat (2), hal. 5`. Contoh ini hanya ilustrasi format.
- **PROPOSED** `hal.` adalah nomor halaman PDF berkas, bukan nomor cetak peraturan (halaman PDF 4 UU 24/2002 memuat nomor cetak "- 2 -"). Nomor cetak disimpan terpisah bila perlu agar sitasi tidak ambigu.
- **PROPOSED** Penjelasan dan Lampiran disitasi dengan penanda sendiri (mis. `Penjelasan Pasal X` atau `Lampiran A`) karena bukan bagian batang tubuh. Penjelasan hanya ada untuk UU 24/2002 dan PP 76/2005 pada kompilasi.
- **PROPOSED** Chunk regulasi yang teksnya belum divalidasi terhadap PDF atau sumber resmi diberi penanda "teks butuh verifikasi". Kebijakan apakah Hermes boleh mengutipnya adalah OQ-32.

## Contoh format (SIMULATED_DATA)

```text
Pertanyaan: Apa ruang lingkup dokumen SOP simulasi X?
Jawaban: Dokumen SOP simulasi X mengatur tahapan penyusunan bahan rapat internal [1].
Tahapan review dilakukan sebelum bahan didistribusikan [1][2].

[1] SOP Simulasi X, versi 2, Langkah 1-3, hlm. 2-3, INTERNAL
[2] Playbook Simulasi Y, versi 1, Bagian Review, hlm. 5, INTERNAL
```

Contoh di atas fiktif dan hanya menunjukkan format.

## Risks

- R-04 Jawaban AI dianggap fakta/keputusan.
- R-02 Kebocoran data melalui sitasi.
- R-11 Metadata buruk sehingga sitasi kurang informatif.
- R-18 Status berlaku regulasi tidak dapat diturunkan dari kompilasi sehingga "Berlaku" dapat menyesatkan.

## Acceptance Criteria

- Tidak ada jawaban `ANSWERED` tanpa sitasi valid.
- Tidak ada sitasi yang merujuk ke chunk di luar hak akses pengguna.
- Sitasi regulasi yang dicabut atau digantikan ditandai dengan jelas.

## Related Documents

- [hermes-overview.md](./hermes-overview.md)
- [retrieval-strategy.md](./retrieval-strategy.md)
- [prompt-policy.md](./prompt-policy.md)
- [rag-evaluation.md](./rag-evaluation.md)
