import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { HermesChat } from "@/components/hermes-chat";
import { PageHeader, Panel, SimulatedLabel } from "@/components/page-elements";
import { UiIcon } from "@/components/ui-icons";
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
      <section className="savi-boundary-grid" aria-label="Batas kerja SAVI AI">
        <div><UiIcon name="book" /><span><strong>Sumber terkendali</strong><small>Hanya memakai pengetahuan terbit yang boleh Anda akses.</small></span></div>
        <div><UiIcon name="shield" /><span><strong>Tetap dalam lingkup SUN</strong><small>Pertanyaan di luar SUN atau upaya membuka data akan ditolak.</small></span></div>
        <div><UiIcon name="users" /><span><strong>Keputusan tetap pada manusia</strong><small>SAVI tidak menerbitkan atau mengubah data secara otomatis.</small></span></div>
      </section>
      <p className="notice savi-trial-notice">
        Tahap uji ini memakai bahan contoh di lingkungan SUNOVATE. Jawaban disusun dari potongan
        sumber yang tersedia dan tidak dikirim ke layanan AI eksternal.
      </p>
      <Panel title="Percakapan">
        <HermesChat />
      </Panel>
    </>
  );
}

