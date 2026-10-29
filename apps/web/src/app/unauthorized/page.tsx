import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Akses dibatasi" };

export default function UnauthorizedPage() {
  return (
    <main className="auth-page" id="main-content">
      <section className="auth-panel" aria-labelledby="unauthorized-title">
        <p className="eyebrow">Akses dibatasi</p>
        <h1 id="unauthorized-title">Anda tidak memiliki izin</h1>
        <p className="lede">
          Akses ditentukan oleh kewenangan, cakupan tim, dan klasifikasi informasi Anda. Hubungi
          pengelola sistem bila Anda memerlukan akses tambahan.
        </p>
        <Link className="button" href="/dashboard">
          Kembali ke dashboard
        </Link>
      </section>
    </main>
  );
}
