"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import type { ApprovalRequest, KnowledgeEntry, Principal } from "@sunovate/contracts";
import { classificationLabel } from "@/lib/ui-labels";

async function mutate(path: string, method: "POST" | "PATCH", body: unknown) {
  const response = await fetch("/api/knowledge-workflow", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, method, body }),
  });
  const result = (await response.json().catch(() => ({}))) as { message?: string };
  if (!response.ok) throw new Error(result.message ?? "Perubahan tidak dapat disimpan");
}

export function KnowledgeWorkflow({ entry, principal, approval }: {
  entry: KnowledgeEntry;
  principal: Principal;
  approval: ApprovalRequest | null;
}) {
  const router = useRouter();
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const isOwner = entry.ownerUserId === principal.id;
  const canEdit = entry.lifecycleStatus === "DRAFT" && isOwner && principal.permissions.includes("knowledge:update");
  const canSubmit = entry.lifecycleStatus === "DRAFT" && isOwner && principal.permissions.includes("knowledge:submit") && principal.permissions.includes("approval:request");
  const canDecide = entry.lifecycleStatus === "IN_REVIEW" && approval?.status === "PENDING" && approval.requestedBy !== principal.id && principal.permissions.includes("approval:decide");
  const canPublish = canDecide && principal.permissions.includes("knowledge:publish");
  const classificationOrder = ["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"];
  const clearanceIndex = classificationOrder.indexOf(principal.clearanceCode);
  const allowedClassifications = classificationOrder.slice(0, Math.max(clearanceIndex, 0) + 1);

  async function update(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage(null);
    const form = new FormData(event.currentTarget);
    try {
      await mutate(`/knowledge/${entry.id}`, "PATCH", {
        revision: entry.revision,
        title: String(form.get("title") ?? "").trim(),
        summary: String(form.get("summary") ?? "").trim(),
        classificationCode: String(form.get("classificationCode") ?? "INTERNAL"),
        sharingScope: String(form.get("sharingScope") ?? "TEAM"),
      });
      setEditing(false); setMessage("Draf berhasil diperbarui."); router.refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Draf tidak dapat diperbarui"); }
    finally { setBusy(false); }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage(null);
    const form = new FormData(event.currentTarget);
    try {
      await mutate(`/knowledge/${entry.id}/submit`, "POST", {
        revision: entry.revision,
        note: String(form.get("note") ?? "").trim() || null,
      });
      setMessage("Draf telah diajukan untuk diperiksa."); router.refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Draf tidak dapat diajukan"); }
    finally { setBusy(false); }
  }

  async function decide(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!approval) return;
    setBusy(true); setMessage(null);
    const form = new FormData(event.currentTarget);
    const submitter = (event.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null;
    const decision = submitter?.value as "APPROVE" | "REJECT";
    const reason = String(form.get("reason") ?? "").trim();
    try {
      await mutate(`/approvals/${approval.id}/decision`, "POST", {
        decision, revision: approval.revision, reason,
      });
      setMessage(decision === "APPROVE" ? "Pengetahuan telah disetujui dan diterbitkan." : "Draf dikembalikan untuk diperbaiki.");
      router.refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Keputusan tidak dapat disimpan"); }
    finally { setBusy(false); }
  }

  if (!canEdit && !canSubmit && !canDecide && !approval) return null;

  return (
    <section className="knowledge-workflow" aria-labelledby="knowledge-workflow-title">
      <header>
        <div><h2 id="knowledge-workflow-title">Tindak lanjut pengetahuan</h2><p>Perubahan dan keputusan dicatat dalam riwayat aktivitas.</p></div>
        {canEdit ? <button className="button secondary" type="button" onClick={() => setEditing((value) => !value)}>{editing ? "Tutup perubahan" : "Ubah draf"}</button> : null}
      </header>
      {message ? <p className="workflow-feedback" role="status">{message}</p> : null}

      {editing ? (
        <form className="knowledge-edit-form" onSubmit={update}>
          <label>Judul<input name="title" defaultValue={entry.title} minLength={5} maxLength={255} required /></label>
          <label className="workflow-wide">Ringkasan<textarea name="summary" defaultValue={entry.summary} minLength={10} maxLength={2000} required /></label>
          <label>Klasifikasi<select name="classificationCode" defaultValue={entry.classificationCode}>{allowedClassifications.map((code) => <option key={code} value={code}>{classificationLabel(code)}</option>)}</select></label>
          <label>Jangkauan setelah terbit<select name="sharingScope" defaultValue={entry.sharingScope}><option value="TEAM">Tim pemilik</option><option value="DIRECTORATE">Direktorat</option></select></label>
          <div className="workflow-actions"><button className="button" disabled={busy}>{busy ? "Menyimpan…" : "Simpan perubahan"}</button></div>
        </form>
      ) : null}

      {canSubmit && !editing ? (
        <form className="workflow-decision" onSubmit={submit}>
          <label>Catatan untuk pemeriksa<textarea name="note" maxLength={1000} placeholder="Jelaskan perubahan atau hal yang perlu diperhatikan" /></label>
          <div><p>Setelah diajukan, draf tidak dapat diubah sampai pemeriksa memberikan keputusan.</p><button className="button" disabled={busy}>{busy ? "Mengajukan…" : "Ajukan pemeriksaan"}</button></div>
        </form>
      ) : null}

      {approval?.status === "PENDING" && !canDecide ? <p className="workflow-waiting">Draf sedang menunggu keputusan pemeriksa yang berwenang.</p> : null}
      {canDecide ? (
        <form className="workflow-decision" onSubmit={(event) => void decide(event)}>
          <label>Alasan keputusan<textarea name="reason" minLength={3} maxLength={1000} required placeholder="Tuliskan dasar keputusan secara jelas" /></label>
          <div><p>Pengaju tidak dapat memutuskan permintaannya sendiri.</p><div className="workflow-actions"><button className="button secondary" disabled={busy} type="submit" name="decision" value="REJECT">Kembalikan untuk diperbaiki</button>{canPublish ? <button className="button" disabled={busy} type="submit" name="decision" value="APPROVE">Setujui dan terbitkan</button> : null}</div></div>
        </form>
      ) : null}
      {approval && approval.status !== "PENDING" ? <p className="workflow-history">Keputusan terakhir: {approval.status === "APPROVED" ? "Disetujui" : "Dikembalikan"}{approval.decisionReason ? ` · ${approval.decisionReason}` : ""}</p> : null}
    </section>
  );
}
