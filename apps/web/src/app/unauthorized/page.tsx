import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Akses dibatasi" };

export default function UnauthorizedPage() {
  return (
    <main className="auth-page" id="main-content">
      <section className="auth-panel" aria-labelledby="unauthorized-title">
        <p className="eyebrow">403 - Akses dibatasi</p>
        <h1 id="unauthorized-title">Anda tidak memiliki izin</h1>
        <p className="lede">
          Akses ditentukan oleh izin, cakupan tim, dan klasifikasi data, serta diperiksa oleh API.
          Hubungi administrator bila Anda memerlukan akses.
        </p>
        <Link className="button" href="/dashboard">
          Kembali ke dashboard
        </Link>
      </section>
    </main>
  );
}
