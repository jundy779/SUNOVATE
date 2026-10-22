import type { Metadata } from "next";
import Link from "next/link";
import type { SecureDocumentSummary } from "@sunovate/contracts";
import { EmptyState } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { classificationLabel } from "@/lib/ui-labels";
import { ReaderManager } from "./reader-manager";

export const metadata: Metadata = { title: "Kelola Akses Dokumen Rahasia" };

type ManageableDocument = SecureDocumentSummary & { readerCount: number };

export default async function ManageSecureAccessPage() {
  const { data: documents } = await apiGet<ManageableDocument[]>("/secure-documents/manageable");
  const readers = await Promise.all(
    documents.map((document) => apiGet<{ email: string }[]>(`/secure-documents/${document.id}/readers`)),
  );
  return (
    <div className="sv">
      <Link className="text-link" href="/dokumen-rahasia">Kembali ke daftar dokumen rahasia</Link>
      <header className="db-masthead">
        <div>
          <p className="kicker">Dokumen rahasia</p>
          <h1>Kelola akses baca</h1>
          <p className="db-standfirst">
            Pembaca dokumen rahasia ditentukan oleh ketua tim pemilik dokumen dan oleh Kasubdit PMP untuk seluruh tim.
            Pembaca boleh dari tim lain, dan setiap perubahan tercatat. Halaman ini tidak menampilkan isi dokumen.
          </p>
        </div>
      </header>
      {documents.length ? (
        documents.map((document, index) => (
          <section className="sv-manage" key={document.id} aria-labelledby={`doc-${document.id}`}>
            <header className="ed-head">
              <h2 id={`doc-${document.id}`}>{document.title}</h2>
              <p>
                {classificationLabel(document.classificationCode)}, tim {document.ownerTeamCode}, {document.pageCount} halaman
              </p>
            </header>
            <ReaderManager documentId={document.id} initialReaders={(readers[index]?.data ?? []).map((reader) => reader.email)} />
          </section>
        ))
      ) : (
        <EmptyState
          title="Tidak ada dokumen yang dapat Anda kelola"
          description="Pengelolaan akses hanya tersedia bagi Kasubdit PMP dan ketua tim pemilik dokumen."
        />
      )}
    </div>
  );
}
