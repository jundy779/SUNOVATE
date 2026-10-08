import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { LoginForm } from "./login-form";

export const metadata: Metadata = { title: "Masuk" };

export default function LoginPage() {
  return (
    <main className="auth-page" id="main-content">
      <section className="auth-context" aria-label="Tentang SUNOVATE">
        <Link className="auth-brand" href="/" aria-label="SUNOVATE beranda">
          <Image src="/brand/logo-dsun.png" alt="Direktorat Surat Utang Negara" width={154} height={69} priority />
          <span>SUNOVATE</span>
        </Link>
        <div>
          <p className="eyebrow">Direktorat Surat Utang Negara</p>
          <h1>Menjaga pengetahuan organisasi tetap utuh dan mudah ditemukan.</h1>
          <p>Sistem mendukung pengelolaan pengetahuan dan koordinasi kerja sesuai kewenangan pengguna.</p>
        </div>
        <p className="auth-tagline">Menjaga pengetahuan, belajar dari pengalaman, berinovasi untuk meningkatkan kinerja.</p>
      </section>
      <section className="auth-panel" aria-labelledby="login-title">
        <div className="auth-panel-inner">
          <p className="eyebrow">Akses pengembangan</p>
          <h2 id="login-title">Masuk ke SUNOVATE</h2>
          <p className="lede">Gunakan akun simulasi untuk meninjau prototipe. Akses ini belum terhubung ke SSO organisasi.</p>
          <LoginForm />
          <p className="data-label">SIMULATED_DATA · jangan gunakan kredensial organisasi</p>
        </div>
      </section>
    </main>
  );
}
