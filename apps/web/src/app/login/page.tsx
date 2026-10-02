import type { Metadata } from "next";
import { LoginForm } from "./login-form";

export const metadata: Metadata = { title: "Masuk" };

export default function LoginPage() {
  return (
    <main className="auth-page" id="main-content">
      <section className="auth-panel" aria-labelledby="login-title">
        <p className="eyebrow">Akses pengembangan</p>
        <h1 id="login-title">Masuk ke SUNOVATE</h1>
        <p className="lede">
          Autentikasi lokal untuk pengguna simulasi. Mekanisme login produksi belum ditetapkan dan
          tidak terhubung ke SSO organisasi.
        </p>
        <LoginForm />
        <p className="data-label">SIMULATED_DATA. Jangan gunakan kredensial organisasi.</p>
      </section>
    </main>
  );
}
