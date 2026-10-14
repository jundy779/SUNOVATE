import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GlossaryRegister, type GlossaryEntry } from "./glossary-register";

const ENTRIES: GlossaryEntry[] = [
  {
    id: "GLS-001",
    canonicalTerm: "Setelmen",
    variants: ["settlement"],
    category: "SPELLING_VARIANT",
    definition: "Variasi ejaan terbatas.",
    sourceReferences: ["PMK 111/2024"],
    validationStatus: "IMPLEMENTED_SPELLING_ONLY",
    runtimeEligibility: "LIMITED_SPELLING_RETRY",
    validationNotes: ["Tidak menambah kewenangan."],
  },
  {
    id: "GLS-006",
    canonicalTerm: "Penukaran",
    variants: ["debt switch"],
    category: "DOMAIN_MAPPING",
    definition: "Kandidat pemetaan istilah.",
    sourceReferences: ["PMK 114/2023"],
    validationStatus: "PENDING_MENTOR_VALIDATION",
    runtimeEligibility: "BLOCKED",
    validationNotes: ["Perlu pemeriksaan mentor."],
  },
];

describe("GlossaryRegister", () => {
  it("separates active spelling variants from blocked domain mappings", () => {
    render(<GlossaryRegister entries={ENTRIES} />);

    expect(screen.getByText("2", { selector: "strong" })).toBeInTheDocument();
    expect(screen.getByText("Aktif untuk variasi ejaan")).toBeInTheDocument();
    const blockedRow = screen.getByText("Penukaran").closest("tr");
    expect(blockedRow).not.toBeNull();
    expect(within(blockedRow!).getByText("Menunggu pemeriksaan mentor")).toBeInTheDocument();
  });
});
