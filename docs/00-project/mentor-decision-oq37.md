# Lembar Keputusan Glosarium SAVI, OQ-37

**Status:** PARTIAL, CONFIRMED MENTOR ANSWERS
**Last Updated:** 2026-10-14

## Tujuan

Mencatat jawaban mentor pada 14 Oktober 2026 mengenai tata kelola glosarium SAVI. Bagian yang dijawab menjadi arahan resmi proyek; OQ-37 tetap parsial karena beberapa pemetaan dan detail teknis belum ditentukan.

## Jawaban yang diterima

| Pertanyaan | Jawaban | Keputusan kerja |
|---|---|---|
| Istilah SUN apa saja yang boleh dianggap memiliki arti sama? | SUN = Surat Utang Negara | Aktif hanya sebagai kepanjangan singkatan SUN. Tidak mengesahkan kandidat pemetaan lain. |
| Siapa yang berwenang menyetujui atau memperbaiki istilah? | Admin | Belum dipetakan menjadi permission runtime karena jenis admin dan dasar kewenangannya belum ditentukan. |
| Dokumen apa yang menjadi sumber resmi? | Peraturan SUN dan playbook transaksi SUN | Diterima sebagai jenis sumber; setiap entri tetap memerlukan identitas dokumen, versi, bagian, status, klasifikasi, dan pemilik. |
| Apakah semua pegawai boleh melihat glosarium yang sama? | Boleh | Glosarium istilah dapat dibaca seluruh pegawai. Hak melihat dokumen sumber tetap mengikuti izin dan klasifikasi. |
| Jika istilah berubah, apakah istilah lama disimpan sebagai riwayat? | Tidak | Istilah lama tidak ditampilkan sebagai entri aktif. Riwayat perubahan dan audit teknis tetap dipertahankan agar perubahan dapat ditelusuri. |
| Berapa lama glosarium diperiksa ulang? | Setiap 3 bulan | Siklus review triwulanan; tanggal mulai dan pengingat operasional belum ditetapkan. |
| Bolehkah SAVI memakai singkatan yang belum ada di dokumen resmi? | Tidak | Singkatan tanpa sumber resmi tetap diblokir dari retrieval expansion. |
| Jika SAVI tidak yakin, pemeriksaan diarahkan kepada siapa? | Admin | SAVI hanya memberi arahan pemeriksaan. Sistem belum menunjuk akun admin, mengirim tiket, atau notifikasi otomatis. |

## Keputusan yang Aman Diaktifkan

- `SUN` dapat dipahami sebagai singkatan dari `Surat Utang Negara`.
- Glosarium boleh tersedia kepada seluruh pegawai, tetapi tidak membuka dokumen sumber yang berada di luar hak akses pengguna.
- Review glosarium dilakukan setiap tiga bulan.
- Singkatan yang tidak tercantum pada dokumen resmi tidak boleh dipakai SAVI untuk memperluas pencarian.
- Peraturan SUN dan playbook transaksi SUN adalah jenis sumber yang dapat diajukan; nama, versi, bagian, status, klasifikasi, dan pemilik dokumen wajib dicatat.

## Hal yang Tetap Terbuka

1. Role dan permission apa yang dimaksud dengan `admin`.
2. Apakah keputusan admin memerlukan pemilik materi, ketua tim, SME, atau reviewer hukum.
3. Daftar pasangan istilah lain yang benar-benar boleh dianggap setara.
4. Status debt switch, cash buyback, SBN, ORI, SBR, T&C, dan nama institusi lama.
5. Tanggal efektif siklus review pertama.
6. Mekanisme pencabutan istilah aktif tanpa menghapus audit perubahan.

## Batas Implementasi

- Tidak ada kandidat istilah yang dipromosikan hanya berdasarkan jawaban umum ini.
- `admin` bukan kewenangan konten tanpa permission dan separation of duties yang disetujui.
- SAVI tidak membuat tiket, menunjuk orang, mengirim pesan, atau mengubah glosarium secara otomatis.
- Penghapusan dari tampilan aktif tidak berarti menghapus audit atau riwayat teknis.

## Related Documents

- [open-questions.md](./open-questions.md)
- [glossary.md](./glossary.md)
- [decision-log.md](../12-governance/decision-log.md)
- [retrieval-strategy.md](../05-ai-rag/retrieval-strategy.md)
