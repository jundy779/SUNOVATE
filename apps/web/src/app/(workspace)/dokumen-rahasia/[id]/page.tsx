import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { SecureDocumentSummary } from "@sunovate/contracts";
import { apiGet, ApiRequestError } from "@/lib/api";
import { isUuid } from "@/lib/secure-documents";
import { classificationLabel } from "@/lib/ui-labels";
import { SecureViewer } from "./secure-viewer";

export const metadata: Metadata = { title: "Dokumen Rahasia" };

export default async function SecureDocumentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!isUuid(id)) notFound();
  let document: SecureDocumentSummary;
  try {
    ({ data: document } = await apiGet<SecureDocumentSummary>(`/secure-documents/${id}`));
  } catch (error) {
    // Missing and not-granted documents look identical. Because the workspace streams behind a
    // loading boundary, this is a soft 404 (status 200 with noindex), as documented in ADR-020.
    if (error instanceof ApiRequestError && error.status === 404) notFound();
    throw error;
  }
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
