import type { Metadata } from "next";
import Link from "next/link";
import type { Principal } from "@sunovate/contracts";
import { apiGet } from "@/lib/api";
import { visibleGuides } from "@/lib/guides";

export const metadata: Metadata = { title: "Panduan Singkat" };

export default async function GuidePage() {
  const { data: principal } = await apiGet<Principal>("/auth/me");
  const guides = visibleGuides(principal.permissions);
  return (
    <div className="guide">
      <header className="db-masthead">
        <div>
          <p className="kicker">Panduan singkat</p>
          <h1>Cara memakai SUNOVATE</h1>
          <p className="db-standfirst">
            Langkah dasar untuk pekerjaan yang paling sering dilakukan. Panduan yang tampil menyesuaikan kewenangan akun
            Anda.
          </p>
        </div>
      </header>

      <nav className="guide-index" aria-label="Daftar panduan">
        <ol>
          {guides.map((guide) => (
            <li key={guide.id}><a href={`#${guide.id}`}>{guide.title}</a></li>
          ))}
        </ol>
      </nav>

      {guides.map((guide) => (
        <section className="guide-section" id={guide.id} key={guide.id} aria-labelledby={`${guide.id}-title`}>
          <header className="ed-head ed-head-split">
            <div>
              <h2 id={`${guide.id}-title`}>{guide.title}</h2>
              <p>{guide.summary}</p>
            </div>
            <Link className="text-link" href={guide.href}>{guide.linkLabel}</Link>
          </header>
          <ol className="guide-steps">
            {guide.steps.map((step) => (
              <li key={step.title}>
                <strong>{step.title}</strong>
                <span>{step.detail}</span>
              </li>
            ))}
          </ol>
          {guide.note ? <p className="guide-note">{guide.note}</p> : null}
        </section>
      ))}

      <p className="db-note">
        Butuh bantuan lain? Hubungi pengelola pengetahuan tim Anda. Seluruh isi di lingkungan ini memakai data contoh.
      </p>
    </div>
  );
}
