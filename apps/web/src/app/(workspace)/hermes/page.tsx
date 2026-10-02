import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { HermesChat } from "@/components/hermes-chat";
import { PageHeader, Panel, SimulatedLabel } from "@/components/page-elements";
import { apiGet } from "@/lib/api";

export const metadata: Metadata = { title: "Hermes" };

export default async function HermesPage() {
  // UX shortcut only; the API rejects queries without hermes:query regardless.
  const { data: me } = await apiGet<Principal>("/auth/me");
  if (!me.permissions.includes("hermes:query")) redirect("/unauthorized");
  return (
    <>
      <PageHeader
        eyebrow="Hermes"
        title="Asisten knowledge berbasis sumber"
        description="Hermes menjawab hanya dari knowledge terbit yang boleh Anda akses, selalu dengan sitasi. Hermes tidak mengakses database secara langsung, tidak memberi keputusan keuangan, dan tidak menjalankan perubahan data tanpa persetujuan manusia."
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
