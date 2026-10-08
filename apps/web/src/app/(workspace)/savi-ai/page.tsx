import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { HermesChat } from "@/components/hermes-chat";
import { PageHeader, Panel, SimulatedLabel } from "@/components/page-elements";
import { apiGet } from "@/lib/api";

export const metadata: Metadata = { title: "SAVI AI" };

export default async function SaviAiPage() {
  // UX shortcut only; the API rejects queries without hermes:query regardless.
  const { data: me } = await apiGet<Principal>("/auth/me");
  if (!me.permissions.includes("hermes:query")) redirect("/unauthorized");
  return (
    <>
      <PageHeader
        eyebrow="SAVI AI"
        title="Asisten pengetahuan berbasis sumber"
        description="SAVI AI menjawab hanya dari pengetahuan terbit yang boleh Anda akses, selalu dengan sitasi. SAVI AI tidak mengakses database secara langsung, tidak memberi keputusan keuangan, dan tidak menjalankan perubahan data tanpa persetujuan manusia."
        action={<SimulatedLabel />}
      />
      <p className="notice">
        Penyedia AI pengembangan bersifat ekstraktif dan deterministik. Tidak ada model eksternal
        dan tidak ada data yang dikirim ke pihak ketiga.
      </p>
      <Panel title="Percakapan">
        <HermesChat />
      </Panel>
    </>
  );
}
