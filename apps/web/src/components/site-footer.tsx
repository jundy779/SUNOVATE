import Image from "next/image";
import Link from "next/link";

const YEAR = 2026;

/** Institutional footer for public pages; `compact` keeps only the bottom bar (login page). */
export function SiteFooter({ compact = false }: { compact?: boolean }) {
  const version = process.env.NEXT_PUBLIC_APP_VERSION;
  return (
    <footer className={compact ? "site-footer site-footer-compact" : "site-footer"}>
      {!compact ? (
        <div className="site-footer-main">
          <div className="site-footer-brand">
            <Image src="/brand/logo-dsun.png" alt="Direktorat Surat Utang Negara" width={110} height={49} />
            <strong>SUNOVATE</strong>
            <span>SUN Organizational Values and Transformation through Experience</span>
          </div>
          <nav aria-label="Tautan kaki halaman">
            <h2>Jelajahi</h2>
            <ul>
              <li><a href="#siklus">Siklus pengetahuan</a></li>
              <li><a href="#akses">Layanan</a></li>
              <li><a href="#tentang">Tentang</a></li>
              <li><a href="#tata-kelola">Tata kelola</a></li>
              <li><Link href="/login">Masuk</Link></li>
            </ul>
          </nav>
          <div>
            <h2>Instansi</h2>
            <ul>
              <li>Direktorat Surat Utang Negara</li>
              <li>Direktorat Jenderal Pengelolaan Pembiayaan dan Risiko</li>
              <li>Kementerian Keuangan Republik Indonesia</li>
            </ul>
          </div>
          <div>
            <h2>Batas layanan</h2>
            <p>SUNOVATE bukan sistem transaksi dan tidak mengambil keputusan keuangan. Keputusan tetap pada pegawai yang berwenang.</p>
          </div>
        </div>
      ) : null}
      <div className="site-footer-bottom">
        <span>© {YEAR} Direktorat Surat Utang Negara, DJPPR, Kementerian Keuangan</span>
        <span>{version ? `Versi ${version} · ` : ""}Lingkungan pengembangan, data contoh</span>
      </div>
    </footer>
  );
}

/** Slim footer at the bottom of every workspace page. */
export function WorkspaceFooter() {
  const version = process.env.NEXT_PUBLIC_APP_VERSION;
  return (
    <footer className="workspace-footer">
      <span>© {YEAR} Direktorat Surat Utang Negara, DJPPR, Kementerian Keuangan</span>
      <span>SUNOVATE{version ? ` versi ${version}` : ""} · Data contoh, belum terhubung ke layanan operasional</span>
    </footer>
  );
}
