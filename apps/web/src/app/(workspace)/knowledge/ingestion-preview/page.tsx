import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { PageHeader, StatusTag } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { ChunkPreviewWorkbench } from "./workbench";

export const metadata: Metadata = { title: "Pemeriksaan Isi Dokumen" };

export default async function IngestionPreviewPage() {
  const { data: me } = await apiGet<Principal>("/auth/me");
  if (!me.permissions.includes("knowledge:review")) redirect("/unauthorized");

  return (
    <>
      <PageHeader
        eyebrow="Basis Pengetahuan"
        title="Periksa pembagian isi dokumen"
        description="Tinjau cara isi dokumen dibagi menjadi bagian-bagian yang dapat dicari. Tahap ini hanya pemeriksaan dan belum menyimpan atau menerbitkan bahan."
        action={<StatusTag tone="warning">Belum disimpan</StatusTag>}
      />
      <ChunkPreviewWorkbench />
    </>
  );
}
