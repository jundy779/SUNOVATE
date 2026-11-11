import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SaviAdminTask } from "./savi-admin-task";

const DRAFT = {
  draftId: "11111111-1111-4111-8111-111111111111",
  kind: "WORK_REPORT",
  title: "Draf laporan pekerjaan",
  text: "Draf laporan pekerjaan per 11-11-2026\nCakupan: PPPSUN",
  sources: [{ type: "TASK", id: "t1", title: "SIMULASI - Tugas" }],
};

function mockFetch() {
  const calls: { url: string; body?: unknown }[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({ url, body: init?.body ? JSON.parse(String(init.body)) : undefined });
      const data = url.endsWith("work-report") ? DRAFT : { decision: "REJECTED" };
      return new Response(JSON.stringify({ data }), { status: 201 });
    }),
  );
  return calls;
}

afterEach(() => vi.unstubAllGlobals());

describe("SaviAdminTask", () => {
  it("shows the draft for review and never saves it before the employee decides", async () => {
    const calls = mockFetch();
    render(<SaviAdminTask />);
    fireEvent.click(screen.getByRole("button", { name: "Susun draf" }));
    const editor = await screen.findByLabelText("Periksa dan ubah draf sebelum disetujui");
    expect((editor as HTMLTextAreaElement).value).toContain("Cakupan: PPPSUN");
    expect(screen.getByText(/belum disimpan atau dikirim/)).toBeInTheDocument();
    expect(calls.map((call) => call.url)).toEqual(["/api/savi/tasks/work-report"]);
  });

  it("records an edited rejection without sending the text", async () => {
    const calls = mockFetch();
    render(<SaviAdminTask />);
    fireEvent.click(screen.getByRole("button", { name: "Susun draf" }));
    const editor = await screen.findByLabelText("Periksa dan ubah draf sebelum disetujui");
    fireEvent.change(editor, { target: { value: "Teks yang diubah pegawai" } });
    fireEvent.click(screen.getByRole("button", { name: "Tolak draf" }));
    await waitFor(() => expect(screen.getByText("Draf ditolak dan tidak dipakai.")).toBeInTheDocument());
    const review = calls.find((call) => call.url === "/api/savi/tasks/reviews")?.body as Record<string, unknown>;
    expect(review).toEqual({ draftId: DRAFT.draftId, kind: "WORK_REPORT", decision: "REJECTED", edited: true });
    expect(JSON.stringify(review)).not.toContain("Teks yang diubah");
  });
});
