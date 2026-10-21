import type { Metadata } from "next";
import Link from "next/link";
import type { SecureDocumentSummary } from "@sunovate/contracts";
import { apiGet } from "@/lib/api";
import { classificationLabel } from "@/lib/ui-labels";
import { SecureViewer } from "./secure-viewer";

export const metadata: Metadata = { title: "Dokumen Rahasia" };

export default async function SecureDocumentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { data: document } = await apiGet<SecureDocumentSummary>(`/secure-documents/${encodeURIComponent(id)}`);
  return (
    <div className="sv">
      <Link className="text-link" href="/dokumen-rahasia">Kembali ke daftar dokumen rahasia</Link>
      <header className="sv-head">
        <p className="kicker">{classificationLabel(document.classificationCode)}, tim {document.ownerTeamCode}</p>
        <h1>{document.title}</h1>
      </header>
      <SecureViewer documentId={document.id} pageCount={document.pageCount} title={document.title} />
    </div>
  );
}
