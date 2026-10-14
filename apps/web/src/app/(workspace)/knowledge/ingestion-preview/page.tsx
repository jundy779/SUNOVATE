import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { PageHeader, StatusTag } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { ChunkPreviewWorkbench } from "./workbench";

export const metadata: Metadata = { title: "Pemeriksaan Isi Dokumen" };

interface TeamOption {
  id: string;
  code: string;
  name: string;
}

export default async function IngestionPreviewPage() {
  const { data: me } = await apiGet<Principal>("/auth/me");
  if (!me.permissions.includes("knowledge:review")) redirect("/unauthorized");
  const required = ["knowledge:create", "document:create", "document:version"];
  const canSave = required.every((permission) => me.permissions.includes(permission));
  const teams = canSave ? (await apiGet<TeamOption[]>("/teams")).data : [];

  return (
    <>
      <PageHeader
        eyebrow="Basis Pengetahuan"
        title="Periksa pembagian isi dokumen"
        description="Tinjau pembagian isi dokumen simulasi. Pengguna berwenang dapat menyimpan hasilnya sebagai draf, tetapi penerbitan tetap melalui pemeriksaan terpisah."
        action={<StatusTag tone="warning">Ruang draf simulasi</StatusTag>}
      />
      <ChunkPreviewWorkbench teams={teams} canSave={canSave} />
    </>
  );
}
