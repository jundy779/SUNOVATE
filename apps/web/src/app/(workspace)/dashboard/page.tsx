import type { Metadata } from "next";
import Link from "next/link";
import type { DashboardSummary } from "@sunovate/contracts";
import { PageHeader, Panel, StatusTag } from "@/components/page-elements";
import { TeamActivityChart } from "@/components/team-activity-chart";
import { UiIcon, type IconName } from "@/components/ui-icons";
import { apiGet } from "@/lib/api";
import { formatDate } from "@/lib/format";

export const metadata: Metadata = { title: "Dashboard" };

const metrics: { label: string; value: number; detail: string; icon: IconName; tone: string }[] = [
  { label: "Total tugas aktif", value: 24, detail: "Dalam berbagai tahapan", icon: "document", tone: "navy" },
  { label: "Perlu perhatian", value: 8, detail: "Memerlukan tindak lanjut", icon: "clock", tone: "gold" },
  { label: "Dalam proses", value: 12, detail: "Sesuai rencana", icon: "users", tone: "navy" },
  { label: "Selesai minggu ini", value: 4, detail: "Tugas yang telah diselesaikan", icon: "check", tone: "success" },
];

const demoTasks = [
  ["Review konsep nota dinas", "Kajian", "Tim A", "8 Okt 2026", "Terlambat", "risk"],
  ["Finalisasi bahan rapat", "Rapat", "Tim B", "9 Okt 2026", "Perlu tindak lanjut", "warning"],
  ["Penyempurnaan pedoman", "Regulasi", "Tim C", "9 Okt 2026", "Dalam proses", "neutral"],
  ["Konfirmasi masukan unit terkait", "Koordinasi", "Tim A", "10 Okt 2026", "Perlu tindak lanjut", "warning"],
  ["Review dokumen pendukung", "Dokumentasi", "Tim D", "10 Okt 2026", "Dalam proses", "neutral"],
  ["Tanggapan atas surat masuk", "Persuratan", "Tim C", "11 Okt 2026", "Perlu tindak lanjut", "warning"],
  ["Pemeriksaan kelengkapan data", "Data", "Tim B", "11 Okt 2026", "Dalam proses", "neutral"],
  ["Penyesuaian materi presentasi", "Rapat", "Tim D", "12 Okt 2026", "Terlambat", "risk"],
] as const;

const qualityRows: { icon: IconName; title: string; detail: string; value: number; tone: "success" | "warning" }[] = [
  { icon: "book", title: "Kelengkapan metadata", detail: "Dokumen memiliki informasi yang lengkap", value: 92, tone: "success" },
  { icon: "tag", title: "Konsistensi klasifikasi", detail: "Sesuai taksonomi yang ditetapkan", value: 78, tone: "warning" },
  { icon: "document", title: "Kualitas konten", detail: "Relevan, mutakhir, dan akurat", value: 88, tone: "success" },
  { icon: "shield", title: "Kepatuhan kebijakan", detail: "Sesuai ketentuan yang berlaku", value: 76, tone: "warning" },
];

export default async function DashboardPage() {
  const { data } = await apiGet<DashboardSummary>("/dashboard/summary");
  const scope = data.scope.allTeams ? "Direktorat Surat Utang Negara" : data.scope.teamCodes.join(", ");

  return (
    <div className="dashboard-page">
      <PageHeader
        eyebrow=""
        title="Ringkasan kerja"
        description={`Gambaran aktivitas, prioritas, dan kualitas pengetahuan di lingkungan ${scope}.`}
        action={<time className="dashboard-date" dateTime={data.referenceDate}>{formatDate(data.referenceDate)}</time>}
      />

      <section className="dashboard-metrics" aria-label="Ringkasan status simulasi">
        {metrics.map((metric) => (
          <article className="dashboard-metric" key={metric.label}>
            <span className={`metric-icon metric-icon-${metric.tone}`}><UiIcon name={metric.icon} /></span>
            <div><strong>{metric.value}</strong><h2>{metric.label}</h2><p>{metric.detail}</p></div>
          </article>
        ))}
      </section>

      <div className="dashboard-primary-grid">
        <Panel title="Perlu perhatian" action={<Link href="/work-monitoring">Lihat semua</Link>}>
          <div className="table-wrap dashboard-task-table">
            <table>
              <thead><tr><th>No.</th><th>Judul tugas / aktivitas</th><th>Kategori</th><th>Penanggung jawab</th><th>Batas waktu</th><th>Status</th><th>Tindakan</th></tr></thead>
              <tbody>
                {demoTasks.map(([title, category, owner, due, status, tone], index) => (
                  <tr key={title}>
                    <td>{index + 1}</td><td>{title}</td><td>{category}</td><td>{owner}</td><td>{due}</td>
                    <td><StatusTag tone={tone}>{status}</StatusTag></td>
                    <td><Link className="table-action" href="/work-monitoring">Lihat</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Aktivitas tim" action={<span className="period-control">Minggu ini <UiIcon name="chevron" /></span>}>
          <TeamActivityChart />
        </Panel>
      </div>

      <div className="dashboard-secondary-grid">
        <Panel title="Kualitas pengetahuan" action={<Link href="/knowledge">Lihat semua</Link>}>
          <div className="quality-list">
            {qualityRows.map((row) => (
              <div className="quality-row" key={row.title}>
                <UiIcon className="quality-icon" name={row.icon} />
                <div className="quality-copy"><strong>{row.title}</strong><span>{row.detail}</span></div>
                <div className="quality-progress"><span style={{ width: `${row.value}%` }} /></div>
                <strong className="quality-value">{row.value}%</strong>
                <StatusTag tone={row.tone}>{row.tone === "success" ? "Baik" : "Perlu perhatian"}</StatusTag>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="SAVI AI">
          <div className="dashboard-assistant">
            <p>Asisten AI berbasis sumber untuk membantu pencarian informasi dan pekerjaan di Direktorat Surat Utang Negara.</p>
            <div className="assistant-prompts" aria-label="Contoh pertanyaan">
              <Link href="/savi-ai">Ringkas dokumen ini</Link>
              <Link href="/savi-ai">Cari referensi terkait</Link>
              <Link href="/savi-ai">Buat draf tindak lanjut</Link>
              <Link href="/savi-ai">Jelaskan ketentuan ini</Link>
              <Link href="/savi-ai">Bandingkan dua dokumen</Link>
              <Link href="/savi-ai">Saran langkah berikutnya</Link>
            </div>
            <Link className="assistant-input" href="/savi-ai">
              <span>Tulis pertanyaan kepada SAVI AI</span><span className="assistant-send"><UiIcon name="send" /></span>
            </Link>
          </div>
        </Panel>
      </div>

      <p className="dashboard-data-note">SIMULATED_DATA · Indikator dashboard berstatus PROPOSED dan menunggu validasi mentor.</p>
    </div>
  );
}
