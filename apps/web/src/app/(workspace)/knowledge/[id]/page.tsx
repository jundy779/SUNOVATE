import Link from "next/link";
import type { KnowledgeEntry } from "@sunovate/contracts";
import {
  ClassificationTag,
  EmptyState,
  PageHeader,
  Panel,
  SimulatedLabel,
  StatusTag,
} from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export default async function KnowledgeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const { data: entry } = await apiGet<KnowledgeEntry>(`/knowledge/${encodeURIComponent(id)}`);

  return (
    <>
      <nav aria-label="Breadcrumb" className="breadcrumb">
        <Link href="/knowledge">Knowledge Hub</Link> / <span>Detail</span>
      </nav>
      <PageHeader
        eyebrow={`Knowledge Hub - ${entry.knowledgeType}`}
        title={entry.title}
        description={entry.summary}
        action={<SimulatedLabel />}
      />
      <dl className="detail-grid">
        <div>
          <dt>Status</dt>
          <dd>
            <StatusTag tone={entry.lifecycleStatus === "PUBLISHED" ? "success" : "neutral"}>
              {entry.lifecycleStatus}
            </StatusTag>
          </dd>
        </div>
        <div>
          <dt>Klasifikasi</dt>
          <dd>
            <ClassificationTag code={entry.classificationCode} />
          </dd>
        </div>
        <div>
          <dt>Tim pemilik</dt>
          <dd>{entry.ownerTeamCode ?? "-"}</dd>
        </div>
        <div>
          <dt>Berbagi</dt>
          <dd>{entry.sharingScope === "DIRECTORATE" ? "Direktorat (bila terbit)" : "Tim pemilik"}</dd>
        </div>
        <div>
          <dt>Versi / revisi</dt>
          <dd>
            {entry.versionLabel} / r{entry.revision}
          </dd>
        </div>
        <div>
          <dt>Diperbarui</dt>
          <dd>{formatDateTime(entry.updatedAt)}</dd>
        </div>
      </dl>

      <Panel title="Isi per bagian" eyebrow="Teks hasil ekstraksi (simulasi)">
        {entry.sections?.length ? (
          <ol className="sections">
            {entry.sections.map((section) => (
              <li key={section.index}>
                <h3>{section.sectionLabel}</h3>
                <p>{section.content}</p>
              </li>
            ))}
          </ol>
        ) : (
          <EmptyState title="Belum ada teks terindeks" />
        )}
      </Panel>

      <Panel title="Referensi dokumen" eyebrow="File tidak disimpan di SUNOVATE">
        {entry.documents?.length ? (
          <ul className="list">
            {entry.documents.map((doc) => (
              <li key={doc.id}>
                <strong>{doc.title}</strong>
                <span>
                  {doc.provider} - <code>{doc.providerLocation}</code>
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState title="Belum ada referensi dokumen" />
        )}
      </Panel>
      <p className="muted">Sumber: {entry.sourceNote ?? "-"}</p>
    </>
  );
}
