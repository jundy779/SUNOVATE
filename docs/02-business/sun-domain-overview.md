# Gambaran Domain Surat Utang Negara (SUN)

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-06

## Purpose

Dokumen ini memberi latar belakang domain SUN bagi pengembang SUNOVATE agar istilah pada metadata, taksonomi knowledge, dan pertanyaan Hermes dapat dipahami. Isi dibatasi pada fakta yang tercantum pada dokumen sumber di root workspace. Dokumen ini bukan rujukan hukum; rujukan resmi tetap peraturan perundang-undangan dan dokumen Dit. SUN.

## Cara Membaca Sumber

Dokumen ini memisahkan dua sumber. Keduanya tidak boleh dicampur dalam satu label.

| Sumber | Arti | Cara dirujuk |
|---|---|---|
| Deck Pengayaan | `Pengayaan_Kelas_Magang_6_Mei_2026.pdf`, sesi berbagi Dit. SUN. Klaim deck diperlakukan sebagai klaim deck, bukan teks regulasi. | "Pengayaan 6 Mei 2026" |
| Kompilasi | `Kompilasi_Peraturan_SUN_formal.pdf`, 199 halaman, 10 regulasi. | `Kompilasi Peraturan SUN, <regulasi>, Pasal X, hal. N` (hal. = halaman PDF 1 sampai 199, bukan nomor cetak peraturan) |

- **CONFIRMED (sumber: Kompilasi Peraturan SUN, sampul, hal. 1)**: Kompilasi menyatakan sumber utamanya adalah Database Peraturan BPK dan JDIH Kementerian Keuangan.
- **NOT VERIFIABLE FROM COMPILATION**: Klaim deck yang tidak ada di kompilasi (nama produk ORI dan SBR, istilah "debt switch", Bursa Efek Indonesia, istilah payung dan singkatan SBN, PMK 124/2024 dan Pasal 1441) dipertahankan sebagai klaim deck. Tidak adanya klaim itu di kompilasi tidak membuktikan klaim salah; hanya berarti kompilasi tidak dapat dipakai untuk memverifikasinya.
- **OPEN QUESTION**: Status berlaku saat ini (berlaku, diubah, dicabut) setiap regulasi tidak dapat diturunkan dari kompilasi. Lihat bagian "Keterbatasan Pembacaan Kompilasi".

## Batasan Penting

- **CONFIRMED**: SUNOVATE tidak menggantikan sistem transaksi SUN resmi, tidak mengambil keputusan keuangan, dan tidak memberikan akses dokumen tanpa otorisasi (sumber: brief sesi 2026-10-01).
- **CONFIRMED**: Proses yang dijelaskan di bawah (penerbitan, pembelian kembali termasuk penukaran, penatausahaan) tidak dieksekusi, dihitung, atau diputuskan oleh SUNOVATE. SUNOVATE hanya menyimpan, mengorganisasikan, dan menemukan kembali knowledge tentang proses tersebut (sumber: brief sesi 2026-10-01).
- **CONFIRMED**: Tabel bisnis SUN yang belum tervalidasi (instrumen, lelang, transaksi, yield, setelmen) telah dihapus dari skema; area SUN Business tetap OPEN QUESTION untuk fase berikutnya (sumber: ADR-013, keputusan sesi 2026-10-01).
- **OUT OF SCOPE**: Angka APBN, kebutuhan pembiayaan, yield, hasil lelang, atau data pasar apa pun. Dokumen ini dan data contoh SUNOVATE tidak memuat angka riil. Angka dalam regulasi (tarif, batas, denda, tenggat) tidak disalin ke dokumen ini; satu-satunya pengecualian adalah batas jangka waktu yang membedakan SPN dari Obligasi Negara, yang bersifat definisi dan dikutip dengan Pasal dan halaman.

## Confirmed Information

### Definisi SUN

- **CONFIRMED (sumber: Kompilasi Peraturan SUN, UU 24/2002, Pasal 1 angka 1, hal. 4; Pengayaan 6 Mei 2026)**: SUN adalah surat berharga berupa surat pengakuan utang dalam mata uang rupiah maupun valuta asing yang dijamin pembayaran bunga dan pokoknya oleh Negara Republik Indonesia sesuai masa berlakunya. Redaksi yang mengikat adalah teks undang-undang pada kompilasi.

