import Link from "next/link";
import type { ApprovalRequest, KnowledgeEntry, Principal } from "@sunovate/contracts";
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
import { knowledgeStatusLabel, knowledgeTypeLabel } from "@/lib/ui-labels";
import { KnowledgeWorkflow } from "./knowledge-workflow";

export default async function KnowledgeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [{ data: entry }, { data: principal }] = await Promise.all([
    apiGet<KnowledgeEntry>(`/knowledge/${encodeURIComponent(id)}`),
    apiGet<Principal>("/auth/me"),
  ]);
  const approvals = principal.permissions.includes("approval:request") || principal.permissions.includes("approval:decide")
    ? (await apiGet<ApprovalRequest[]>("/approvals?pageSize=100")).data
    : [];
  const approval = approvals.find((item) => item.requestType === "KNOWLEDGE_PUBLICATION" && item.targetEntityId === entry.id) ?? null;

  return (
    <>
      <nav aria-label="Breadcrumb" className="breadcrumb">
        <Link href="/knowledge">Basis Pengetahuan</Link> / <span>Detail</span>
      </nav>
      <PageHeader
        eyebrow={`Basis Pengetahuan · ${knowledgeTypeLabel(entry.knowledgeType)}`}
        title={entry.title}
        description={entry.summary}
        action={<SimulatedLabel />}
      />
      <dl className="detail-grid">
        <div>
          <dt>Status</dt>
          <dd>
            <StatusTag tone={entry.lifecycleStatus === "PUBLISHED" ? "success" : "neutral"}>
              {knowledgeStatusLabel(entry.lifecycleStatus)}
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

      <KnowledgeWorkflow entry={entry} principal={principal} approval={approval} />

      <Panel title="Isi per bagian" eyebrow="Teks hasil pembacaan dokumen (contoh)">
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
          <EmptyState title="Belum ada teks yang dapat ditampilkan" />
        )}
      </Panel>

      <Panel title="Referensi dokumen" eyebrow="Berkas tetap berada di penyimpanan resmi">
        {entry.documents?.length ? (
          <ul className="list">
            {entry.documents.map((doc) => (
              <li key={doc.id}>
                <strong>{doc.title}</strong>
                <span>
                  Lokasi berkas telah tercatat pada layanan penyimpanan yang disetujui.
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
