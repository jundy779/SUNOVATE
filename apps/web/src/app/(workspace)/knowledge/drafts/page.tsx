import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import type { DraftSearchHit, Principal } from "@sunovate/contracts";
import {
  ClassificationTag,
  EmptyState,
  PageHeader,
  StatusTag,
} from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { knowledgeTypeLabel } from "@/lib/ui-labels";

export const metadata: Metadata = { title: "Pencarian Draf" };

type SearchParams = Promise<{ q?: string }>;

export default async function DraftSearchPage({ searchParams }: { searchParams: SearchParams }) {
  const { q = "" } = await searchParams;
  const { data: me } = await apiGet<Principal>("/auth/me");
  if (!me.roles.includes("knowledge_owner") && !me.permissions.includes("knowledge:review")) {
    redirect("/unauthorized");
  }

  const params = new URLSearchParams({ pageSize: "50" });
  if (q.trim().length >= 2) params.set("q", q.trim());
  const { data, meta } = await apiGet<DraftSearchHit[]>(
    `/knowledge/drafts/search?${params.toString()}`,
  );

  return (
    <>
      <PageHeader
        eyebrow="Basis Pengetahuan"
        title="Pencarian draf"
        description="Temukan bahan yang masih disiapkan dalam kewenangan Anda. Draf tidak muncul pada pencarian pengetahuan terbit dan tidak digunakan oleh SAVI."
        action={<Link className="button secondary" href="/knowledge">Kembali ke basis pengetahuan</Link>}
      />
      <aside className="governance-strip" aria-label="Ketentuan akses draf">
        <strong>Ruang kerja terbatas</strong>
        <span>Pemilik melihat drafnya sendiri. Pemeriksa melihat draf sesuai lingkup tim dan klasifikasi.</span>
      </aside>
      <form className="toolbar" role="search" aria-label="Pencarian draf">
        <label>
          <span className="sr-only">Kata kunci draf</span>
          <input type="search" name="q" defaultValue={q} minLength={2} placeholder="Cari judul, ringkasan, atau isi draf" />
        </label>
        <button className="button" type="submit">Cari draf</button>
        {q ? <Link className="button secondary" href="/knowledge/drafts">Bersihkan</Link> : null}
        <span className="muted">{meta.total ?? data.length} draf</span>
      </form>
      {data.length ? (
        <div className="table-wrap panel">
          <table>
            <thead>
              <tr>
                <th scope="col">Draf</th>
                <th scope="col">Jenis</th>
                <th scope="col">Tim</th>
                <th scope="col">Akses</th>
                <th scope="col">Klasifikasi</th>
                <th scope="col">Diperbarui</th>
              </tr>
            </thead>
            <tbody>
              {data.map((hit) => (
                <tr key={hit.knowledgeEntryId}>
                  <td>
                    <Link className="action-link" href={`/knowledge/${hit.knowledgeEntryId}`}>{hit.title}</Link>
                    <small className="table-supporting-text">
                      {hit.sectionLabel ? `${hit.sectionLabel} — ` : ""}{hit.snippet}
                    </small>
                  </td>
                  <td>{knowledgeTypeLabel(hit.knowledgeType)}</td>
                  <td>{hit.ownerTeamCode ?? "-"}</td>
                  <td><StatusTag tone="neutral">{hit.accessReason === "OWNER" ? "Milik saya" : "Untuk diperiksa"}</StatusTag></td>
                  <td><ClassificationTag code={hit.classificationCode} /></td>
                  <td>{formatDateTime(hit.updatedAt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          title={q ? "Draf tidak ditemukan" : "Belum ada draf dalam kewenangan Anda"}
          description={q ? "Periksa kata kunci atau cari bahan lain yang masih disiapkan." : "Draf yang Anda miliki atau perlu Anda periksa akan tampil di halaman ini."}
        />
      )}
    </>
  );
}