### Jenis SUN

| Jenis | Ciri umum | Status |
|---|---|---|
| Surat Perbendaharaan Negara (SPN) | SUN berjangka waktu pendek, sampai dengan 12 bulan, dengan pembayaran bunga secara diskonto | CONFIRMED (sumber: Kompilasi Peraturan SUN, UU 24/2002, Pasal 3 ayat (2), hal. 5; selaras dengan Pengayaan 6 Mei 2026) |
| Obligasi Negara | SUN berjangka waktu lebih dari 12 bulan, dengan kupon dan/atau pembayaran bunga secara diskonto | CONFIRMED (sumber: Kompilasi Peraturan SUN, UU 24/2002, Pasal 3 ayat (3), hal. 5; selaras dengan Pengayaan 6 Mei 2026) |

- **CONFIRMED (sumber: Kompilasi Peraturan SUN, UU 24/2002, Pasal 3 ayat (1), hal. 5)**: SUN terdiri atas SPN dan Obligasi Negara.
- **CONFIRMED (sumber: Kompilasi Peraturan SUN, UU 24/2002, Pasal 2 ayat (2), hal. 5)**: SUN diterbitkan dalam bentuk yang diperdagangkan atau yang tidak diperdagangkan di Pasar Sekunder.

### SUN Ritel

| Instrumen | Sifat menurut deck | Sumber deck | Verifikasi di kompilasi |
|---|---|---|---|
| ORI (Obligasi Negara Ritel) | Dapat diperdagangkan (tradable) di pasar sekunder | Pengayaan 6 Mei 2026 | NOT VERIFIABLE FROM COMPILATION: nama produk ORI tidak ada di kompilasi |
| SBR (Savings Bond Ritel) | Tidak dapat diperdagangkan (non-tradable) | Pengayaan 6 Mei 2026 | NOT VERIFIABLE FROM COMPILATION: nama produk SBR tidak ada di kompilasi |

- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 27/2020, Pasal 2 ayat (2), hal. 181)**: SUN Ritel dapat diterbitkan dalam bentuk dapat diperdagangkan dan dalam bentuk tidak dapat diperdagangkan. Pemetaan ORI ke bentuk pertama dan SBR ke bentuk kedua berasal dari deck saja.
- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 27/2020, Pasal 1 angka 8, hal. 178)**: SUN Ritel adalah SUN yang dijual Pemerintah kepada investor ritel di pasar perdana domestik.
- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 27/2020, Pasal 2 ayat (4), hal. 181; Pasal 1 angka 13, hal. 179)**: Pemerintah dapat menetapkan Mitra Distribusi untuk membantu pemasaran dan penawaran SUN Ritel. Mitra Distribusi adalah Bank, Perusahaan Efek, Perusahaan Financial Technology, dan/atau Penyelenggara Perdagangan Melalui Sistem Elektronik yang ditetapkan Pemerintah.

### Jenis Transaksi

Kolom "Sumber deck" memuat klaim deck Pengayaan. Kolom "Sumber kompilasi" memuat teks regulasi yang mendukung atau menyempurnakan klaim itu. Setiap sel kompilasi memakai format `Kompilasi Peraturan SUN, <regulasi>, Pasal X, hal. N`.

