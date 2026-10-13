"use client";

import { useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import type { Principal, TeamSummary, WorkItem } from "@sunovate/contracts";
import { TASK_STATUS_LABELS, type TaskStatus } from "@sunovate/shared-types";
import { DeadlineTag, EmptyState, Panel, StatusTag } from "@/components/page-elements";
import { formatDate } from "@/lib/format";
import { classificationLabel } from "@/lib/ui-labels";

type Entity = "outputs" | "tasks" | "milestones" | "pending" | "followUps";
type InitialData = Record<Entity, WorkItem[]>;

const CONFIG: Record<Entity, { label: string; singular: string; path: string; permission: string }> = {
  outputs: { label: "Output kerja", singular: "output", path: "/work-outputs", permission: "work:create" },
  tasks: { label: "Tugas", singular: "tugas", path: "/tasks", permission: "work:create" },
  milestones: { label: "Tahapan penting", singular: "tahapan penting", path: "/milestones", permission: "work:create" },
  pending: { label: "Perlu tindak lanjut", singular: "hal yang perlu ditindaklanjuti", path: "/pending-matters", permission: "pending:manage" },
  followUps: { label: "Tindak lanjut", singular: "tindak lanjut", path: "/follow-ups", permission: "pending:manage" },
};

const TASK_STATUSES = Object.keys(TASK_STATUS_LABELS) as TaskStatus[];
const PENDING_STATUSES = ["OPEN", "IN_PROGRESS", "RESOLVED", "CANCELLED"];
const FOLLOW_UP_STATUSES = ["OPEN", "DONE", "CANCELLED"];
const MILESTONE_STATUSES = ["PLANNED", "ACHIEVED", "MISSED", "CANCELLED"];

function labelStatus(status: string) {
  const labels: Record<string, string> = {
    ...TASK_STATUS_LABELS,
    OPEN: "Terbuka", RESOLVED: "Selesai", DONE: "Selesai",
    PLANNED: "Direncanakan", ACHIEVED: "Tercapai", MISSED: "Tidak tercapai",
  };
  return labels[status] ?? status.replaceAll("_", " ");
}

function statuses(entity: Entity) {
  if (entity === "pending") return PENDING_STATUSES;
  if (entity === "followUps") return FOLLOW_UP_STATUSES;
  if (entity === "milestones") return MILESTONE_STATUSES;
  return TASK_STATUSES;
}

function priorityLabel(priority: string) {
  return ({ LOW: "Rendah", HIGH: "Tinggi", URGENT: "Mendesak" } as Record<string, string>)[priority] ?? "Normal";
}

async function mutate(path: string, method: "POST" | "PATCH" | "DELETE", body?: unknown) {
  const response = await fetch("/api/work", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, method, body }),
  });
  const result = (await response.json().catch(() => ({}))) as { message?: string };
  if (!response.ok) throw new Error(result.message ?? "Data tidak dapat disimpan");
}

