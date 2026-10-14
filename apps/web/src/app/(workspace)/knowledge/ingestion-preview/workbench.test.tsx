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

    render(<ChunkPreviewWorkbench teams={[]} canSave={false} />);
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
    render(<ChunkPreviewWorkbench teams={[]} canSave={false} />);
    fireEvent.click(screen.getByRole("button", { name: "Periksa pembagian" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Bahan tidak dapat diperiksa");
  });

  it("menyimpan hasil yang sudah diperiksa sebagai draf", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({
      data: { documentLabel: "SIMULASI - Bahan", knowledgeType: "REGULATION", chunkCount: 1,
        totalWords: 3, persisted: false, chunks: [{ index: 0, sectionLabel: "Pasal 1",
          content: "Isi ketentuan pertama.", wordCount: 3, contentHash: "abcdef1234567890" }] },
      meta: { dataLabel: "SIMULATED_DATA" },
    }), { status: 200, headers: { "Content-Type": "application/json" } }));
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({
      data: { id: "00000000-0000-4000-8000-000000000099", title: "SIMULASI - Bahan" },
      meta: { dataLabel: "SIMULATED_DATA" },
    }), { status: 201, headers: { "Content-Type": "application/json" } }));

    render(<ChunkPreviewWorkbench teams={[{ id: "team-1", code: "PSUN", name: "Peraturan SUN" }]} canSave />);
    fireEvent.click(screen.getByRole("button", { name: "Periksa pembagian" }));
    await screen.findByText("Pasal 1");
    fireEvent.click(screen.getByRole("button", { name: "Setujui pembagian dan simpan draf" }));

    expect(await screen.findByText("Draf berhasil disimpan.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Buka draf" })).toHaveAttribute(
      "href", "/knowledge/00000000-0000-4000-8000-000000000099",
    );
    expect(fetchMock).toHaveBeenLastCalledWith("/api/knowledge/chunk-drafts", expect.any(Object));
  });
});
