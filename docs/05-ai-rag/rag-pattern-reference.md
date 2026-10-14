# Referensi Pola RAG dan Agentic AI

**Status:** PROPOSED
**Last Updated:** 2026-10-14

## Tujuan

Dokumen ini menerjemahkan dua referensi visual yang diberikan ketua proyek pada 14 Oktober 2026—pola Agentic AI dan lima lapisan RAG—ke batas arsitektur SUNOVATE. Gambar pihak ketiga tidak disalin ke repositori; konsepnya ditelaah dan disesuaikan dengan tata kelola Dit. SUN.

## Pemetaan lima lapisan RAG

| Lapisan referensi | Penerapan SUNOVATE | Status |
|---|---|---|
| Split | Ekstraksi, normalisasi, pemisahan berbasis Pasal/tahap/bagian, dan pencatatan hash | Preview chunking deterministik berbasis Python **IMPLEMENTED**; ekstraksi berkas produksi dan tokenizer model **PROPOSED** |
| Search | Pencarian leksikal dengan penyaringan izin sebelum pemeringkatan; vektor disiapkan pada skema | Leksikal data simulasi **IMPLEMENTED**; embedding dan hybrid search menunggu OQ-11 |
| Compose | Jawaban hanya dari konteks terotorisasi dan memiliki sitasi | Jawaban ekstraktif dan validasi sitasi **IMPLEMENTED**; model eksternal **PROPOSED** |
| Filter | Top-k, pemeriksaan cakupan, retry ejaan terbatas, dan penolakan bila bukti tidak cukup | **IMPLEMENTED** pada data simulasi; reranker model **PROPOSED** |
| Production | Audit, evaluasi, umpan balik, keamanan, cache, dan pemantauan kualitas | Audit/evaluasi/umpan balik dasar **IMPLEMENTED**; cache dan pemantauan produksi **PROPOSED** |

## Adaptasi Agentic AI

SAVI AI tidak diubah menjadi agen otonom bebas. Pola yang dapat dipakai adalah orkestrasi terkendali: menerima pertanyaan, memeriksa ruang lingkup dan izin, memilih pencarian yang disetujui, menyusun jawaban bersitasi, lalu meminta tindakan manusia untuk keputusan yang membutuhkan kewenangan.

| Komponen referensi | Keputusan SUNOVATE |
|---|---|
| Orchestrator | Gateway deterministik menjadi pengendali alur; tidak boleh melewati pemeriksaan izin. |
| Memory | Riwayat percakapan tidak menjadi sumber fakta dan tidak membuka dokumen di luar izin. Memori jangka panjang belum diaktifkan. |
| Tools | Hanya layanan internal yang didaftarkan dan diaudit. Penelusuran web bebas tidak diaktifkan. |
| Planning | Rencana multi-langkah dibatasi pada alur yang telah disetujui; tidak melakukan transaksi atau keputusan SUN. |
| Specialized agents | Ditunda. Pembagian agen tidak diperlukan untuk MVP dan menambah permukaan risiko. |
| Human in the loop | Wajib untuk publikasi knowledge, koreksi data terkunci, dan tindakan berwenang lainnya. |
| Feedback | Umpan balik dicatat sebagai bahan evaluasi, bukan langsung mengubah aturan atau pengetahuan. |

## Implementasi saat ini

`apps/api/sunovate_api/hermes/chunking.py` menyediakan preview pemotongan teks yang sudah diekstrak. Modul ini:

- mengenali batas `Pasal 1` maupun kerusakan spasi seperti `Pasal29`;
- mengenali `Tahap` dan `Langkah` untuk SOP/playbook serta heading terbatas untuk kajian/laporan;
- tidak menggabungkan isi lintas unit struktur;
- menghasilkan urutan, label bagian, jumlah kata, dan SHA-256 yang stabil;
- tidak membaca berkas, menulis database, membuat embedding, atau memublikasikan knowledge.

Jumlah kata hanya pagar pengembangan. Ambang token produksi tetap menunggu model dan tokenizer yang disetujui melalui OQ-11. Teks yang mengandung instruksi tetap diperlakukan sebagai data; pertahanan prompt injection tetap dilakukan pada pipeline terpisah sebelum retrieval.

## Batas keputusan

- Tidak ada data atau dokumen internal yang dimasukkan oleh perubahan ini.
- Tidak ada koneksi AI, vector database, web search, Telegram, atau WhatsApp yang diaktifkan.
- Hasil preview harus ditinjau manusia sebelum menjadi chunk resmi.
- Klasifikasi dan izin wajib diwariskan dari dokumen induk pada pipeline produksi.

## Related Documents

- [rag-architecture.md](./rag-architecture.md)
- [chunking-strategy.md](./chunking-strategy.md)
- [ingestion-pipeline.md](./ingestion-pipeline.md)
- [prompt-injection-defense.md](./prompt-injection-defense.md)
- [human-approval.md](./human-approval.md)
