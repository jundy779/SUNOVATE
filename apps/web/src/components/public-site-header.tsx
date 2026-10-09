import Image from "next/image";
import Link from "next/link";

export function PublicSiteHeader({ compact = false }: { compact?: boolean }) {
  return (
    <>
      <div className="institution-bar">
        <span>Kementerian Keuangan Republik Indonesia</span>
        <span>Direktorat Jenderal Pengelolaan Pembiayaan dan Risiko</span>
        <span className="institution-tools">Bahasa Indonesia · Aksesibilitas</span>
      </div>
      <header className="public-header">
        <Link className="public-brand" href="/" aria-label="SUNOVATE beranda">
          <Image src="/brand/logo-dsun.png" alt="Direktorat Surat Utang Negara" width={138} height={61} priority />
          <span className="brand-divider" aria-hidden="true" />
          <span className="product-wordmark"><strong>SUNOVATE</strong><small>Direktorat Surat Utang Negara</small></span>
        </Link>
        {!compact ? <nav className="public-nav" aria-label="Navigasi utama"><a href="#tentang">Tentang</a><a href="#akses">Akses Utama</a><a href="#pengetahuan">Knowledge Hub</a><Link href="/hermes">SAVI AI</Link></nav> : null}
        <Link className="button public-login-link" href={compact ? "/" : "/login"}>{compact ? "Beranda" : "Masuk"}</Link>
      </header>
    </>
  );
}
