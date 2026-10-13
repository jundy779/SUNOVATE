import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ValidationRegister, type IntakeCase } from "./validation-register";

const CASES: IntakeCase[] = [
  {
    id: "SME-01",
    question: "Bagaimana memeriksa data hasil lelang?",
    draftAnswer: "Lakukan rekonsiliasi berdasarkan sumber resmi.",
    suppliedReferences: ["PMK 111 Tahun 2024"],
    candidateReferences: ["SOP lelang yang disahkan"],
    validationNotes: ["Konfirmasi kepada SME lelang"],
    validationStatus: "PENDING_SME_VALIDATION",
    runtimeEligibility: "BLOCKED",
  },
  {
    id: "SME-02",
    question: "Bagaimana koreksi setelah data dikunci?",
    draftAnswer: "Ajukan koreksi melalui jalur resmi.",
    suppliedReferences: ["PMK 111 Tahun 2024"],
    candidateReferences: [],
    validationNotes: ["Rujukan pasal perlu diperbaiki"],
    validationStatus: "NEEDS_REVISION",
    runtimeEligibility: "BLOCKED",
  },
];

const AUCTION_QUESTION = "Bagaimana memeriksa data hasil lelang?";
const LOCKED_QUESTION = "Bagaimana koreksi setelah data dikunci?";

describe("ValidationRegister", () => {
  it("filters the read-only register by search and status", () => {
    render(<ValidationRegister cases={CASES} />);

    expect(screen.getByText("Menampilkan 2 dari 2 pertanyaan")).toBeInTheDocument();

    fireEvent.change(screen.getByRole("searchbox", { name: "Cari dalam register" }), {
      target: { value: "dikunci" },
    });
    expect(screen.getByText("Menampilkan 1 dari 2 pertanyaan")).toBeInTheDocument();
    expect(screen.queryByText(AUCTION_QUESTION)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Atur ulang" }));
    fireEvent.change(screen.getByRole("combobox", { name: "Status validasi" }), {
      target: { value: "PENDING_SME_VALIDATION" },
    });
    expect(screen.getByText(AUCTION_QUESTION)).toBeInTheDocument();
    expect(screen.queryByText(LOCKED_QUESTION)).not.toBeInTheDocument();
  });

  it("shows a recoverable empty state and supports printing", () => {
    const print = vi.spyOn(window, "print").mockImplementation(() => undefined);
    render(<ValidationRegister cases={CASES} />);

    fireEvent.change(screen.getByRole("searchbox", { name: "Cari dalam register" }), {
      target: { value: "tidak ditemukan" },
    });
    expect(screen.getByText("Tidak ada pertanyaan yang cocok")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Tampilkan semua" }));
    expect(screen.getByText("Menampilkan 2 dari 2 pertanyaan")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Cetak register" }));
    expect(print).toHaveBeenCalledOnce();
    print.mockRestore();
  });
});