| Transaksi | Penjelasan ringkas | Sumber deck | Sumber kompilasi |
|---|---|---|---|
| Lelang | Penjualan SUN di pasar perdana domestik yang diikuti Peserta Lelang SUN | Pengayaan 6 Mei 2026 | CONFIRMED: PMK 168/2019, Pasal 1 angka 7, hal. 142; PMK 111/2024, Pasal 14 ayat (1)-(2), hal. 40-41 |
| Private placement | Penjualan SUN tanpa lelang berupa transaksi bilateral antara Pemerintah dan Pihak, dengan ketentuan sesuai kesepakatan. Dibedakan dari transaksi langsung | Pengayaan 6 Mei 2026 | CONFIRMED: PMK 51/2019, Pasal 1 angka 7, hal. 62; PMK 111/2024, Pasal 14 ayat (5) huruf a dan c, hal. 41 |
| Bookbuilding | Cara penjualan tanpa lelang melalui pengumpulan pemesanan dalam periode yang ditentukan. Juga dipakai untuk pembelian kembali dan untuk penjualan SUN valuta asing di pasar perdana domestik | Pengayaan 6 Mei 2026 | CONFIRMED: PMK 111/2024, Pasal 14 ayat (5) huruf b, hal. 41; PMK 114/2023, Pasal 2 ayat (2) huruf b angka 1, hal. 121; PMK 128/PMK.08/2012, Pasal 1 angka 7, hal. 170 |
| Pembelian kembali (buyback) | Pembelian kembali SUN oleh Pemerintah di Pasar Sekunder sebelum jatuh tempo, dengan cara tunai dan/atau penukaran. Istilah "cash buyback" bukan istilah teks regulasi; istilah teks adalah pembelian kembali dengan cara tunai | Pengayaan 6 Mei 2026 ("cash buyback") | CONFIRMED: PMK 114/2023, Pasal 2 ayat (1), (3) dan (4), hal. 121 |
| Penukaran | Cara pembelian kembali dengan penyerahan SUN atau SBSN sebagai seri penukar; selisih nilai penyelesaian dapat dibayar tunai | Pengayaan 6 Mei 2026 (istilah "debt switch") | CONFIRMED untuk "penukaran": PMK 114/2023, Pasal 2 ayat (3) huruf b dan ayat (5)-(6), hal. 121. NOT VERIFIABLE FROM COMPILATION untuk istilah "debt switch". PROPOSED: istilah "debt switch" dipetakan ke "penukaran"; perlu validasi mentor |
| Transaksi SUN secara langsung | Transaksi SUN antara Pemerintah dan Bank Indonesia, Lembaga Penjamin Simpanan, BUMN, BLU, dan/atau Dealer Utama secara langsung melalui sarana yang ditentukan | Tidak disebut di deck | PROPOSED penambahan baris. CONFIRMED keberadaan regulasi: PMK 165/2022, judul, hal. 49, dan Pasal 1 angka 16, hal. 51 |
| Penjualan dan pembelian kembali SUN valuta asing di pasar internasional | Penjualan dan pembelian kembali SUN valuta asing di pasar internasional yang diselenggarakan Pemerintah | Tidak disebut di deck | PROPOSED penambahan baris. CONFIRMED keberadaan regulasi: PMK 215/2019, judul, hal. 82, dan Pasal 2 ayat (1), hal. 87 |

- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 111/2024, Pasal 14 ayat (5), hal. 41)**: Penjualan SUN melalui metode tanpa lelang mencakup penempatan melalui transaksi bilateral (private placement), pengumpulan pemesanan (bookbuilding), dan transaksi langsung. Daftar transaksi di atas tidak lengkap dan bukan daftar yang ditetapkan Dit. SUN.

Rincian syarat, mekanisme, dan jadwal setiap transaksi tidak dicatat di sini. Pengembang harus merujuk ke peraturan pada indeks di bawah, bukan menyimpulkan sendiri.

### Pihak yang Terlibat

| Pihak | Peran menurut deck | Sumber kompilasi |
|---|---|---|
| Dealer Utama | Pihak dalam transaksi SUN; rincian hak dan kewajiban merujuk ke regulasi (Pengayaan 6 Mei 2026) | CONFIRMED: bank atau perusahaan efek yang ditunjuk Menteri sebagai Dealer Utama (PMK 114/2023, Pasal 1 angka 15, hal. 119). Peraturan Menteri khusus Dealer Utama dirujuk tetapi tidak ada di kompilasi |
| Bank Indonesia | Agen penatausaha dan agen lelang (Pengayaan 6 Mei 2026) | CONFIRMED: penatausahaan SUN (pencatatan kepemilikan, kliring dan setelmen, agen pembayar bunga dan pokok) dilaksanakan Bank Indonesia (UU 24/2002, Pasal 12 ayat (1), hal. 7). Menteri menunjuk Bank Indonesia sebagai agen lelang SPN dan dapat menunjuk sebagai agen lelang Obligasi Negara (UU 24/2002, Pasal 13 ayat (1)-(2), hal. 7-8). Bank Indonesia bertindak selaku agen penatausahaan SUN (PMK 111/2024, Pasal 19 ayat (4), hal. 43) |
| Bursa Efek Indonesia (BEI) | Pihak dalam ekosistem SUN; rincian peran merujuk ke sumber (Pengayaan 6 Mei 2026) | NOT VERIFIABLE FROM COMPILATION: BEI tidak disebut di kompilasi. CONFIRMED hanya bahwa perdagangan SUN dapat melalui bursa dan/atau di luar bursa (PMK 111/2024, Pasal 4 ayat (4), hal. 37) |
| Mitra Distribusi | Pihak dalam distribusi SUN ritel (Pengayaan 6 Mei 2026) | CONFIRMED: definisi dan komposisi pada bagian SUN Ritel di atas (PMK 27/2020, Pasal 1 angka 13, hal. 179; Pasal 5 ayat (1), hal. 182) |

- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 111/2024, Pasal 1 angka 8, hal. 36)**: Setelmen adalah penyelesaian transaksi SUN yang terdiri dari setelmen dana dan/atau setelmen kepemilikan SUN.
- **OUT OF SCOPE**: Integrasi dengan sistem Bank Indonesia, BEI, Dealer Utama, atau Mitra Distribusi. Tidak ada integrasi semacam itu yang tersedia atau direncanakan tanpa validasi (lihat [market-data-proposal](../08-integrations/market-data-proposal.md)).

### Tugas Dit. SUN

- **CONFIRMED (sumber: Pengayaan 6 Mei 2026)**: Deck mengutip Pasal 1441 PMK 124 Tahun 2024 sebagai dasar tugas Direktorat Surat Utang Negara. **NOT VERIFIABLE FROM COMPILATION**: PMK 124/2024 tidak dimuat dalam kompilasi, sehingga isi pasal dan keberadaan peraturan itu belum diverifikasi. Dokumen ini tidak menyatakan PMK 124/2024 sebagai dasar tugas Dit. SUN yang terverifikasi.
- **OPEN QUESTION**: Redaksi lengkap rumusan tugas dan fungsi belum dicatat dalam fact sheet sesi ini. Pengembang tidak boleh merumuskan ulang tugas Dit. SUN; kutip langsung dari sumber setelah diverifikasi mentor.
- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 111/2024, Pasal 14 ayat (6), Pasal 16 ayat (4), Pasal 17 ayat (1), hal. 41-42)**: Beberapa kegiatan (penjualan SUN, pembelian kembali SUN, rekomendasi acuan harga) disebut dilaksanakan oleh Direktorat Jenderal melalui Direktorat Surat Utang Negara. Ini adalah ketentuan pelaksanaan kegiatan di regulasi tersebut, bukan rumusan tugas dan fungsi organisasi.

### Indeks Regulasi (Kompilasi)

Judul diambil dari kepala naskah masing-masing regulasi (bukan dari indeks kompilasi hal. 2 yang tidak memuat judul untuk beberapa PMK). Nomor dan judul yang rusak oleh ekstraksi teks dicatat apa adanya.

