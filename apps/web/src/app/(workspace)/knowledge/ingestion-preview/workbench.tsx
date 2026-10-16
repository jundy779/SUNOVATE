"use client";

import Link from "next/link";
import { useState } from "react";
import type { FormEvent } from "react";

interface ChunkItem { index: number; sectionLabel: string; content: string; wordCount: number; contentHash: string; }
interface ExtractionInfo { format: string; sizeBytes: number; checksum: string; pageCount: number | null; paragraphCount: number | null; sheetCount: number | null; status: "EXTRACTED"; nextStep: "HUMAN_REVIEW"; statusHistory: ["PENDING", "EXTRACTED"]; persisted: false; }
interface PreviewData { documentLabel: string; knowledgeType: string; chunkCount: number; totalWords: number; persisted: false; extractedText?: string; extraction?: ExtractionInfo; chunks: ChunkItem[]; }
interface TeamOption { id: string; code: string; name: string; }

const TYPE_OPTIONS = [
  ["REGULATION", "Peraturan"], ["SOP", "Prosedur kerja"], ["PLAYBOOK", "Panduan kerja"],
  ["STUDY", "Kajian"], ["REPORT", "Laporan"], ["MEETING_MATERIAL", "Bahan rapat"],
  ["LESSON_LEARNED", "Catatan pembelajaran"], ["OTHER", "Pengetahuan lainnya"],
] as const;

const SAMPLE_TEXT = `Pasal 1
Ketentuan pertama untuk simulasi pemeriksaan isi dokumen SUN.

Pasal 2
Ketentuan kedua menjelaskan tahapan verifikasi dan persetujuan oleh pejabat yang berwenang.`;

