import type { Metadata } from "next";
import Link from "next/link";
import type { SecureDocumentSummary } from "@sunovate/contracts";
import { EmptyState } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { classificationLabel } from "@/lib/ui-labels";

export const metadata: Metadata = { title: "Dokumen Rahasia" };

export default async function SecureDocumentsPage() {
  const { data: documents } = await apiGet<SecureDocumentSummary[]>("/secure-documents");
  return (
    <div className="sv">
      <header className="db-masthead">
        <div>
          <p className="kicker">Dokumen rahasia</p>
          <h1>Dokumen yang boleh Anda baca</h1>
          <p className="db-standfirst">
            Dokumen di halaman ini hanya dapat dibaca. Tidak tersedia unduhan, salinan, atau cetak, dan setiap halaman
            yang dibuka tercatat atas nama Anda.
          </p>
        </div>
      </header>

      {documents.length ? (
        <ul className="sv-list">
          {documents.map((document) => (
            <li key={document.id}>
              <span className="db-headline-type">{classificationLabel(document.classificationCode)}, tim {document.ownerTeamCode}</span>
              <Link href={`/dokumen-rahasia/${document.id}`}>{document.title}</Link>
              <small>{document.pageCount} halaman, hanya untuk dibaca</small>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState
          title="Belum ada dokumen rahasia untuk Anda"
          description="Akses diberikan per dokumen oleh pejabat berwenang. Hubungi pengelola pengetahuan bila Anda memerlukannya."
        />
      )}

      <p className="db-note">Data contoh. Dokumen di lingkungan ini fiktif dan tidak berisi informasi Direktorat SUN.</p>
    </div>
  );
}
