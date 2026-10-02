# Gambaran Domain Surat Utang Negara (SUN)

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini memberi latar belakang domain SUN bagi pengembang SUNOVATE agar istilah pada metadata, taksonomi knowledge, dan pertanyaan Hermes dapat dipahami. Isi dibatasi pada fakta yang tercantum pada dokumen sumber di root workspace. Dokumen ini bukan rujukan hukum; rujukan resmi tetap peraturan perundang-undangan dan dokumen Dit. SUN.

## Batasan Penting

- **CONFIRMED**: SUNOVATE tidak menggantikan sistem transaksi SUN resmi, tidak mengambil keputusan keuangan, dan tidak memberikan akses dokumen tanpa otorisasi (sumber: brief sesi 2026-10-01).
- **CONFIRMED**: Proses yang dijelaskan di bawah (penerbitan, pembelian kembali, debt switch, penatausahaan) tidak dieksekusi, dihitung, atau diputuskan oleh SUNOVATE. SUNOVATE hanya menyimpan, mengorganisasikan, dan menemukan kembali knowledge tentang proses tersebut (sumber: brief sesi 2026-10-01).
- **CONFIRMED**: Tabel bisnis SUN yang belum tervalidasi (instrumen, lelang, transaksi, yield, setelmen) telah dihapus dari skema; area SUN Business tetap OPEN QUESTION untuk fase berikutnya (sumber: ADR-013, keputusan sesi 2026-10-01).
- **OUT OF SCOPE**: Angka APBN, kebutuhan pembiayaan, yield, hasil lelang, atau data pasar apa pun. Dokumen ini dan data contoh SUNOVATE tidak memuat angka riil.

## Confirmed Information

### Definisi SUN

- **CONFIRMED**: Definisi SUN mengacu pada Pasal 1 Undang-Undang Nomor 24 Tahun 2002 tentang Surat Utang Negara, yaitu surat berharga berupa surat pengakuan utang dalam mata uang rupiah maupun valuta asing yang dijamin pembayaran bunga dan pokoknya oleh Negara Republik Indonesia sesuai masa berlakunya (sumber: Pengayaan_Kelas_Magang_6_Mei_2026.pdf; Kompilasi_Peraturan_SUN_formal.pdf, UU 24/2002). Redaksi yang mengikat adalah teks undang-undang pada kompilasi.

### Jenis SUN

| Jenis | Ciri umum | Status |
|---|---|---|
| Surat Perbendaharaan Negara (SPN) | SUN berjangka waktu pendek, sampai dengan 12 bulan, dengan pembayaran bunga secara diskonto | CONFIRMED (sumber: Pengayaan 6 Mei 2026; UU 24/2002) |
| Obligasi Negara | SUN berjangka waktu lebih dari 12 bulan, dengan kupon dan/atau pembayaran bunga secara diskonto | CONFIRMED (sumber: Pengayaan 6 Mei 2026; UU 24/2002) |

### SUN Ritel

| Instrumen | Sifat | Status |
|---|---|---|
| ORI (Obligasi Negara Ritel) | Dapat diperdagangkan (tradable) di pasar sekunder | CONFIRMED (sumber: Pengayaan 6 Mei 2026) |
| SBR (Savings Bond Ritel) | Tidak dapat diperdagangkan (non-tradable) | CONFIRMED (sumber: Pengayaan 6 Mei 2026) |

- **CONFIRMED**: Distribusi SUN ritel melibatkan Mitra Distribusi (sumber: Pengayaan 6 Mei 2026).

### Jenis Transaksi

| Transaksi | Penjelasan ringkas | Sumber |
|---|---|---|
| Penerbitan melalui lelang | Penerbitan SUN di pasar perdana melalui mekanisme lelang | CONFIRMED (Pengayaan 6 Mei 2026) |
| Penerbitan melalui private placement | Penerbitan SUN kepada pihak tertentu di luar mekanisme lelang | CONFIRMED (Pengayaan 6 Mei 2026) |
| Penerbitan melalui bookbuilding | Penerbitan SUN dengan mekanisme pengumpulan pemesanan | CONFIRMED (Pengayaan 6 Mei 2026) |
| Cash buyback | Pembelian kembali SUN sebelum jatuh tempo dengan pembayaran tunai | CONFIRMED (Pengayaan 6 Mei 2026; PMK 114/2023) |
| Debt switch | Penukaran SUN tertentu dengan SUN lain | CONFIRMED (Pengayaan 6 Mei 2026) |

Rincian syarat, mekanisme, dan jadwal setiap transaksi tidak dicatat di sini. Pengembang harus merujuk ke peraturan pada indeks di bawah, bukan menyimpulkan sendiri.

### Pihak yang Terlibat

| Pihak | Peran sebagaimana disebut sumber | Sumber |
|---|---|---|
| Dealer Utama | Disebut sebagai pihak dalam transaksi SUN; rincian hak dan kewajiban merujuk ke regulasi | CONFIRMED (Pengayaan 6 Mei 2026) |
| Bank Indonesia | Agen penatausaha dan agen lelang | CONFIRMED (Pengayaan 6 Mei 2026) |
| Bursa Efek Indonesia (BEI) | Disebut sebagai pihak dalam ekosistem SUN; rincian peran merujuk ke sumber | CONFIRMED (Pengayaan 6 Mei 2026) |
| Mitra Distribusi | Pihak dalam distribusi SUN ritel | CONFIRMED (Pengayaan 6 Mei 2026) |

