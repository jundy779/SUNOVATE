import type { Metadata } from "next";
import Link from "next/link";
import { PublicSiteHeader } from "@/components/public-site-header";
import { UiIcon } from "@/components/ui-icons";
import { LoginForm } from "./login-form";

export const metadata: Metadata = { title: "Masuk" };

export default function LoginPage() {
  return (
    <main className="auth-page" id="main-content">
      <PublicSiteHeader compact />
      <div className="auth-layout">
        <section className="auth-context" aria-label="Tentang SUNOVATE">
          <div><p className="auth-wordmark">SUNOVATE</p><p className="auth-organization">Direktorat Surat Utang Negara</p></div>
          <blockquote>Menjaga pengetahuan, belajar dari pengalaman, berinovasi untuk meningkatkan kinerja.</blockquote>
          <div className="auth-principles"><span><UiIcon name="book" />Kelola pengetahuan</span><span><UiIcon name="chart" />Dukung pekerjaan</span><span><UiIcon name="users" />Tumbuh bersama</span></div>
        </section>
        <section className="auth-panel" aria-labelledby="login-title">
          <div className="auth-panel-inner">
            <p className="section-label">Akses ruang kerja</p><h1 id="login-title">Masuk ke ruang kerja SUNOVATE</h1>
            <p className="lede">Gunakan akun simulasi yang telah disediakan untuk mengakses pengetahuan dan pekerjaan sesuai kewenangan Anda.</p>
            <LoginForm />
            <Link className="auth-back-link" href="/">← Kembali ke beranda</Link>
            <div className="auth-security"><UiIcon name="shield" /><span>Akses dicatat dan dilindungi sesuai kebijakan keamanan informasi.</span></div>
            <p className="data-label">Lingkungan pengembangan · data contoh · jangan gunakan akun organisasi</p>
          </div>
        </section>
      </div>
    </main>
  );
}
