"use client";

import { useState } from "react";
import type { FormEvent } from "react";

interface ChunkItem {
  index: number;
  sectionLabel: string;
  content: string;
  wordCount: number;
  contentHash: string;
}

interface PreviewData {
  documentLabel: string;
  knowledgeType: string;
  chunkCount: number;
  totalWords: number;
  persisted: false;
  chunks: ChunkItem[];
}

const TYPE_OPTIONS = [
  ["REGULATION", "Peraturan"],
  ["SOP", "Prosedur kerja"],
  ["PLAYBOOK", "Panduan kerja"],
  ["STUDY", "Kajian"],
  ["REPORT", "Laporan"],
  ["MEETING_MATERIAL", "Bahan rapat"],
  ["LESSON_LEARNED", "Catatan pembelajaran"],
  ["OTHER", "Pengetahuan lainnya"],
] as const;

const SAMPLE_TEXT = `Pasal 1
Ketentuan pertama untuk simulasi pemeriksaan isi dokumen SUN.

Pasal 2
Ketentuan kedua menjelaskan tahapan verifikasi dan persetujuan oleh pejabat yang berwenang.`;

export function ChunkPreviewWorkbench() {
  const [title, setTitle] = useState("SIMULASI - Bahan pemeriksaan dokumen SUN");
  const [type, setType] = useState("REGULATION");
  const [text, setText] = useState(SAMPLE_TEXT);
  const [result, setResult] = useState<PreviewData | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    setResult(null);
    try {
      const response = await fetch("/api/knowledge/chunk-preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentLabel: title, knowledgeType: type, extractedText: text, maxWords: 400 }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message ?? "Pemeriksaan belum dapat dilakukan");
      setResult(payload.data as PreviewData);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Pemeriksaan belum dapat dilakukan");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ingestion-layout">
      <form className="ingestion-form" onSubmit={submit}>
        <div className="ingestion-heading">
          <div><p className="eyebrow">Bahan contoh</p><h2>Isi yang akan diperiksa</h2></div>
          <span className="data-label">Data simulasi</span>
        </div>
        <div className="ingestion-fields">
          <label>
            Nama bahan
            <input value={title} minLength={3} maxLength={255} onChange={(event) => setTitle(event.target.value)} required />
          </label>
          <label>
            Jenis pengetahuan
            <select value={type} onChange={(event) => setType(event.target.value)}>
              {TYPE_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <label className="ingestion-text">
            Teks hasil pembacaan dokumen
            <textarea value={text} minLength={20} maxLength={100000} rows={14} onChange={(event) => setText(event.target.value)} required />
            <small>Gunakan teks contoh tanpa informasi rahasia. Berkas asli belum diunggah pada tahap ini.</small>
          </label>
        </div>
        {message ? <p className="ingestion-error" role="alert">{message}</p> : null}
        <div className="ingestion-actions">
          <button className="button secondary" type="button" onClick={() => { setResult(null); setMessage(""); }}>Bersihkan hasil</button>
          <button className="button" type="submit" disabled={busy}>{busy ? "Memeriksa…" : "Periksa pembagian"}</button>
        </div>
      </form>

      <section className="ingestion-results" aria-live="polite">
        <div className="ingestion-heading">
          <div><p className="eyebrow">Hasil pemeriksaan</p><h2>Bagian isi dokumen</h2></div>
          {result ? <span className="status status-neutral">{result.chunkCount} bagian</span> : null}
        </div>
        {!result ? (
          <div className="ingestion-empty"><strong>Belum ada hasil</strong><p>Isi bahan di sebelah kiri, lalu pilih “Periksa pembagian”.</p></div>
        ) : (
          <>
            <div className="ingestion-summary">
              <div><strong>{result.chunkCount}</strong><span>Bagian</span></div>
              <div><strong>{result.totalWords}</strong><span>Jumlah kata</span></div>
              <div><strong>Tidak</strong><span>Disimpan</span></div>
            </div>
            <div className="chunk-list">
              {result.chunks.map((chunk) => (
                <article key={chunk.contentHash}>
                  <header><span>{String(chunk.index + 1).padStart(2, "0")}</span><h3>{chunk.sectionLabel}</h3><small>{chunk.wordCount} kata</small></header>
                  <p>{chunk.content}</p>
                  <footer>Kode pemeriksaan: {chunk.contentHash.slice(0, 12)}</footer>
                </article>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