export function WorkManagement({ initial, principal, teams }: {
  initial: InitialData;
  principal: Principal;
  teams: TeamSummary[];
}) {
  const router = useRouter();
  const [active, setActive] = useState<Entity>("outputs");
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<WorkItem | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const config = CONFIG[active];
  const canCreate = principal.permissions.includes(config.permission);
  const canUpdate = principal.permissions.includes(active === "pending" || active === "followUps" ? "pending:manage" : "work:update");
  const scopedTeams = useMemo(
    () => principal.allTeams ? teams : teams.filter((team) => principal.teams.some((owned) => owned.id === team.id)),
    [principal, teams],
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setMessage(null);
    const form = new FormData(event.currentTarget);
    const body: Record<string, unknown> = {
      title: String(form.get("title") ?? "").trim(),
      ownerTeamId: String(form.get("ownerTeamId") ?? ""),
      classificationCode: String(form.get("classificationCode") ?? "INTERNAL"),
    };
    const dateValue = String(form.get("date") ?? "");
    if (dateValue) body[active === "outputs" ? "targetDate" : "dueDate"] = dateValue;
    if (active === "outputs" || active === "pending") body.description = String(form.get("description") ?? "").trim();
    if (active === "tasks" || active === "milestones") body.workOutputId = String(form.get("workOutputId") ?? "") || null;
    if (active === "followUps") body.pendingMatterId = String(form.get("pendingMatterId") ?? "") || null;
    try {
      await mutate(config.path, "POST", body);
      setCreating(false); setMessage(`${config.label} berhasil ditambahkan.`); router.refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Data tidak dapat disimpan"); }
    finally { setBusy(false); }
  }

  async function updateStatus(item: WorkItem, status: string) {
    setBusy(true); setMessage(null);
    try {
      await mutate(`${config.path}/${item.id}`, "PATCH", { revision: item.revision, status });
      setEditing(null); setMessage("Status berhasil diperbarui."); router.refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Status tidak dapat diperbarui"); }
    finally { setBusy(false); }
  }

  async function remove(item: WorkItem) {
    if (!window.confirm(`Arsipkan ${config.singular} “${item.title}”?`)) return;
    setBusy(true); setMessage(null);
    try {
      await mutate(`${config.path}/${item.id}?revision=${item.revision}`, "DELETE");
      setMessage(`${config.label} berhasil diarsipkan.`); router.refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Data tidak dapat diarsipkan"); }
    finally { setBusy(false); }
  }

  const items = initial[active];
  return (
    <div className="work-manager">
      <nav className="work-tabs" aria-label="Jenis data monitoring">
        {(Object.keys(CONFIG) as Entity[]).map((key) => (
          <button key={key} type="button" className={active === key ? "is-active" : ""}
            onClick={() => { setActive(key); setCreating(false); setEditing(null); setMessage(null); }}>
            {CONFIG[key].label}<span>{initial[key].length}</span>
          </button>
        ))}
      </nav>

      <Panel title={config.label} action={canCreate ? <button className="button work-add" type="button" onClick={() => setCreating((value) => !value)}>Tambah {config.singular}</button> : undefined}>
        {message ? <p className="work-feedback" role="status">{message}</p> : null}
        {creating ? (
          <form className="work-form" onSubmit={submit}>
            <label>Judul<input name="title" minLength={3} maxLength={255} required /></label>
            {(active === "outputs" || active === "pending") ? <label className="work-form-wide">Deskripsi<textarea name="description" minLength={5} maxLength={4000} required /></label> : null}
            <label>Tim<select name="ownerTeamId" required defaultValue=""><option value="" disabled>Pilih tim</option>{scopedTeams.map((team) => <option key={team.id} value={team.id}>{team.code} · {team.name}</option>)}</select></label>
            <label>Klasifikasi<select name="classificationCode" defaultValue="INTERNAL">{["PUBLIC", "INTERNAL", "RESTRICTED"].map((code) => <option key={code} value={code}>{classificationLabel(code)}</option>)}</select></label>
            {(active === "tasks" || active === "milestones") ? <label>Output terkait<select name="workOutputId" required={active === "milestones"} defaultValue=""><option value="">Tanpa output</option>{initial.outputs.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label> : null}
            {active === "followUps" ? <label>Hal terkait<select name="pendingMatterId" defaultValue=""><option value="">Tanpa induk</option>{initial.pending.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label> : null}
            <label>{active === "outputs" ? "Tanggal target" : "Tenggat"}<input type="date" name="date" /></label>
            <div className="work-form-actions"><button type="button" className="button secondary" onClick={() => setCreating(false)}>Batal</button><button className="button" disabled={busy}>{busy ? "Menyimpan…" : "Simpan"}</button></div>
          </form>
        ) : null}

        {!items.length ? <EmptyState title={`Belum ada ${config.label.toLowerCase()}`} /> : (
          <div className="table-wrap work-table"><table><thead><tr><th>Judul</th><th>Tim</th><th>Status</th><th>Progres</th><th>Tanggal</th><th>Tenggat</th>{canUpdate ? <th>Aksi</th> : null}</tr></thead>
            <tbody>{items.map((item) => <tr key={item.id}><td><strong>{item.title}</strong>{item.priority && item.priority !== "NORMAL" ? <small>Prioritas {priorityLabel(item.priority)}</small> : null}</td><td>{item.ownerTeamCode ?? "-"}</td><td>{editing?.id === item.id ? <select aria-label={`Status ${item.title}`} defaultValue={item.status} disabled={busy} onChange={(event) => void updateStatus(item, event.target.value)}>{statuses(active).map((status) => <option key={status} value={status}>{labelStatus(status)}</option>)}</select> : <StatusTag>{labelStatus(item.status)}</StatusTag>}</td><td>{item.progress === undefined ? "-" : `${item.progress}%`}</td><td>{formatDate(active === "outputs" ? item.targetDate : item.dueDate)}</td><td><DeadlineTag state={item.deadlineState} /></td>{canUpdate ? <td><div className="row-actions"><button type="button" onClick={() => setEditing(editing?.id === item.id ? null : item)}>Ubah</button><button type="button" className="danger-link" disabled={busy} onClick={() => void remove(item)}>Arsipkan</button></div></td> : null}</tr>)}</tbody>
          </table></div>
        )}
      </Panel>
      <p className="work-policy-note">Setiap perubahan diperiksa terhadap versi terakhir dan dicatat dalam riwayat aktivitas. Alur persetujuan belum diaktifkan karena kewenangannya masih menunggu konfirmasi.</p>
    </div>
  );
}