| No | Regulasi | Halaman PDF | Judul (tentang) | Status |
|---|---|---|---|---|
| 1 | UU 24/2002 | 3-20 | Surat Utang Negara | CONFIRMED (sumber: Kompilasi Peraturan SUN, indeks, hal. 2) |
| 2 | PP 76/2005 | 21-33 | Tata Cara Penatausahaan, Pertanggungjawaban, dan Publikasi Informasi atas Pengelolaan Surat Utang Negara | CONFIRMED (sumber: Kompilasi Peraturan SUN, PP 76/2005, judul, hal. 21; indeks, hal. 2) |
| 3 | PMK 111/2024 | 34-48 | Pengelolaan Surat Utang Negara | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 111/2024, judul, hal. 34) |
| 4 | PMK 165/2022 | 49-59 | Transaksi Surat Utang Negara Secara Langsung | CONFIRMED untuk judul pada naskah (sumber: Kompilasi Peraturan SUN, PMK 165/2022, judul, hal. 49; judul yang sama disebut PMK 111/2024, Pasal 30 angka 4 huruf b, hal. 47). Indeks kompilasi hal. 2 memuat judul berbeda: NEEDS LEGAL CONFIRMATION |
| 5 | PMK 51/2019 | 60-81 | Penjualan Surat Utang Negara di Pasar Perdana Domestik dengan Cara Private Placement | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 51/2019, judul, hal. 60; ejaan "private" dari hal. 76, kepala naskah terbaca "PRWATE" akibat galat OCR) |
| 6 | PMK 215/2019 | 82-116 | Penjualan dan Pembelian Kembali Surat Utang Negara dalam Valuta Asing di Pasar Internasional | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 215/2019, judul, hal. 82; nomor pada kepala naskah terbaca "215 /PMK.OS/2019", galat OCR untuk 08) |
| 7 | PMK 114/2023 | 117-139 | Pembelian Kembali Surat Utang Negara di Pasar Sekunder | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 114/2023, diktum, hal. 118) |
| 8 | PMK 168/2019 | 140-167 | Lelang Surat Utang Negara di Pasar Perdana Domestik | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 168/2019, judul, hal. 140; nomor pada kepala naskah terbaca "168 /PMK.OS/2019", galat OCR untuk 08) |
| 9 | PMK 128/PMK.08/2012 | 168-175 | Penjualan Surat Utang Negara dalam Valuta Asing di Pasar Perdana Domestik dengan Cara Bookbuilding | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 128/PMK.08/2012, judul, hal. 168) |
| 10 | PMK 27/2020 | 176-199 | Penjualan Surat Utang Negara Ritel di Pasar Perdana Domestik | CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 27/PMK.08/2020, judul, hal. 176). Nomor pada kepala naskah rusak oleh OCR; angka 27 dikonfirmasi oleh judul lampiran hal. 198 dan indeks hal. 2 |

Rentang halaman diambil dari bookmark PDF kompilasi dan indeks hal. 2, lalu dicocokkan dengan kepala naskah tiap regulasi.

- **NEEDS LEGAL CONFIRMATION**: Judul resmi PMK 165/2022. Indeks kompilasi (hal. 2) menulis "Transaksi Surat Berharga Negara di Pasar Sekunder", sedangkan kepala naskah (hal. 49) menulis "Transaksi Surat Utang Negara Secara Langsung". Judul pada naskah dicatat sebagai CONFIRMED karena teks regulasi itu sendiri dan PMK 111/2024 memakainya. Ketidaksesuaian indeks terhadap naskah belum dijelaskan oleh kompilasi; sumber resmi yang menjadi acuan adalah OQ-27.
- **OPEN QUESTION (OQ-17)**: Permintaan awal menyebut "PMK 128 tahun 2019". Kompilasi memuat PMK 128/PMK.08/2012 (bukan "PMK 128 tahun 2019") pada hal. 168-175, tentang penjualan SUN dalam valuta asing di pasar perdana domestik dengan cara bookbuilding. Satu-satunya keterangan substitusi adalah catatan sampul (hal. 1) tanpa alasan tertulis; kompilasi tidak menjelaskan mengapa nomor atau tahun berbeda. Apakah "PMK 128 tahun 2019" salah ketik atau regulasi lain, serta status berlaku PMK 128/PMK.08/2012: NEEDS LEGAL CONFIRMATION. "PMK 128 tahun 2019" tidak disajikan sebagai regulasi yang ada.
- **OPEN QUESTION**: Status berlaku setiap regulasi (berlaku, diubah, dicabut) belum diverifikasi (lihat OQ-26). Relasi antarperaturan tidak boleh diisi tanpa sumber.
- **CONFIRMED (sumber: Kompilasi Peraturan SUN, PMK 111/2024, Pasal 30, hal. 47)**: PMK 111/2024 mencabut seluruh PMK 212/PMK.08/2016 dan ketentuan tertentu pada PMK 168/PMK.08/2021, PMK 114/2023, PMK 168/2019, dan PMK 165/2022. Ini pernyataan antarteks dalam kompilasi, bukan status berlaku saat ini. PMK 168/PMK.08/2021 (Dealer Utama, tidak ada di kompilasi) berbeda dari PMK 168/PMK.08/2019 (lelang, hal. 140-167).

