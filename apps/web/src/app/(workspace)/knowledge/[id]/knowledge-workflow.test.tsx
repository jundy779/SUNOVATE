import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ApprovalRequest, KnowledgeEntry, Principal } from "@sunovate/contracts";
import { KnowledgeWorkflow } from "./knowledge-workflow";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }));

const ENTRY = {
  id: "00000000-0000-4000-8000-000000000101",
  title: "SIMULASI - Panduan pemeriksaan",
  knowledgeType: "PLAYBOOK",
  summary: "Ringkasan bahan simulasi untuk menguji alur pemeriksaan.",
  lifecycleStatus: "DRAFT",
  sharingScope: "TEAM",
  classificationCode: "INTERNAL",
  ownerTeamCode: "PPSUN",
  ownerUserId: "00000000-0000-4000-8000-000000000001",
  versionLabel: "v0.1",
  revision: 1,
  updatedAt: "2026-10-15T00:00:00Z",
  dataOrigin: "SIMULATED_DATA",
} satisfies KnowledgeEntry;

const OWNER = {
  id: ENTRY.ownerUserId,
  email: "owner@example.test",
  displayName: "Pemilik",
  roles: ["knowledge_owner"],
  permissions: ["knowledge:update", "knowledge:submit", "approval:request"],
  teams: [], allTeams: false, clearanceCode: "INTERNAL",
} satisfies Principal;

const APPROVAL = {
  id: "00000000-0000-4000-8000-000000000201",
  requestType: "KNOWLEDGE_PUBLICATION",
  targetEntityType: "knowledge_entry",
  targetEntityId: ENTRY.id,
  status: "PENDING",
  requestedBy: OWNER.id,
  decidedBy: null, decidedAt: null, decisionReason: null,
  ownerTeamCode: "PPSUN", classificationCode: "INTERNAL",
  revision: 1, createdAt: "2026-10-15T00:00:00Z",
} satisfies ApprovalRequest;

afterEach(() => { vi.restoreAllMocks(); refresh.mockReset(); });

describe("KnowledgeWorkflow", () => {
  it("memberi pemilik tindakan ubah dan ajukan tanpa keputusan", () => {
    render(<KnowledgeWorkflow entry={ENTRY} principal={OWNER} approval={null} />);
    expect(screen.getByRole("button", { name: "Ubah draf" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ajukan pemeriksaan" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /terbitkan/i })).not.toBeInTheDocument();
  });

  it("menunjukkan status menunggu kepada pengaju tanpa tombol keputusan", () => {
    render(<KnowledgeWorkflow entry={{ ...ENTRY, lifecycleStatus: "IN_REVIEW" }} principal={OWNER} approval={APPROVAL} />);
    expect(screen.getByText(/menunggu keputusan pemeriksa/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /terbitkan|kembalikan/i })).not.toBeInTheDocument();
  });

  it("membatasi penerbitan kepada pemeriksa yang memiliki kewenangan terbit", () => {
    const reviewer = { ...OWNER, id: "00000000-0000-4000-8000-000000000002", roles: ["reviewer"], permissions: ["approval:decide"] };
    const submitted = { ...ENTRY, lifecycleStatus: "IN_REVIEW" } as KnowledgeEntry;
    const view = render(<KnowledgeWorkflow entry={submitted} principal={reviewer} approval={APPROVAL} />);
    expect(screen.getByRole("button", { name: "Kembalikan untuk diperbaiki" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Setujui dan terbitkan" })).not.toBeInTheDocument();

    view.rerender(<KnowledgeWorkflow entry={submitted} principal={{ ...reviewer, permissions: ["approval:decide", "knowledge:publish"] }} approval={APPROVAL} />);
    expect(screen.getByRole("button", { name: "Setujui dan terbitkan" })).toBeInTheDocument();
  });

  it("mengirim keputusan penerbitan dengan alasan dan revisi persetujuan", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ data: {}, meta: {} }), { status: 200 }));
    const reviewer = { ...OWNER, id: "00000000-0000-4000-8000-000000000002", roles: ["knowledge_coordinator"], permissions: ["approval:decide", "knowledge:publish"] };
    render(<KnowledgeWorkflow entry={{ ...ENTRY, lifecycleStatus: "IN_REVIEW" }} principal={reviewer} approval={APPROVAL} />);
    fireEvent.change(screen.getByLabelText("Alasan keputusan"), { target: { value: "Isi telah diperiksa dan sesuai." } });
    fireEvent.click(screen.getByRole("button", { name: "Setujui dan terbitkan" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());
    const request = JSON.parse(String((fetchMock.mock.calls[0]?.[1] as RequestInit).body));
    expect(request).toEqual({ path: `/approvals/${APPROVAL.id}/decision`, method: "POST", body: { decision: "APPROVE", revision: 1, reason: "Isi telah diperiksa dan sesuai." } });
  });
});
