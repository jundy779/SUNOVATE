import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { PageHeader, Panel, StatusTag } from "@/components/page-elements";
import { apiGet } from "@/lib/api";

export const metadata: Metadata = { title: "Validasi SAVI" };

type ValidationStatus =
  | "PENDING_SME_VALIDATION"
  | "PENDING_LEGAL_VALIDATION"
  | "NEEDS_REVISION"
  | "VERIFIED"
  | "REJECTED";

interface IntakeCase {
  id: string;
  question: string;
  draftAnswer: string;
  suppliedReferences: string[];
  candidateReferences: string[];
  validationNotes: string[];
  validationStatus: ValidationStatus;
  runtimeEligibility: "BLOCKED";
}

interface IntakeRegister {
  dataLabel: "MENTOR_PROVIDED_DRAFT";
  source: string;
  purpose: string;
  activationStatus: "EXCLUDED_FROM_RUNTIME";
  cases: IntakeCase[];
}

const STATUS_LABELS: Record<ValidationStatus, string> = {
  PENDING_SME_VALIDATION: "Menunggu validasi SME",
  PENDING_LEGAL_VALIDATION: "Menunggu validasi hukum",
  NEEDS_REVISION: "Perlu revisi",
  VERIFIED: "Terverifikasi",
  REJECTED: "Ditolak",
};

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

      <Panel
        eyebrow={`${intake.cases.length} pertanyaan`}
        title="Register validasi"
        action={<StatusTag tone="warning">Baca saja</StatusTag>}
      >
        <div className="validation-list">
          {intake.cases.map((item) => (
            <article className="validation-item" key={item.id}>
              <header>
                <span className="validation-id">{item.id}</span>
                <StatusTag tone={item.validationStatus === "NEEDS_REVISION" ? "risk" : "warning"}>
                  {STATUS_LABELS[item.validationStatus]}
                </StatusTag>
              </header>
              <h3>{item.question}</h3>
              <div className="validation-grid">
                <section>
                  <h4>Jawaban acuan awal</h4>
                  <p>{item.draftAnswer}</p>
                </section>
                <section>
                  <h4>Sumber yang diberikan</h4>
                  <ul>
                    {item.suppliedReferences.map((source) => <li key={source}>{source}</li>)}
                  </ul>
                  {item.candidateReferences.length ? (
                    <>
                      <h4>Kandidat sumber koreksi</h4>
                      <ul>
                        {item.candidateReferences.map((source) => <li key={source}>{source}</li>)}
                      </ul>
                    </>
                  ) : null}
                </section>
              </div>
              <section className="validation-notes">
                <h4>Catatan yang harus diselesaikan</h4>
                <ul>
                  {item.validationNotes.map((note) => <li key={note}>{note}</li>)}
                </ul>
              </section>
            </article>
          ))}
        </div>
      </Panel>
    </>
  );
}
