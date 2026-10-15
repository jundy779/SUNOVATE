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
        title="Periksa isi dokumen simulasi"
        description="Baca berkas simulasi secara sementara, periksa hasil pembacaan dan pembagian isinya, lalu simpan sebagai draf bila sudah sesuai. Penerbitan tetap melalui pemeriksaan terpisah."
        action={<StatusTag tone="warning">Ruang draf simulasi</StatusTag>}
      />
      <ChunkPreviewWorkbench teams={teams} canSave={canSave} />
    </>
  );
}
