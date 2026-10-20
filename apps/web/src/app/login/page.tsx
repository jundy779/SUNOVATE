import type { Metadata } from "next";
import Link from "next/link";
import { PublicSiteHeader } from "@/components/public-site-header";
import { UiIcon } from "@/components/ui-icons";
import { LoginForm } from "./login-form";

export const metadata: Metadata = { title: "Masuk" };

const PILOT_TEAMS = ["PPSUN", "AKPSUN", "PSUN", "PPPSUN", "DHTV", "SUN Tematik", "MONEV"] as const;

export default function LoginPage() {
  return (
    <main className="login" id="main-content">
      <PublicSiteHeader compact />
      <div className="login-layout">
        <section className="login-context" aria-label="Tentang SUNOVATE">
          <div>
            <p className="login-wordmark">SUNOVATE</p>
            <p className="login-expansion">SUN Organizational Values and Transformation through Experience</p>
          </div>
          <p className="login-motto">
            <span>Menjaga pengetahuan,</span>
            <span>belajar dari pengalaman,</span>
            <span>berinovasi untuk meningkatkan kinerja.</span>
          </p>
          <div className="login-teams">
            <p>Tim kerja tahap uji coba</p>
            <ul>{PILOT_TEAMS.map((team) => <li key={team}>{team}</li>)}</ul>
          </div>
        </section>

        <section className="login-panel" aria-labelledby="login-title">
          <div className="login-panel-inner">
            <h1 id="login-title">Masuk ke SUNOVATE</h1>
            <p className="login-lede">
              Pilih akun pengembangan yang tersedia. Isi yang tampil setelah masuk mengikuti tim dan kewenangan akun tersebut.
            </p>
            <LoginForm />
            <div className="login-security">
              <UiIcon name="shield" />
              <span>Setiap akses tercatat. Jangan gunakan akun atau kata sandi organisasi di lingkungan ini.</span>
            </div>
            <Link className="text-link" href="/">Kembali ke beranda</Link>
          </div>
        </section>
      </div>
    </main>
  );
}
