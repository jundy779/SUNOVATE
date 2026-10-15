import type { Metadata } from "next";
import Link from "next/link";
import type { ApprovalRequest, Principal } from "@sunovate/contracts";
import { ClassificationTag, EmptyState, PageHeader, StatusTag } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export const metadata: Metadata = { title: "Antrean Pemeriksaan" };

type SearchParams = Promise<{ status?: string; teamCode?: string }>;

const STATUS_LABELS: Record<string, string> = {
  PENDING: "Menunggu keputusan",
  APPROVED: "Disetujui",
  REJECTED: "Dikembalikan",
  CANCELLED: "Dibatalkan",
};

function tone(status: string) {
  if (status === "APPROVED") return "success" as const;
  if (status === "REJECTED" || status === "CANCELLED") return "risk" as const;
  return "warning" as const;
}

export default async function ApprovalsPage({ searchParams }: { searchParams: SearchParams }) {
  const { status = "", teamCode = "" } = await searchParams;
  const [{ data: principal }, { data: teams }] = await Promise.all([
    apiGet<Principal>("/auth/me"),
    apiGet<{ id: string; code: string; name: string }[]>("/teams"),
  ]);
  const params = new URLSearchParams({ pageSize: "100", requestType: "KNOWLEDGE_PUBLICATION" });
  if (["PENDING", "APPROVED", "REJECTED", "CANCELLED"].includes(status)) params.set("status", status);
  if (teamCode) params.set("teamCode", teamCode);
  const { data, meta } = await apiGet<ApprovalRequest[]>(`/approvals?${params.toString()}`);
  const pending = data.filter((item) => item.status === "PENDING").length;
  const isReviewer = principal.permissions.includes("approval:decide");

  return (
    <>
      <PageHeader
        eyebrow="Tata kelola pengetahuan"
        title="Antrean pemeriksaan"
        description={isReviewer ? "Tinjau bahan yang menunggu keputusan dalam lingkup kewenangan Anda." : "Pantau status bahan yang telah Anda ajukan untuk diperiksa."}
      />
      <div className="approval-summary" aria-label="Ringkasan antrean">
        <div><strong>{meta.total ?? data.length}</strong><span>Permintaan ditampilkan</span></div>
        <div><strong>{pending}</strong><span>Menunggu keputusan</span></div>
        <div><strong>{isReviewer ? "Pemeriksa" : "Pengaju"}</strong><span>Tampilan sesuai peran</span></div>
      </div>
      <form className="toolbar" aria-label="Penyaringan antrean">
        <label><span className="sr-only">Status</span><select name="status" defaultValue={status}><option value="">Semua status</option>{Object.entries(STATUS_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label><span className="sr-only">Tim</span><select name="teamCode" defaultValue={teamCode}><option value="">Semua tim</option>{teams.map((team) => <option key={team.id} value={team.code}>{team.code} · {team.name}</option>)}</select></label>
        <button className="button" type="submit">Terapkan</button>
        {(status || teamCode) ? <Link className="button secondary" href="/approvals">Bersihkan</Link> : null}
      </form>
      {data.length ? (
        <div className="table-wrap panel approval-table"><table><thead><tr><th>Bahan pengetahuan</th><th>Pengaju</th><th>Tim</th><th>Status</th><th>Klasifikasi</th><th>Diajukan</th><th>Tindak lanjut</th></tr></thead>
          <tbody>{data.map((item) => <tr key={item.id}>
            <td><strong>{item.targetTitle ?? "Bahan tidak tersedia"}</strong><small>{item.requestType === "KNOWLEDGE_PUBLICATION" ? "Pemeriksaan sebelum penerbitan" : "Permintaan tindakan"}</small></td>
            <td>{item.requestedByName ?? "Pengguna tidak tersedia"}{item.requestedBy === principal.id ? <small>Pengajuan saya</small> : null}</td>
            <td>{item.ownerTeamCode ?? "-"}</td>
            <td><StatusTag tone={tone(item.status)}>{STATUS_LABELS[item.status] ?? "Status belum dikenal"}</StatusTag></td>
            <td><ClassificationTag code={item.classificationCode} /></td>
            <td>{formatDateTime(item.createdAt)}</td>
            <td>{item.targetEntityId && item.targetTitle ? <Link className="action-link" href={`/knowledge/${item.targetEntityId}`}>{item.status === "PENDING" && isReviewer && item.requestedBy !== principal.id ? "Periksa bahan" : "Buka detail"}</Link> : "-"}</td>
          </tr>)}</tbody>
        </table></div>
      ) : <EmptyState title="Tidak ada permintaan yang cocok" description="Ubah filter atau periksa kembali setelah ada bahan yang diajukan." />}
      <p className="approval-policy-note">Keputusan tetap dilakukan pada detail bahan. Sistem mencegah pengaju memutuskan permintaannya sendiri.</p>
    </>
  );
}
