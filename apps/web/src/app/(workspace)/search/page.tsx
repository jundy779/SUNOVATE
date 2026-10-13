import type { Metadata } from "next";
import Link from "next/link";
import type { SearchHit } from "@sunovate/contracts";
import { ClassificationTag, EmptyState, PageHeader, SimulatedLabel } from "@/components/page-elements";
import { apiGet } from "@/lib/api";

export const metadata: Metadata = { title: "Pencarian" };

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();
  const result =
    query.length >= 2 ? await apiGet<SearchHit[]>(`/search?q=${encodeURIComponent(query)}`) : null;

  return (
    <>
      <PageHeader
        eyebrow="Pencarian"
        title="Cari pengetahuan yang telah diterbitkan"
        description="Pencarian leksikal atas judul, ringkasan, dan teks bagian. Hanya entri terbit dalam cakupan Anda yang ditampilkan. Pencarian semantik masih berupa usulan."
        action={<SimulatedLabel />}
      />
      <form className="search-form" role="search" action="/search">
        <label htmlFor="q">Kata kunci</label>
        <div>
          <input id="q" name="q" type="search" defaultValue={query} minLength={2} maxLength={200}
            placeholder="Contoh: metadata dokumen" />
          <button className="button" type="submit">
            Cari
          </button>
        </div>
      </form>
      {!result ? (
        <EmptyState
          title="Belum ada pencarian"
          description="Masukkan minimal dua karakter untuk mencari pengetahuan yang boleh Anda akses."
        />
      ) : result.data.length ? (
        <ol className="results" aria-label={`${result.data.length} hasil`}>
          {result.data.map((hit) => (
            <li key={hit.knowledgeEntryId}>
              <Link className="action-link" href={`/knowledge/${hit.knowledgeEntryId}`}>
                {hit.title}
              </Link>
              <p className="muted">
                {hit.knowledgeType} - {hit.ownerTeamCode} - <ClassificationTag code={hit.classificationCode} />
                {hit.sectionLabel ? ` - ${hit.sectionLabel}` : ""}
              </p>
              <p>{hit.snippet}</p>
            </li>
          ))}
        </ol>
      ) : (
        <EmptyState
          title="Tidak ada hasil"
          description="Tidak ada pengetahuan yang telah diterbitkan dalam cakupan Anda yang cocok dengan kata kunci ini."
        />
      )}
    </>
  );
}
