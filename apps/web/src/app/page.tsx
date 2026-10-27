import Link from "next/link";
import { KnowledgeCycle } from "@/components/knowledge-cycle";
import { PublicSiteHeader } from "@/components/public-site-header";
import { UiIcon, type IconName } from "@/components/ui-icons";

const services: { label: string; detail: string; icon: IconName; href: string }[] = [
  { label: "Basis pengetahuan", detail: "Regulasi, panduan kerja, dan catatan pembelajaran yang sudah diperiksa", icon: "book", href: "/knowledge" },
  { label: "SAVI AI", detail: "Pertanyaan tentang SUN dijawab dari sumber yang boleh Anda akses", icon: "chat", href: "/savi-ai" },
  { label: "Monitoring kerja", detail: "Output, tenggat, dan tindak lanjut tim dalam satu tempat", icon: "chart", href: "/work-monitoring" },
  { label: "Pencarian", detail: "Telusuri dokumen dan pengetahuan lintas tim sesuai kewenangan", icon: "search", href: "/search" },
];

const answerRules = [
  ["Hanya dari sumber yang diterbitkan", "Draf dan dokumen yang belum disetujui tidak dipakai untuk menjawab."],
  ["Selalu menyebut rujukan", "Setiap jawaban menunjukkan dokumen asalnya agar dapat diperiksa kembali."],
  ["Berhenti ketika bukti kurang", "SAVI AI menyatakan keterbatasannya dan mengarahkan Anda ke pemilik pengetahuan."],
] as const;

const governance = [
  ["Akses sesuai kewenangan", "Isi yang tampil mengikuti tim, peran, dan tingkat kerahasiaan dokumen."],
  ["Jejak yang tercatat", "Perubahan penting dan persetujuan tersimpan untuk kebutuhan pemeriksaan."],
  ["Keputusan tetap pada manusia", "SUNOVATE membantu menemukan dan menyusun, bukan menetapkan kebijakan."],
] as const;

export default function Home() {
  return (
    <main className="site" id="main-content">
      <PublicSiteHeader />

      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-text">
          <p className="kicker">Memori institusional Direktorat Surat Utang Negara</p>
          <h1 id="hero-title">Pengetahuan organisasi yang tetap utuh ketika orangnya berganti.</h1>
          <p className="hero-standfirst">
            SUNOVATE menyimpan pengalaman kerja, keputusan, dan rujukan SUN dalam satu tempat yang tertata,
            sehingga konteks sebuah kebijakan masih dapat ditelusuri bertahun-tahun kemudian.
          </p>
          <div className="hero-actions">
            <Link className="button" href="/login">Akses SUNOVATE</Link>
            <a className="text-link" href="#siklus">Lihat cara kerjanya</a>
          </div>
        </div>
        <div className="hero-figure" id="siklus">
          <KnowledgeCycle />
        </div>
      </section>

      <section className="service-rail" id="akses" aria-labelledby="services-title">
        <h2 id="services-title">Layanan SUNOVATE</h2>
        <ul>
          {services.map((service) => (
            <li key={service.label}>
              <Link href={service.href}>
                <UiIcon name={service.icon} />
                <span>
                  <strong>{service.label}</strong>
                  <small>{service.detail}</small>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="briefing" aria-label="Tentang SUNOVATE">
        <article className="briefing-lead" id="tentang" aria-labelledby="about-title">
          <p className="kicker">Tentang</p>
          <h2 id="about-title">Konteks keputusan sering hilang lebih cepat daripada dokumennya.</h2>
          <p>
            Bahan rapat, catatan lelang, dan kajian tersebar di banyak tempat. Yang paling cepat hilang justru alasan
            di balik sebuah keputusan, terutama ketika pegawai yang memahaminya berpindah tugas.
          </p>
          <p>
            SUNOVATE membantu menangkap, memvalidasi, dan menghubungkan pengetahuan itu, lalu menyajikannya kembali
            kepada pimpinan, ketua tim, dan pegawai baru sesuai kewenangan masing-masing.
          </p>
          <blockquote>
            Menjaga pengetahuan, belajar dari pengalaman, berinovasi untuk meningkatkan kinerja.
          </blockquote>
        </article>

        <div className="briefing-side">
          <section aria-labelledby="savi-title">
            <header className="ed-head">
              <h2 id="savi-title">Cara SAVI AI menjawab</h2>
              <p>Asisten pengetahuan untuk pertanyaan seputar Surat Utang Negara</p>
            </header>
            <dl className="rule-list">
              {answerRules.map(([term, detail]) => (
                <div key={term}><dt>{term}</dt><dd>{detail}</dd></div>
              ))}
            </dl>
          </section>
          <section id="tata-kelola" aria-labelledby="governance-title">
            <header className="ed-head">
              <h2 id="governance-title">Tata kelola</h2>
              <p>Pengaman yang berlaku sejak dokumen pertama diunggah</p>
            </header>
            <dl className="rule-list">
              {governance.map(([term, detail]) => (
                <div key={term}><dt>{term}</dt><dd>{detail}</dd></div>
              ))}
            </dl>
          </section>
        </div>
      </section>

      <p className="env-notice">
        <UiIcon name="shield" />
        <span>
          <strong>Lingkungan pengembangan.</strong> Seluruh isi memakai data contoh dan belum terhubung ke layanan operasional.
        </span>
      </p>

      <footer className="site-footer">
        <div>
          <strong>SUNOVATE</strong>
          <span>SUN Organizational Values and Transformation through Experience</span>
        </div>
        <span>Direktorat Surat Utang Negara, DJPPR, Kementerian Keuangan</span>
        <span>Bukan sistem transaksi atau pengambilan keputusan keuangan</span>
        <span>Versi {process.env.NEXT_PUBLIC_APP_VERSION}</span>
      </footer>
    </main>
  );
}
