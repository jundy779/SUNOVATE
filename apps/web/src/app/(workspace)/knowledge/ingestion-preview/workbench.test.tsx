import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ChunkPreviewWorkbench } from "./workbench";

afterEach(() => vi.restoreAllMocks());

describe("ChunkPreviewWorkbench", () => {
  it("menampilkan hasil pemeriksaan tanpa tindakan simpan", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      data: {
        documentLabel: "SIMULASI - Bahan",
        knowledgeType: "REGULATION",
        chunkCount: 2,
        totalWords: 12,
        persisted: false,
        chunks: [
          { index: 0, sectionLabel: "Pasal 1", content: "Isi ketentuan pertama.", wordCount: 3, contentHash: "abcdef1234567890" },
          { index: 1, sectionLabel: "Pasal 2", content: "Isi ketentuan kedua.", wordCount: 3, contentHash: "123456abcdef7890" },
        ],
      },
      meta: { dataLabel: "SIMULATED_DATA" },
    }), { status: 200, headers: { "Content-Type": "application/json" } }));

    render(<ChunkPreviewWorkbench />);
    fireEvent.click(screen.getByRole("button", { name: "Periksa pembagian" }));

    await waitFor(() => expect(screen.getByText("Pasal 1")).toBeInTheDocument());
    expect(screen.getByText("Pasal 2")).toBeInTheDocument();
    expect(screen.getByText("Tidak")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /simpan|terbit/i })).not.toBeInTheDocument();
  });

  it("menampilkan pesan kegagalan dari layanan", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(
      JSON.stringify({ message: "Bahan tidak dapat diperiksa" }),
      { status: 422, headers: { "Content-Type": "application/json" } },
    ));
    render(<ChunkPreviewWorkbench />);
    fireEvent.click(screen.getByRole("button", { name: "Periksa pembagian" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Bahan tidak dapat diperiksa");
  });
});
