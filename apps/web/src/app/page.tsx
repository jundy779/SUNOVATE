import Link from "next/link";
import { PublicSiteHeader } from "@/components/public-site-header";
import { UiIcon, type IconName } from "@/components/ui-icons";

const primaryAccess: { label: string; detail: string; icon: IconName; href: string }[] = [
  { label: "Monitoring Kerja", detail: "Output, tugas, dan tindak lanjut", icon: "chart", href: "/work-monitoring" },
  { label: "Basis Pengetahuan", detail: "Pengetahuan terstruktur dan terlacak", icon: "book", href: "/knowledge" },
  { label: "SAVI AI", detail: "Jawaban berbasis sumber", icon: "chat", href: "/savi-ai" },
  { label: "Pencarian", detail: "Temukan informasi lintas sumber", icon: "search", href: "/search" },
];

const knowledgeAreas = [
  ["Regulasi dan kebijakan", "Rujukan yang terkelola dengan metadata, status, serta riwayat versi."],
  ["SOP dan panduan kerja", "Langkah kerja yang dapat dipelajari kembali dan disempurnakan bersama."],
  ["Catatan pembelajaran", "Pengalaman pelaksanaan yang disimpan sebagai memori organisasi."],
  ["Bahan rapat dan arsip", "Dokumen pendukung yang dapat ditelusuri sesuai hak akses pengguna."],
] as const;

export default function Home() {
  return (
    <main className="landing" id="main-content">
      <PublicSiteHeader />
      <section className="landing-hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <h1 id="hero-title">Pengetahuan yang terjaga, kinerja yang berkelanjutan.</h1>
          <p className="hero-lede">SUN Organizational Values and Transformation through Experience menghubungkan pengetahuan, pengalaman, dan koordinasi kerja Direktorat Surat Utang Negara dalam satu ruang yang tertata.</p>
          <div className="hero-actions"><Link className="button button-gold" href="/login">Masuk ke SUNOVATE</Link><a className="button button-outline-light" href="#pengetahuan">Jelajahi Basis Pengetahuan</a></div>
        </div>
        <div className="hero-image" role="img" aria-label="Ilustrasi arsitektur institusi pelayanan publik" />
      </section>
      <section className="access-rail" id="akses" aria-labelledby="access-title">
        <h2 id="access-title">Akses utama</h2>
        <div className="access-links">
          {primaryAccess.map((item) => <Link href={item.href} key={item.label}><UiIcon name={item.icon} /><span><strong>{item.label}</strong><small>{item.detail}</small></span><span aria-hidden="true">→</span></Link>)}
        </div>
      </section>
      <section className="institutional-content" id="tentang">
        <article className="about-sunovate" aria-labelledby="about-title">
          <p className="section-label">Tentang SUNOVATE</p><h2 id="about-title">Memori organisasi yang dapat dipakai kembali.</h2>
          <p>SUNOVATE membantu Direktorat Surat Utang Negara menjaga kesinambungan pengetahuan, mendokumentasikan pengalaman kerja, dan menemukan informasi berbasis sumber sesuai kewenangan pengguna.</p>
          <blockquote>“Menjaga pengetahuan, belajar dari pengalaman, berinovasi untuk meningkatkan kinerja.”</blockquote>
          <div className="governance-note"><UiIcon name="shield" /><span><strong>Dirancang dengan tata kelola</strong>Kontrol akses, klasifikasi informasi, sitasi sumber, dan jejak audit menjadi bagian dari fondasi sistem.</span></div>
        </article>
        <article className="knowledge-directory" id="pengetahuan" aria-labelledby="knowledge-title">
          <div className="content-heading"><div><p className="section-label">Basis Pengetahuan</p><h2 id="knowledge-title">Ruang pengetahuan</h2></div><Link className="text-link" href="/knowledge">Lihat seluruh pengetahuan</Link></div>
          <div className="knowledge-list">{knowledgeAreas.map(([title, detail], index) => <div key={title}><span>{String(index + 1).padStart(2, "0")}</span><div><h3>{title}</h3><p>{detail}</p></div></div>)}</div>
        </article>
      </section>
      <section className="prototype-notice" aria-label="Status lingkungan"><div><strong>Lingkungan pengembangan</strong><span>Seluruh informasi yang tampil merupakan data contoh.</span></div><span>Belum terhubung ke layanan operasional</span></section>
      <footer className="public-footer"><div><strong>SUNOVATE</strong><span>Direktorat Surat Utang Negara</span></div><span>SUN Organizational Values and Transformation through Experience</span><span>Prototipe pengembangan · bukan sistem transaksi atau pengambilan keputusan keuangan</span></footer>
    </main>
  );
}
