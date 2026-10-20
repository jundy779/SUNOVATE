import Image from "next/image";
import Link from "next/link";

export function PublicSiteHeader({ compact = false }: { compact?: boolean }) {
  return (
    <>
      <div className="gov-bar">
        <span>Kementerian Keuangan Republik Indonesia</span>
        <span>Direktorat Jenderal Pengelolaan Pembiayaan dan Risiko</span>
        <span className="gov-bar-lang">Bahasa Indonesia</span>
      </div>
      <header className="site-header">
        <Link className="site-brand" href="/" aria-label="Beranda SUNOVATE">
          <Image src="/brand/logo-dsun.png" alt="Direktorat Surat Utang Negara" width={122} height={54} priority />
          <span className="site-wordmark">
            <strong>SUNOVATE</strong>
            <small>Direktorat Surat Utang Negara</small>
          </span>
        </Link>
        {!compact ? (
          <nav className="site-nav" aria-label="Navigasi beranda">
            <a href="#siklus">Siklus pengetahuan</a>
            <a href="#akses">Layanan</a>
            <a href="#tentang">Tentang</a>
            <a href="#tata-kelola">Tata kelola</a>
          </nav>
        ) : null}
        <Link className="button site-cta" href={compact ? "/" : "/login"}>
          {compact ? "Beranda" : "Masuk"}
        </Link>
      </header>
    </>
  );
}
