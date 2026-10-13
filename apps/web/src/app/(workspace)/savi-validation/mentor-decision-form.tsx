"use client";

import { useState } from "react";

interface MentorDecisionDraft {
  substantiveValidator: string;
  legalReviewer: string;
  finalApprover: string;
  reviewSequence: string;
  requiredSources: string;
  requiredSop: string;
  classificationAccess: string;
  refusalEscalation: string;
  reviewValidity: string;
  additionalNotes: string;
}

const EMPTY_DRAFT: MentorDecisionDraft = {
  substantiveValidator: "",
  legalReviewer: "",
  finalApprover: "",
  reviewSequence: "",
  requiredSources: "",
  requiredSop: "",
  classificationAccess: "",
  refusalEscalation: "",
  reviewValidity: "",
  additionalNotes: "",
};

const FIELD_GROUPS: Array<{
  title: string;
  description: string;
  fields: Array<{ name: keyof MentorDecisionDraft; label: string; placeholder: string }>;
}> = [
  {
    title: "Kewenangan validasi",
    description: "Tuliskan jabatan atau peran, bukan nama orang, agar keputusan tetap berlaku ketika terjadi pergantian pegawai.",
    fields: [
      {
        name: "substantiveValidator",
        label: "Siapa validator substansi untuk setiap topik SUN?",
        placeholder: "Contoh format: Ketua Tim/PIC sesuai topik, perlu dikonfirmasi mentor",
      },
      {
        name: "legalReviewer",
        label: "Siapa yang memeriksa ketepatan dasar hukum?",
        placeholder: "Jabatan atau unit reviewer hukum yang berwenang",
      },
      {
        name: "finalApprover",
        label: "Siapa pemberi persetujuan akhir sebelum jawaban aktif?",
        placeholder: "Jabatan approver akhir dan batas kewenangannya",
      },
    ],
  },
  {
    title: "Urutan dan bukti review",
    description: "Pastikan sistem tidak menyamakan pemeriksaan substansi, hukum, dan persetujuan akhir.",
    fields: [
      {
        name: "reviewSequence",
        label: "Bagaimana urutan review dan kondisi pengembalian untuk revisi?",
        placeholder: "Urutan tahap, pemisahan tugas, dan alasan revisi/penolakan",
      },
      {
        name: "requiredSources",
        label: "Sumber resmi apa yang wajib mendukung setiap jawaban?",
        placeholder: "Peraturan, dokumen resmi, atau sumber lain yang disahkan",
      },
      {
        name: "requiredSop",
        label: "SOP atau checklist internal apa yang wajib diperiksa?",
        placeholder: "Nama/kode SOP, pemilik dokumen, serta versi yang berlaku",
      },
    ],
  },
  {
    title: "Batas penggunaan SAVI",
    description: "Tentukan kapan jawaban boleh ditampilkan, dibatasi, atau harus dialihkan kepada pegawai berwenang.",
    fields: [
      {
        name: "classificationAccess",
        label: "Apa klasifikasi dan cakupan akses untuk jawaban serta sumbernya?",
        placeholder: "Klasifikasi, role yang boleh mengakses, dan batas tim",
      },
      {
        name: "refusalEscalation",
        label: "Dalam kondisi apa SAVI harus menolak atau mengeskalasi?",
        placeholder: "Misalnya bukti tidak cukup, data sensitif, atau membutuhkan keputusan pejabat",
      },
      {
        name: "reviewValidity",
        label: "Kapan jawaban wajib ditinjau ulang?",
        placeholder: "Pemicu perubahan regulasi/SOP, masa berlaku, dan jadwal review",
      },
    ],
  },
];

export function MentorDecisionForm() {
  const [draft, setDraft] = useState<MentorDecisionDraft>(EMPTY_DRAFT);
  const completed = Object.entries(draft)
    .filter(([key]) => key !== "additionalNotes")
    .filter(([, value]) => value.trim()).length;
  const total = Object.keys(EMPTY_DRAFT).length - 1;

  const updateField = (name: keyof MentorDecisionDraft, value: string) => {
    setDraft((current) => ({ ...current, [name]: value }));
  };

  return (
    <section className="mentor-decision" aria-labelledby="mentor-decision-title">
      <header className="mentor-decision-heading">
        <div>
          <p className="eyebrow">Open Question OQ-36</p>
          <h2 id="mentor-decision-title">Lembar keputusan mentor</h2>
          <p>
            Bahan diskusi untuk menetapkan tata kelola jawaban operasional SAVI. Isian tidak disimpan dan tidak mengaktifkan jawaban.
          </p>
        </div>
        <div className="mentor-decision-progress" aria-label={`${completed} dari ${total} pokok keputusan terisi`}>
          <strong>{completed}/{total}</strong>
          <span>pokok keputusan terisi</span>
        </div>
      </header>

      <form className="mentor-decision-form" onSubmit={(event) => event.preventDefault()}>
        {FIELD_GROUPS.map((group, index) => (
          <fieldset key={group.title}>
            <legend>
              <span>{String(index + 1).padStart(2, "0")}</span>
              {group.title}
            </legend>
            <p>{group.description}</p>
            <div className="mentor-decision-fields">
              {group.fields.map((field) => (
                <label key={field.name}>
                  <span>{field.label}</span>
                  <textarea
                    value={draft[field.name]}
                    onChange={(event) => updateField(field.name, event.target.value)}
                    placeholder={field.placeholder}
                    rows={3}
                  />
                </label>
              ))}
            </div>
          </fieldset>
        ))}

        <label className="mentor-decision-notes">
          <span>Catatan tambahan mentor</span>
          <textarea
            value={draft.additionalNotes}
            onChange={(event) => updateField("additionalNotes", event.target.value)}
            placeholder="Keputusan atau arahan lain yang perlu diterjemahkan ke requirement SUNOVATE"
            rows={4}
          />
        </label>

        <div className="mentor-decision-actions">
          <p>Konfirmasi resmi tetap dilakukan melalui mekanisme yang disetujui Direktorat SUN.</p>
          <button type="button" className="button button-secondary" onClick={() => setDraft(EMPTY_DRAFT)}>
            Kosongkan isian
          </button>
          <button type="button" className="button" onClick={() => window.print()}>
            Cetak lembar
          </button>
        </div>
      </form>
    </section>
  );
}
