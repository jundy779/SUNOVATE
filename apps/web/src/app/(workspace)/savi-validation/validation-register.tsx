"use client";

import { useMemo, useState } from "react";
import { StatusTag, type Tone } from "@/components/page-elements";

export type ValidationStatus =
  | "PENDING_SME_VALIDATION"
  | "PENDING_LEGAL_VALIDATION"
  | "NEEDS_REVISION"
  | "VERIFIED"
  | "REJECTED";

export interface IntakeCase {
  id: string;
  question: string;
  draftAnswer: string;
  suppliedReferences: string[];
  candidateReferences: string[];
  validationNotes: string[];
  validationStatus: ValidationStatus;
  runtimeEligibility: "BLOCKED";
}

export const STATUS_LABELS: Record<ValidationStatus, string> = {
  PENDING_SME_VALIDATION: "Menunggu validasi SME",
  PENDING_LEGAL_VALIDATION: "Menunggu validasi hukum",
  NEEDS_REVISION: "Perlu revisi",
  VERIFIED: "Terverifikasi",
  REJECTED: "Ditolak",
};

const STATUS_TONES: Record<ValidationStatus, Tone> = {
  PENDING_SME_VALIDATION: "warning",
  PENDING_LEGAL_VALIDATION: "warning",
  NEEDS_REVISION: "risk",
  VERIFIED: "success",
  REJECTED: "risk",
};

const ALL_STATUSES = "ALL";

function searchableText(item: IntakeCase) {
  return [
    item.id,
    item.question,
    item.draftAnswer,
    ...item.suppliedReferences,
    ...item.candidateReferences,
    ...item.validationNotes,
  ]
    .join(" ")
    .toLocaleLowerCase("id-ID");
}

export function ValidationRegister({ cases }: { cases: IntakeCase[] }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<ValidationStatus | typeof ALL_STATUSES>(ALL_STATUSES);

  const counts = useMemo(
    () =>
      cases.reduce<Partial<Record<ValidationStatus, number>>>((result, item) => {
        result[item.validationStatus] = (result[item.validationStatus] ?? 0) + 1;
        return result;
      }, {}),
    [cases],
  );

  const availableStatuses = useMemo(
    () => (Object.keys(STATUS_LABELS) as ValidationStatus[]).filter((item) => counts[item]),
    [counts],
  );

  const normalizedQuery = query.trim().toLocaleLowerCase("id-ID");
  const filteredCases = useMemo(
    () =>
      cases.filter(
        (item) =>
          (status === ALL_STATUSES || item.validationStatus === status) &&
          (!normalizedQuery || searchableText(item).includes(normalizedQuery)),
      ),
    [cases, normalizedQuery, status],
  );

  const resetFilters = () => {
    setQuery("");
    setStatus(ALL_STATUSES);
  };

  return (
    <>
      <div className="validation-summary" aria-label="Ringkasan status validasi">
        <div>
          <strong>{cases.length}</strong>
          <span>Total pertanyaan</span>
        </div>
        {availableStatuses.map((item) => (
          <div key={item}>
            <strong>{counts[item]}</strong>
            <span>{STATUS_LABELS[item]}</span>
          </div>
        ))}
      </div>

      <div className="validation-toolbar">
        <label className="validation-search">
          <span>Cari dalam register</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Pertanyaan, sumber, atau catatan"
          />
        </label>
        <label>
          <span>Status validasi</span>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as ValidationStatus | typeof ALL_STATUSES)}
          >
            <option value={ALL_STATUSES}>Semua status</option>
            {availableStatuses.map((item) => (
              <option value={item} key={item}>
                {STATUS_LABELS[item]} ({counts[item]})
              </option>
            ))}
          </select>
        </label>
        <div className="validation-toolbar-actions">
          <button type="button" className="button button-secondary" onClick={resetFilters}>
            Atur ulang
          </button>
          <button type="button" className="button button-secondary" onClick={() => window.print()}>
            Cetak register
          </button>
        </div>
      </div>

      <p className="validation-result-count" role="status" aria-live="polite">
        Menampilkan {filteredCases.length} dari {cases.length} pertanyaan
      </p>

      {filteredCases.length ? (
        <div className="validation-list">
          {filteredCases.map((item) => (
            <article className="validation-item" key={item.id}>
              <header>
                <span className="validation-id">{item.id}</span>
                <StatusTag tone={STATUS_TONES[item.validationStatus]}>
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
      ) : (
        <section className="validation-empty" role="status">
          <h3>Tidak ada pertanyaan yang cocok</h3>
          <p>Ubah kata pencarian atau status validasi untuk melihat data lainnya.</p>
          <button type="button" className="button button-secondary" onClick={resetFilters}>
            Tampilkan semua
          </button>
        </section>
      )}
    </>
  );
}