export function ChunkPreviewWorkbench({ teams, canSave }: { teams: TeamOption[]; canSave: boolean }) {
  const [title, setTitle] = useState("SIMULASI - Bahan pemeriksaan dokumen SUN");
  const [type, setType] = useState("REGULATION");
  const [text, setText] = useState(SAMPLE_TEXT);
  const [summary, setSummary] = useState("Draf simulasi untuk memeriksa struktur isi dokumen sebelum penerbitan.");
  const [teamId, setTeamId] = useState(teams[0]?.id ?? "");
  const [classification, setClassification] = useState("INTERNAL");
  const [sharingScope, setSharingScope] = useState("TEAM");
  const [result, setResult] = useState<PreviewData | null>(null);
  const [previewSignature, setPreviewSignature] = useState("");
  const [savedDraftId, setSavedDraftId] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const signature = JSON.stringify([title, type, text]);

  async function extractFile(file: File | undefined) {
    if (!file) return;
    setBusy(true); setMessage(""); setResult(null); setSavedDraftId("");
    try {
      const form = new FormData();
      form.set("documentLabel", title); form.set("knowledgeType", type);
      form.set("maxWords", "400"); form.set("sourceFile", file);
      const response = await fetch("/api/knowledge/extract-preview", { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(`${payload.message ?? "Berkas belum dapat dibaca"}. Berkas tidak disimpan.`);
      const data = payload.data as PreviewData;
      const extractedText = data.extractedText ?? "";
      setText(extractedText); setResult(data);
      setPreviewSignature(JSON.stringify([title, type, extractedText]));
    } catch (error) { setMessage(error instanceof Error ? error.message : "Berkas belum dapat dibaca"); }
    finally { setBusy(false); }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage(""); setResult(null); setSavedDraftId("");
    try {
      const response = await fetch("/api/knowledge/chunk-preview", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentLabel: title, knowledgeType: type, extractedText: text, maxWords: 400 }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message ?? "Pemeriksaan belum dapat dilakukan");
      setResult(payload.data as PreviewData); setPreviewSignature(signature);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Pemeriksaan belum dapat dilakukan"); }
    finally { setBusy(false); }
  }

  async function saveDraft() {
    if (!result || previewSignature !== signature) { setMessage("Periksa kembali pembagian setelah mengubah isi bahan."); return; }
    setBusy(true); setMessage("");
    try {
      const response = await fetch("/api/knowledge/chunk-drafts", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentLabel: title, knowledgeType: type, extractedText: text, maxWords: 400,
          summary, ownerTeamId: teamId, classificationCode: classification, sharingScope }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message ?? "Draf belum dapat disimpan");
      setSavedDraftId(payload.data.id as string);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Draf belum dapat disimpan"); }
    finally { setBusy(false); }
  }

  return (
    <div className="ingestion-layout">
      <form className="ingestion-form" onSubmit={submit}>
        <div className="ingestion-heading"><div><p className="eyebrow">Bahan contoh</p><h2>Isi yang akan diperiksa</h2></div><span className="data-label">Data simulasi</span></div>
        <div className="ingestion-fields">
          <label>Nama bahan<input value={title} minLength={3} maxLength={255} onChange={(event) => { setTitle(event.target.value); setSavedDraftId(""); }} required /></label>
          <label>Jenis pengetahuan<select value={type} onChange={(event) => { setType(event.target.value); setSavedDraftId(""); }}>{TYPE_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="ingestion-text">Berkas simulasi<input aria-label="Berkas simulasi" type="file" accept=".txt,.md,.pdf,.docx,.xlsx,.xls" disabled={busy} onChange={(event) => void extractFile(event.target.files?.[0])} /><small>Nama berkas harus diawali SIMULASI. Maksimal 2 MB, tanpa kata sandi, makro, atau tautan data luar.</small></label>
          <label className="ingestion-text">Ringkasan draf<textarea className="ingestion-summary-input" value={summary} minLength={10} maxLength={2000} rows={3} onChange={(event) => setSummary(event.target.value)} required /></label>
          {canSave ? <>
            <label>Tim pemilik<select value={teamId} onChange={(event) => setTeamId(event.target.value)} required>{teams.map((team) => <option key={team.id} value={team.id}>{team.code} · {team.name}</option>)}</select></label>
            <label>Tingkat informasi<select value={classification} onChange={(event) => setClassification(event.target.value)}><option value="PUBLIC">Terbuka</option><option value="INTERNAL">Internal</option><option value="RESTRICTED">Terbatas</option></select></label>
            <label>Cakupan setelah diterbitkan<select value={sharingScope} onChange={(event) => setSharingScope(event.target.value)}><option value="TEAM">Tim pemilik</option><option value="DIRECTORATE">Direktorat</option></select></label>
          </> : null}
          <label className="ingestion-text">Teks hasil pembacaan dokumen<textarea aria-label="Teks hasil pembacaan dokumen" value={text} minLength={20} maxLength={100000} rows={14} onChange={(event) => { setText(event.target.value); setSavedDraftId(""); }} required /><small>Hasil pembacaan dapat diperiksa dan diperbaiki sebelum disimpan. Berkas sumber tidak disimpan.</small></label>
        </div>
        {message ? <p className="ingestion-error" role="alert">{message}</p> : null}
        <div className="ingestion-actions"><button className="button secondary" type="button" onClick={() => { setResult(null); setSavedDraftId(""); setMessage(""); }}>Bersihkan hasil</button><button className="button" type="submit" disabled={busy}>{busy ? "Memeriksa…" : "Periksa pembagian"}</button></div>
      </form>

      <section className="ingestion-results" aria-live="polite">
        <div className="ingestion-heading"><div><p className="eyebrow">Hasil pemeriksaan</p><h2>Bagian isi dokumen</h2></div>{result ? <span className="status status-neutral">{result.chunkCount} bagian</span> : null}</div>
        {!result ? <div className="ingestion-empty"><strong>Belum ada hasil</strong><p>Isi bahan di sebelah kiri, lalu pilih “Periksa pembagian”.</p></div> : <>
          <div className="ingestion-summary"><div><strong>{result.chunkCount}</strong><span>Bagian</span></div><div><strong>{result.totalWords}</strong><span>Jumlah kata</span></div><div><strong>{savedDraftId ? "Ya" : "Tidak"}</strong><span>Disimpan</span></div></div>
          {result.extraction ? <><ol className="extraction-steps" aria-label="Tahapan pemeriksaan berkas"><li className="complete">Pemeriksaan awal selesai</li><li className="complete">Isi berhasil dibaca</li><li className="current">Menunggu pemeriksaan manusia</li></ol><p className="extraction-note" role="status">Berkas {result.extraction.format} berhasil dibaca di ruang sementara. Sumber tidak disimpan. Kode pemeriksaan {result.extraction.checksum.slice(0, 12)}.</p></> : null}
          <div className="chunk-list">{result.chunks.map((chunk) => <article key={chunk.contentHash}><header><span>{String(chunk.index + 1).padStart(2, "0")}</span><h3>{chunk.sectionLabel}</h3><small>{chunk.wordCount} kata</small></header><p>{chunk.content}</p><footer>Kode pemeriksaan: {chunk.contentHash.slice(0, 12)}</footer></article>)}</div>
          <div className="ingestion-save">{savedDraftId ? <p role="status">Draf berhasil disimpan. <Link href={`/knowledge/${savedDraftId}`}>Buka draf</Link></p> : canSave ? <><p>Hasil akan disimpan sebagai draf dan belum dapat digunakan SAVI.</p><button className="button" type="button" disabled={busy || !teamId} onClick={saveDraft}>{busy ? "Menyimpan…" : "Setujui pembagian dan simpan draf"}</button></> : <p>Akun ini dapat memeriksa pembagian, tetapi tidak memiliki kewenangan membuat draf.</p>}</div>
        </>}
      </section>
    </div>
  );
}
