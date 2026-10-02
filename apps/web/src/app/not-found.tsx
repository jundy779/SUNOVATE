import Link from "next/link";

export default function NotFound() {
  return (
    <main className="auth-page" id="main-content">
      <section className="auth-panel" aria-labelledby="not-found-title">
        <p className="eyebrow">404</p>
        <h1 id="not-found-title">Data atau halaman tidak ditemukan</h1>
        <p className="lede">
          Halaman tidak tersedia, atau data berada di luar cakupan akses Anda.
        </p>
        <Link className="button" href="/dashboard">
          Kembali ke dashboard
        </Link>
      </section>
    </main>
  );
}
