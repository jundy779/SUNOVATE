import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { PageHeader, Panel, StatusTag } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { MentorDecisionForm } from "./mentor-decision-form";
import { ValidationRegister, type IntakeCase } from "./validation-register";

export const metadata: Metadata = { title: "Validasi SAVI" };

interface IntakeRegister {
  dataLabel: "MENTOR_PROVIDED_DRAFT";
  source: string;
  purpose: string;
  activationStatus: "EXCLUDED_FROM_RUNTIME";
  cases: IntakeCase[];
}

export default async function SaviValidationPage() {
  const { data: me } = await apiGet<Principal>("/auth/me");
  const canReview = me.permissions.includes("knowledge:review");
  const canSeeAllTeams = me.permissions.includes("scope:all_teams");
  if (!canReview || !canSeeAllTeams) redirect("/unauthorized");

  const { data: intake } = await apiGet<IntakeRegister>("/hermes/sme-question-intake");

  return (
    <>
      <PageHeader
        eyebrow="Tata kelola SAVI AI"
        title="Validasi pertanyaan mentor"
        description="Register baca saja untuk memeriksa jawaban acuan, dasar sumber, dan kekurangan bukti sebelum sebuah pertanyaan boleh masuk pengujian aktif SAVI."
        action={<span className="data-label">MENTOR_PROVIDED_DRAFT</span>}
      />

      <section className="governance-strip" aria-label="Status aktivasi">
        <div>
          <p className="eyebrow">Status runtime</p>
          <h2>Belum terhubung ke jawaban SAVI</h2>
          <p>Seluruh kasus diblokir sampai validasi substansi, hukum, SOP, klasifikasi, dan hak akses selesai.</p>
        </div>
        <StatusTag tone="risk">BLOCKED</StatusTag>
      </section>

      <MentorDecisionForm />

      <Panel
        eyebrow={`${intake.cases.length} pertanyaan`}
        title="Register validasi"
        action={<StatusTag tone="warning">Baca saja</StatusTag>}
      >
        <ValidationRegister cases={intake.cases} />
      </Panel>
    </>
  );
}
