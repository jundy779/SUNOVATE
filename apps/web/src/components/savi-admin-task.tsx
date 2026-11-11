"use client";

import { useState } from "react";

interface Draft {
  draftId: string;
  kind: "WORK_REPORT";
  title: string;
  text: string;
  sources: { type: string; id: string; title: string }[];
}

type Phase = "idle" | "loading" | "review" | "saving" | "accepted" | "rejected" | "error";

/**
 * SAVI administrative task (DEC-20261111-02): SAVI drafts, the employee reviews.
 * Nothing is saved or sent automatically; accepting copies the reviewed text for the employee.
 */
export function SaviAdminTask() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [text, setText] = useState("");
  const [message, setMessage] = useState("");

  async function generate() {
    setPhase("loading");
    setMessage("");
    try {
      const response = await fetch("/api/savi/tasks/work-report", { method: "POST" });
      if (!response.ok) throw new Error();
      const body = (await response.json()) as { data: Draft };
      setDraft(body.data);
      setText(body.data.text);
      setPhase("review");
    } catch {
      setPhase("error");
      setMessage("Draf belum dapat disusun. Coba lagi beberapa saat lagi.");
    }
  }

  async function decide(decision: "ACCEPTED" | "REJECTED") {
    if (!draft) return;
    setPhase("saving");
    try {
      const response = await fetch("/api/savi/tasks/reviews", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ draftId: draft.draftId, kind: draft.kind, decision, edited: text !== draft.text }),
      });
      if (!response.ok) throw new Error();
      if (decision === "ACCEPTED") {
        try {
          await navigator.clipboard.writeText(text);
          setMessage("Draf disetujui dan disalin. Tempelkan ke dokumen atau pesan Anda.");
        } catch {
          setMessage("Draf disetujui. Salin teks di atas secara manual.");
        }
        setPhase("accepted");
      } else {
        setMessage("Draf ditolak dan tidak dipakai.");
        setDraft(null);
        setPhase("rejected");
      }
    } catch {
      setPhase("review");
      setMessage("Keputusan belum tercatat. Coba lagi.");
    }
  }

  return (
    <div className="savi-task">
      <div className="savi-task-intro">
        <div>
          <h3>Draf laporan pekerjaan</h3>
          <p>
            SAVI menyusun rekap dari Monitoring Kerja yang boleh Anda akses: tugas aktif, yang terlambat,
            yang jatuh tempo dekat, dan yang selesai minggu ini. Anda memeriksa dan mengubahnya sebelum dipakai.
          </p>
        </div>
        <button className="button" type="button" onClick={generate} disabled={phase === "loading" || phase === "saving"}>
          {phase === "loading" ? "Menyusun draf…" : draft ? "Susun ulang" : "Susun draf"}
        </button>
      </div>
      {draft && phase !== "rejected" ? (
        <div className="savi-task-review">
          <label htmlFor="savi-task-text">Periksa dan ubah draf sebelum disetujui</label>
          <textarea id="savi-task-text" value={text} onChange={(event) => setText(event.target.value)} rows={14} />
          <p className="savi-task-sources">
            Disusun dari {draft.sources.length} butir Monitoring Kerja. Draf belum disimpan atau dikirim ke mana pun.
          </p>
          <div className="savi-task-actions">
            <button className="button" type="button" onClick={() => decide("ACCEPTED")} disabled={phase !== "review"}>
              Setujui dan salin
            </button>
            <button className="button button-secondary" type="button" onClick={() => decide("REJECTED")} disabled={phase !== "review"}>
              Tolak draf
            </button>
          </div>
        </div>
      ) : null}
      {message ? <p className={phase === "error" ? "notice notice-error" : "notice"} role="status">{message}</p> : null}
    </div>
  );
}
