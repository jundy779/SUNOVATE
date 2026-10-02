import type { Metadata } from "next";
import Link from "next/link";
import type { KnowledgeEntry } from "@sunovate/contracts";
import { KNOWLEDGE_STATUSES } from "@sunovate/shared-types";
import {
  ClassificationTag,
  EmptyState,
  PageHeader,
  SimulatedLabel,
  StatusTag,
} from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export const metadata: Metadata = { title: "Knowledge Hub" };

type SearchParams = Promise<{ q?: string; status?: string }>;

export default async function KnowledgePage({ searchParams }: { searchParams: SearchParams }) {
  const { q = "", status = "" } = await searchParams;
  const params = new URLSearchParams({ pageSize: "50" });
  if (q) params.set("q", q);
  if ((KNOWLEDGE_STATUSES as readonly string[]).includes(status)) params.set("status", status);
  const { data, meta } = await apiGet<KnowledgeEntry[]>(`/knowledge?${params.toString()}`);

  return (
    <>
      <PageHeader
        eyebrow="Knowledge Hub"
        title="Pengetahuan institusional"
        description="Metadata dan ringkasan knowledge yang boleh Anda akses. File resmi tetap berada pada document provider yang disetujui."
        action={<SimulatedLabel />}
      />
      <form className="toolbar" role="search" aria-label="Filter knowledge">
        <label>
          <span className="sr-only">Kata kunci</span>
          <input type="search" name="q" defaultValue={q} placeholder="Cari judul atau ringkasan" />
        </label>
        <label>
          <span className="sr-only">Status</span>
          <select name="status" defaultValue={status}>
            <option value="">Semua status</option>
            {KNOWLEDGE_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <button className="button" type="submit">
          Terapkan
        </button>
        <span className="muted">{meta.total ?? data.length} entri</span>
      </form>
      {data.length ? (
        <div className="table-wrap panel">
          <table>
            <thead>
              <tr>
                <th scope="col">Judul</th>
                <th scope="col">Jenis</th>
                <th scope="col">Tim</th>
                <th scope="col">Status</th>
                <th scope="col">Klasifikasi</th>
                <th scope="col">Diperbarui</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.id}>
                  <td>
                    <Link className="action-link" href={`/knowledge/${entry.id}`}>
                      {entry.title}
                    </Link>
                  </td>
                  <td>{entry.knowledgeType}</td>
                  <td>{entry.ownerTeamCode ?? "-"}</td>
                  <td>
                    <StatusTag tone={entry.lifecycleStatus === "PUBLISHED" ? "success" : "neutral"}>
                      {entry.lifecycleStatus}
                    </StatusTag>
                  </td>
                  <td>
                    <ClassificationTag code={entry.classificationCode} />
                  </td>
                  <td>{formatDateTime(entry.updatedAt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          title="Tidak ada knowledge yang cocok"
          description="Ubah kata kunci atau filter. Hasil hanya memuat entri dalam cakupan tim dan klasifikasi Anda."
        />
      )}
    </>
  );
}
