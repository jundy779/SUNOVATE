import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { HermesChat } from "./hermes-chat";

const answer = {
  data: {
    conversationId: "00000000-0000-4000-8000-000000000001",
    messageId: "00000000-0000-4000-8000-000000000002",
    decision: "ANSWERED",
    reason: "ok",
    answer: "Berdasarkan sumber yang dapat Anda akses:\n\n1. Metadata wajib dicatat. [1]",
    citations: [
      {
        index: 1,
        knowledgeEntryId: "00000000-0000-4000-8000-000000000003",
        documentChunkId: "00000000-0000-4000-8000-000000000004",
        title: "SIMULASI - SOP Registrasi Metadata Dokumen Knowledge",
        sectionLabel: "Langkah 1",
        versionLabel: "v1.0",
        knowledgeType: "SOP",
        classificationCode: "INTERNAL",
      },
    ],
    excludedPassages: 0,
    approvalRequestId: null,
    followUp: null,
  },
  meta: { dataLabel: "SIMULATED_DATA" },
};

function renderChat() {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: 0 } } });
  return render(
    <QueryClientProvider client={client}>
      <HermesChat />
    </QueryClientProvider>,
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("HermesChat", () => {
  it("shows the answer with its citation and decision label", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(answer), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    renderChat();
    fireEvent.change(screen.getByLabelText("Pertanyaan untuk SAVI AI"), {
      target: { value: "Apa metadata wajib dokumen knowledge?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Kirim pertanyaan" }));

    expect(await screen.findByText("Dijawab dengan sumber")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: answer.data.citations[0]!.title })).toHaveAttribute(
      "href",
      `/knowledge/${answer.data.citations[0]!.knowledgeEntryId}`,
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/hermes", expect.objectContaining({ method: "POST" }));
  });

  it("validates the question before calling the API", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    renderChat();
    fireEvent.click(screen.getByRole("button", { name: "Kirim pertanyaan" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Pertanyaan minimal 3 karakter");
    await waitFor(() => expect(fetchMock).not.toHaveBeenCalled());
  });

  it("shows API errors without technical details", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ code: "PERMISSION_DENIED", message: "Anda tidak memiliki izin" }), {
          status: 403,
        }),
      ),
    );
    renderChat();
    fireEvent.change(screen.getByLabelText("Pertanyaan untuk SAVI AI"), {
      target: { value: "Apa SOP knowledge?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Kirim pertanyaan" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Anda tidak memiliki izin");
  });

  it("shows safe next steps when available sources are insufficient", async () => {
    const insufficient = {
      ...answer,
      data: {
        ...answer.data,
        decision: "INSUFFICIENT_EVIDENCE",
        answer: "Bukti pada sumber yang dapat Anda akses belum cukup.",
        citations: [],
        followUp: {
          status: "NEEDS_CLARIFICATION",
          title: "Sumber belum mencukupi",
          guidance: "Perjelas periode, nama dokumen, proses, atau unit yang dimaksud.",
          clarificationPrompt: "Sebutkan periode dan dokumen acuan yang ingin diperiksa.",
        },
      },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(JSON.stringify(insufficient), { status: 200 })),
    );
    renderChat();
    fireEvent.change(screen.getByLabelText("Pertanyaan untuk SAVI AI"), {
      target: { value: "Bagaimana proses yang belum ada sumbernya?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Kirim pertanyaan" }));

    expect(await screen.findByRole("region", { name: "Langkah berikutnya" })).toHaveTextContent(
      "Sumber belum mencukupi",
    );
    expect(screen.getByText(/tidak mengirim permintaan kepada pegawai/i)).toBeInTheDocument();
  });
});