- **OUT OF SCOPE**: Integrasi dengan sistem Bank Indonesia, BEI, Dealer Utama, atau Mitra Distribusi. Tidak ada integrasi semacam itu yang tersedia atau direncanakan tanpa validasi (lihat [market-data-proposal](../08-integrations/market-data-proposal.md)).

### Tugas Dit. SUN

- **CONFIRMED**: Deck Pengayaan mengutip Pasal 1441 PMK 124 Tahun 2024 sebagai dasar tugas Direktorat Surat Utang Negara (sumber: Pengayaan 6 Mei 2026).
- **OPEN QUESTION**: Redaksi lengkap rumusan tugas dan fungsi belum dicatat dalam fact sheet sesi ini. Pengembang tidak boleh merumuskan ulang tugas Dit. SUN; kutip langsung dari sumber setelah diverifikasi mentor.

### Indeks Regulasi (Kompilasi)

Sumber kompilasi menyatakan berasal dari Database Peraturan BPK dan JDIH Kemenkeu (sumber: Kompilasi_Peraturan_SUN_formal.pdf).

| No | Regulasi | Judul/pokok yang tercatat | Status |
|---|---|---|---|
| 1 | UU 24/2002 | tentang Surat Utang Negara | CONFIRMED |
| 2 | PP 76/2005 | Judul belum dicatat; lihat kompilasi | CONFIRMED (keberadaan) |
| 3 | PMK 111/2024 | tentang Pengelolaan SUN | CONFIRMED |
| 4 | PMK 165/2022 | tentang Transaksi SBN di Pasar Sekunder | CONFIRMED |
| 5 | PMK 51/2019 | Judul belum dicatat; lihat kompilasi | CONFIRMED (keberadaan) |
| 6 | PMK 215/2019 | Judul belum dicatat; lihat kompilasi | CONFIRMED (keberadaan) |
| 7 | PMK 114/2023 | tentang Pembelian Kembali SUN di Pasar Sekunder | CONFIRMED |
| 8 | PMK 168/2019 | Judul belum dicatat; lihat kompilasi | CONFIRMED (keberadaan) |
| 9 | PMK 128/PMK.08/2012 | Judul belum dicatat; lihat kompilasi | CONFIRMED (keberadaan) |
| 10 | PMK 27/2020 | Judul belum dicatat; lihat kompilasi | CONFIRMED (keberadaan) |

- **OPEN QUESTION (OQ-17)**: Permintaan awal menyebut "PMK 128 tahun 2019", tetapi kompilasi memakai PMK 128/PMK.08/2012. Status substitusi ini perlu dikonfirmasi.
- **OPEN QUESTION**: Status berlaku setiap regulasi (berlaku, diubah, dicabut) belum diverifikasi. Relasi antarperaturan tidak boleh diisi tanpa sumber.

## Implikasi untuk SUNOVATE

- **PROPOSED**: Regulasi pada indeks direkam sebagai `knowledge_entries` bertipe `REGULATION` dengan klasifikasi `PUBLIC` bila sudah diundangkan (lihat [document-classification](../04-data/document-classification.md)). Pemetaan klasifikasi tetap OQ-05.
- **PROPOSED**: Hubungan antarperaturan dicatat di `regulation_relations` dengan tipe `AMENDS`, `REVOKES`, `IMPLEMENTS`, `REFERENCES`, `SUPERSEDES`, hanya bila didukung teks peraturan.
- **PROPOSED**: Istilah domain (SUN, SPN, Obligasi Negara, ORI, SBR, lelang, private placement, bookbuilding, cash buyback, debt switch, Dealer Utama, Mitra Distribusi) dimasukkan ke [glossary](../00-project/glossary.md) dan dipakai sebagai `tags` untuk membantu retrieval.
- **CONFIRMED**: Hermes hanya menjawab berdasarkan knowledge yang sudah dipublikasikan dan diotorisasi, dengan sitasi; Hermes tidak memberikan rekomendasi transaksi atau keputusan keuangan (sumber: brief sesi 2026-10-01; lihat [scope-guard](../05-ai-rag/scope-guard.md)).
- **CONFIRMED**: Seluruh data contoh berlabel `SIMULATED_DATA` dan tidak boleh memuat angka SUN riil (sumber: AGENTS.md; lihat [simulated-data-policy](../04-data/simulated-data-policy.md)).
- **OPEN QUESTION**: Apakah SUNOVATE kelak menampilkan data SUN Business (instrumen, lelang, transaksi) masih belum diputuskan (ADR-013).

## Open Questions

- OQ-04 Dokumen apa yang boleh masuk repository dan RAG.
- OQ-05 Klasifikasi setiap jenis dokumen.
- OQ-17 Status PMK 128.
- Redaksi tugas Dit. SUN berdasarkan Pasal 1441 PMK 124/2024.

Daftar lengkap: [open-questions](../00-project/open-questions.md).

## Related Documents

- [team-work-scope](team-work-scope.md)
- [knowledge-lifecycle](knowledge-lifecycle.md)
- [business-rules](business-rules.md)
- [scope-and-boundaries](../00-project/scope-and-boundaries.md)
- [metadata-schema](../04-data/metadata-schema.md)