### Keterbatasan Pembacaan Kompilasi

- **CONFIRMED (sumber: metode telaah kompilasi, 2026-10-06)**: Temuan di dokumen ini berasal dari pembacaan terbantu mesin atas kompilasi: ekstraksi teks tanpa OCR, dengan kutipan diperiksa otomatis terhadap teks ekstraksi (bukan terhadap gambar halaman PDF). Teks ekstraksi tidak dibandingkan dengan sumber resmi seperti Berita Negara atau JDIH.
- **OPEN QUESTION**: Tanggal pengundangan dan nomor Berita Negara PMK 111/2024 tidak terbaca pada kompilasi (hal. 48); lihat OQ-28.
- **OPEN QUESTION**: Status berlaku saat ini tidak dapat diturunkan dari kompilasi, dan ketiadaan relasi pencabutan di kompilasi tidak membuktikan suatu regulasi masih berlaku (OQ-26).

## Implikasi untuk SUNOVATE

- **PROPOSED**: Regulasi pada indeks direkam sebagai `knowledge_entries` bertipe `REGULATION` dengan klasifikasi `PUBLIC` bila sudah diundangkan (lihat [document-classification](../04-data/document-classification.md)). Pemetaan klasifikasi tetap OQ-05.
- **PROPOSED**: Hubungan antarperaturan dicatat di `regulation_relations` dengan tipe `AMENDS`, `REVOKES`, `IMPLEMENTS`, `REFERENCES`, `SUPERSEDES`, hanya bila didukung teks peraturan. Pencabutan sebagian dan ketentuan peralihan memerlukan catatan tambahan (lihat [logical-data-model](../04-data/logical-data-model.md) dan [document-lifecycle](document-lifecycle.md)).
- **PROPOSED**: Istilah domain (SUN, SPN, Obligasi Negara, ORI, SBR, lelang, private placement, bookbuilding, pembelian kembali, penukaran, Dealer Utama, Mitra Distribusi) dimasukkan ke [glossary](../00-project/glossary.md) dan dipakai sebagai `tags` untuk membantu retrieval. Istilah deck yang tidak ada di kompilasi (ORI, SBR, "debt switch", "cash buyback", SBN) ditandai sebagai istilah deck di glosarium.
- **CONFIRMED**: Hermes hanya menjawab berdasarkan knowledge yang sudah dipublikasikan dan diotorisasi, dengan sitasi; Hermes tidak memberikan rekomendasi transaksi atau keputusan keuangan (sumber: brief sesi 2026-10-01; lihat [scope-guard](../05-ai-rag/scope-guard.md)).
- **CONFIRMED**: Seluruh data contoh berlabel `SIMULATED_DATA` dan tidak boleh memuat angka SUN riil (sumber: AGENTS.md; lihat [simulated-data-policy](../04-data/simulated-data-policy.md)).
- **OPEN QUESTION**: Apakah SUNOVATE kelak menampilkan data SUN Business (instrumen, lelang, transaksi) masih belum diputuskan (ADR-013).

## Open Questions

- OQ-04 Dokumen apa yang boleh masuk repository dan RAG.
- OQ-05 Klasifikasi setiap jenis dokumen.
- OQ-17 Status PMK 128 (penggantian "PMK 128 tahun 2019" oleh PMK 128/PMK.08/2012 tidak dijelaskan kompilasi).
- OQ-26 Status berlaku terkini 10 regulasi dalam kompilasi.
- OQ-27 Sumber acuan untuk judul dan nomor regulasi (judul PMK 165/2022, nomor PMK 27/2020).
- OQ-28 Tanggal pengundangan dan nomor Berita Negara PMK 111/2024.
- Redaksi tugas Dit. SUN berdasarkan Pasal 1441 PMK 124/2024 (klaim deck, NOT VERIFIABLE FROM COMPILATION).

Daftar lengkap: [open-questions](../00-project/open-questions.md).

## Related Documents

- [team-work-scope](team-work-scope.md)
- [knowledge-lifecycle](knowledge-lifecycle.md)
- [business-rules](business-rules.md)
- [scope-and-boundaries](../00-project/scope-and-boundaries.md)
- [metadata-schema](../04-data/metadata-schema.md)
