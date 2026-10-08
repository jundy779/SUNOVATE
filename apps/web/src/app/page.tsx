import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <main className="landing" id="main-content">
      <header className="public-header">
        <Link className="public-brand" href="/" aria-label="SUNOVATE beranda">
          <Image src="/brand/logo-dsun.png" alt="Direktorat Surat Utang Negara" width={138} height={61} priority />
          <span className="brand-divider" aria-hidden="true" />
          <span className="product-wordmark"><strong>SUNOVATE</strong><small>Knowledge &amp; transformation workspace</small></span>
        </Link>
        <Link className="button secondary" href="/login">Masuk ke sistem</Link>
      </header>

      <section className="landing-hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">DJPPR · Kementerian Keuangan RI</p>
          <h1 id="hero-title">Pengetahuan organisasi yang terjaga, terhubung, dan dapat ditelusuri.</h1>
          <p className="hero-lede">SUN Organizational Values and Transformation through Experience mendukung pengelolaan pengetahuan, pemantauan kerja, dan pencarian informasi berbasis sumber di lingkungan Direktorat Surat Utang Negara.</p>
          <div className="hero-actions">
            <Link className="button" href="/login">Akses SUNOVATE</Link>
            <a className="text-link" href="#kapabilitas">Lihat kapabilitas</a>
          </div>
        </div>
        <aside className="hero-statement" aria-label="Tagline SUNOVATE">
          <div className="statement-topline"><span className="statement-index">01</span><span>Nilai utama</span></div>
          <blockquote>Menjaga pengetahuan, belajar dari pengalaman, berinovasi untuk meningkatkan kinerja.</blockquote>
          <p>Prototipe pengembangan · seluruh data demonstrasi berlabel SIMULATED_DATA</p>
        </aside>
      </section>

      <section className="capability-section" id="kapabilitas" aria-labelledby="capability-title">
        <div className="section-intro">
          <p className="eyebrow">Kapabilitas utama</p>
          <h2 id="capability-title">Satu ruang kerja untuk pengetahuan dan koordinasi</h2>
          <p>Fitur disusun dengan kontrol akses, klasifikasi, dan jejak audit sebagai fondasi.</p>
        </div>
        <div className="capability-list">
          <article><span>01</span><div><h3>Basis Pengetahuan</h3><p>Metadata, versi, dan sumber pengetahuan yang terstruktur dan dapat ditelusuri.</p></div></article>
          <article><span>02</span><div><h3>SAVI AI</h3><p>Asisten berbasis sumber yang menjawab dalam ruang lingkup SUN dan menyertakan sitasi.</p></div></article>
          <article><span>03</span><div><h3>Monitoring Kerja</h3><p>Ringkasan output, tugas, dan tindak lanjut sesuai kewenangan pengguna.</p></div></article>
        </div>
      </section>

      <footer className="public-footer">
        <span>SUNOVATE · Prototipe pengembangan</span>
        <span>Bukan sistem transaksi atau pengambilan keputusan keuangan</span>
      </footer>
    </main>
  );
}
