import { StatusTag } from "@/components/page-elements";

export type GlossaryValidationStatus =
  | "IMPLEMENTED_SPELLING_ONLY"
  | "PENDING_MENTOR_VALIDATION"
  | "PENDING_SME_VALIDATION"
  | "PENDING_LEGAL_VALIDATION"
  | "REJECTED";

export interface GlossaryEntry {
  id: string;
  canonicalTerm: string;
  variants: string[];
  category: "SPELLING_VARIANT" | "DOMAIN_MAPPING" | "ABBREVIATION" | "HISTORICAL_NAME";
  definition: string;
  sourceReferences: string[];
  validationStatus: GlossaryValidationStatus;
  runtimeEligibility: "LIMITED_SPELLING_RETRY" | "BLOCKED";
  validationNotes: string[];
}

const STATUS_LABELS: Record<GlossaryValidationStatus, string> = {
  IMPLEMENTED_SPELLING_ONLY: "Aktif untuk variasi ejaan",
  PENDING_MENTOR_VALIDATION: "Menunggu pemeriksaan mentor",
  PENDING_SME_VALIDATION: "Menunggu pemeriksaan substansi",
  PENDING_LEGAL_VALIDATION: "Menunggu pemeriksaan hukum",
  REJECTED: "Ditolak",
};

const CATEGORY_LABELS: Record<GlossaryEntry["category"], string> = {
  SPELLING_VARIANT: "Variasi ejaan",
  DOMAIN_MAPPING: "Pemetaan istilah domain",
  ABBREVIATION: "Singkatan",
  HISTORICAL_NAME: "Nama lintas waktu",
};

export function GlossaryRegister({ entries }: { entries: GlossaryEntry[] }) {
  const active = entries.filter((entry) => entry.runtimeEligibility === "LIMITED_SPELLING_RETRY");

  return (
    <>
      <div className="validation-summary" aria-label="Ringkasan glosarium">
        <div>
          <strong>{entries.length}</strong>
          <span>Total istilah</span>
        </div>
        <div>
          <strong>{active.length}</strong>
          <span>Variasi ejaan aktif</span>
        </div>
        <div>
          <strong>{entries.length - active.length}</strong>
          <span>Masih diblokir</span>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Istilah utama</th>
              <th>Variasi</th>
              <th>Jenis</th>
              <th>Status pemeriksaan</th>
              <th>Dasar dan catatan</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id}>
                <td>
                  <strong>{entry.canonicalTerm}</strong>
                  <span className="table-detail">{entry.definition}</span>
                </td>
                <td>{entry.variants.join(", ")}</td>
                <td>{CATEGORY_LABELS[entry.category]}</td>
                <td>
                  <StatusTag tone={entry.runtimeEligibility === "BLOCKED" ? "warning" : "success"}>
                    {STATUS_LABELS[entry.validationStatus]}
                  </StatusTag>
                </td>
                <td>
                  <ul className="compact-list">
                    {entry.sourceReferences.map((source) => <li key={source}>{source}</li>)}
                    {entry.validationNotes.map((note) => <li key={note}>{note}</li>)}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
