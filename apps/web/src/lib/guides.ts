/**
 * In-app quick guides (TASK-035). Each guide is shown only when the user holds one of its
 * permissions, so nobody is told about a page they cannot open. Labels match the screens.
 */
export interface GuideStep {
  title: string;
  detail: string;
}

export interface Guide {
  id: string;
  title: string;
  summary: string;
  anyOf: string[];
  href: string;
  linkLabel: string;
  steps: GuideStep[];
  note?: string;
}

export const GUIDES: Guide[] = [
  {
    id: "mencari",
    title: "Mencari dokumen dan pengetahuan",
    summary: "Temukan regulasi, panduan kerja, dan catatan pembelajaran yang boleh Anda lihat.",
    anyOf: ["search:query", "knowledge:read"],
    href: "/search",
    linkLabel: "Buka Pencarian",
    steps: [
      { title: "Ketik kata kunci di kotak pencarian", detail: "Kotak pencarian ada di bagian atas setiap halaman. Pakai istilah yang biasa dipakai di dokumen, misalnya nama proses, nama dokumen, atau periode." },
      { title: "Baca hasil dan sumbernya", detail: "Setiap hasil menampilkan judul, jenis, tim pemilik, klasifikasi, dan potongan isi. Hasil hanya mencakup pengetahuan yang sudah disetujui dan sesuai hak akses Anda." },
      { title: "Buka entri untuk detail lengkap", detail: "Klik judul untuk melihat isi, versi, dan tanggal pembaruan. Di menu Basis Pengetahuan Anda juga dapat menelusuri semua entri, lengkap dengan jenisnya, dan menyaringnya berdasarkan status." },
    ],
  },
  {
    id: "savi",
    title: "Bertanya kepada SAVI AI",
    summary: "Ajukan pertanyaan tentang SUN dan dapatkan jawaban yang menyebutkan sumbernya.",
    anyOf: ["hermes:query"],
    href: "/savi-ai",
    linkLabel: "Buka SAVI AI",
    steps: [
      { title: "Tulis pertanyaan yang jelas", detail: "Sebutkan nama dokumen, proses, periode, atau unit terkait. Contoh: \u201cApa metadata wajib saat mendaftarkan dokumen?\u201d Lalu tekan Kirim pertanyaan." },
      { title: "Periksa sumber yang digunakan", detail: "Angka dalam kurung seperti [1] menunjuk ke bagian Sumber yang digunakan di bawah jawaban. Buka sumbernya bila jawaban akan dipakai untuk pekerjaan." },
      { title: "Keputusan tetap di tangan Anda", detail: "SAVI AI membantu menemukan dan merangkum pengetahuan, bukan mengambil keputusan. Bila sumber tidak cukup, SAVI akan menyampaikannya dan menyarankan menghubungi pemilik pengetahuan." },
    ],
    note: "SAVI AI hanya menjawab pertanyaan seputar Surat Utang Negara dan tidak membaca dokumen rahasia.",
  },
  {
    id: "pekerjaan",
    title: "Memantau dan memperbarui pekerjaan",
    summary: "Lihat output, tugas, dan tindak lanjut tim, lalu perbarui statusnya.",
    anyOf: ["work:read"],
    href: "/work-monitoring",
    linkLabel: "Buka Monitoring Kerja",
    steps: [
      { title: "Pilih jenis data", detail: "Di Monitoring Kerja, pilih tab Output kerja, Tugas, Tahapan penting, Perlu tindak lanjut, atau Tindak lanjut." },
      { title: "Cari, saring, dan urutkan", detail: "Ketik sebagian judul di Cari judul, pilih Saring status atau Saring tim, dan klik judul kolom untuk mengurutkan, seperti di Excel." },
      { title: "Perbarui status", detail: "Bila Anda berwenang, klik Ubah pada baris pekerjaan lalu pilih status baru. Setiap perubahan tercatat dalam riwayat aktivitas." },
      { title: "Unduh ke Excel bila perlu", detail: "Tombol Unduh Excel menghasilkan berkas berisi data yang boleh Anda lihat, lengkap dengan filter. Jangan teruskan berkas kepada pihak yang tidak berwenang." },
    ],
  },
  {
    id: "rahasia",
    title: "Membaca dokumen rahasia",
    summary: "Dokumen rahasia hanya dapat dibaca di layar oleh pegawai yang diberi akses.",
    anyOf: ["document:read"],
    href: "/dokumen-rahasia",
    linkLabel: "Buka Dokumen Rahasia",
    steps: [
      { title: "Pilih dokumen dari daftar", detail: "Daftar hanya berisi dokumen yang aksesnya diberikan kepada Anda. Bila kosong, berarti belum ada dokumen rahasia untuk Anda." },
      { title: "Setujui pernyataan kerahasiaan", detail: "Pernyataan wajib disetujui setiap kali dokumen dibuka, lalu tekan Buka dokumen." },
      { title: "Baca per halaman", detail: "Halaman tampil sebagai gambar dengan tanda air nama dan waktu akses Anda. Dokumen tidak dapat diunduh, disalin, atau dicetak, dan setiap halaman yang dibuka tercatat." },
    ],
  },
  {
    id: "akses-rahasia",
    title: "Menentukan pembaca dokumen rahasia",
    summary: "Untuk ketua tim dan Kasubdit PMP: memberi dan mencabut akses baca.",
    anyOf: ["secure_document:manage_team", "secure_document:manage_all"],
    href: "/dokumen-rahasia/kelola",
    linkLabel: "Buka Kelola akses baca",
    steps: [
      { title: "Buka Kelola akses baca", detail: "Tombolnya ada di halaman Dokumen Rahasia. Ketua tim melihat dokumen timnya; Kasubdit PMP melihat dokumen seluruh tim." },
      { title: "Beri akses dengan email pegawai", detail: "Isi email pegawai lalu tekan Beri akses baca. Pegawai harus aktif dan memiliki tingkat kerahasiaan yang cukup." },
      { title: "Cabut akses bila tidak diperlukan", detail: "Tekan Cabut akses pada nama pembaca. Penampil yang sedang terbuka langsung tertutup." },
    ],
  },
];

export function visibleGuides(permissions: readonly string[]): Guide[] {
  const granted = new Set(permissions);
  return GUIDES.filter((guide) => guide.anyOf.some((permission) => granted.has(permission)));
}
