import type { Metadata } from "next";
import Link from "next/link";
import type { DashboardSummary } from "@sunovate/contracts";
import { DeadlineTag, EmptyState, PageHeader, Panel, StatusTag } from "@/components/page-elements";
import { TeamActivityChart } from "@/components/team-activity-chart";
import { UiIcon, type IconName } from "@/components/ui-icons";
import { apiGet } from "@/lib/api";
import { formatDate } from "@/lib/format";

export const metadata: Metadata = { title: "Dashboard" };

const qualityRows: { icon: IconName; title: string; detail: string; value: number; tone: "success" | "warning" }[] = [
  { icon: "book", title: "Kelengkapan metadata", detail: "Dokumen memiliki informasi yang lengkap", value: 92, tone: "success" },
  { icon: "tag", title: "Konsistensi klasifikasi", detail: "Sesuai taksonomi yang ditetapkan", value: 78, tone: "warning" },
  { icon: "document", title: "Kualitas konten", detail: "Relevan, mutakhir, dan akurat", value: 88, tone: "success" },
  { icon: "shield", title: "Kepatuhan kebijakan", detail: "Sesuai ketentuan yang berlaku", value: 76, tone: "warning" },
];

export default async function DashboardPage() {
  const { data } = await apiGet<DashboardSummary>("/dashboard/summary");
  const scope = data.scope.allTeams ? "Direktorat Surat Utang Negara" : data.scope.teamCodes.join(", ");
  const metrics: { label: string; value: number; detail: string; icon: IconName; tone: string }[] = [
    { label: "Total tugas aktif", value: data.metrics.totalActiveTasks, detail: "Dalam berbagai tahapan", icon: "document", tone: "navy" },
    { label: "Perlu perhatian", value: data.metrics.attentionCount, detail: "Memerlukan tindak lanjut", icon: "clock", tone: "gold" },
    { label: "Dalam proses", value: data.metrics.inProgressTasks, detail: "Sedang dikerjakan", icon: "users", tone: "navy" },
    { label: "Selesai minggu ini", value: data.metrics.completedThisWeek, detail: "Berdasarkan waktu pembaruan", icon: "check", tone: "success" },
  ];

  return (
    <div className="dashboard-page">
      <PageHeader
        eyebrow=""
        title="Ringkasan kerja"
        description={`Gambaran aktivitas, prioritas, dan kualitas pengetahuan di lingkungan ${scope}.`}
        action={<time className="dashboard-date" dateTime={data.referenceDate}>{formatDate(data.referenceDate)}</time>}
      />

      <section className="dashboard-governance" aria-label="Konteks tata kelola dashboard">
        <div>
          <UiIcon name="users" />
          <span><small>Cakupan akses</small><strong>{scope}</strong></span>
        </div>
        <div>
          <UiIcon name="document" />
          <span><small>Status indikator</small><strong>Usulan, menunggu validasi mentor</strong></span>
        </div>
        <div>
          <UiIcon name="shield" />
          <span><small>Aksi SAVI AI</small><strong>Wajib persetujuan manusia</strong></span>
        </div>
      </section>

      <section className="dashboard-metrics" aria-label="Ringkasan status simulasi">
        {metrics.map((metric) => (
          <article className="dashboard-metric" key={metric.label}>
            <span className={`metric-icon metric-icon-${metric.tone}`}><UiIcon name={metric.icon} /></span>
            <div><strong>{metric.value}</strong><h2>{metric.label}</h2><p>{metric.detail}</p></div>
          </article>
        ))}
      </section>

      <section className="dashboard-source-status" aria-labelledby="source-status-title">
        <div className="dashboard-source-heading">
          <UiIcon name="chart" />
          <div>
            <h2 id="source-status-title">Indikator data SUN</h2>
            <p>Nilai tidak ditampilkan sebelum sumber, definisi, dan hak akses disetujui.</p>
          </div>
        </div>
        <dl>
          <div><dt>Yield SUN</dt><dd>Sumber data belum tersedia</dd></div>
          <div><dt>Kepemilikan SBN</dt><dd>Sumber data belum tersedia</dd></div>
        </dl>
      </section>

      <div className="dashboard-primary-grid">
        <Panel title="Perlu perhatian" action={<Link href="/work-monitoring">Lihat semua</Link>}>
          {data.attention.length ? (
            <div className="table-wrap dashboard-task-table">
              <table>
                <thead><tr><th>No.</th><th>Judul tugas / aktivitas</th><th>Kategori</th><th>Penanggung jawab</th><th>Batas waktu</th><th>Status tenggat</th><th>Tindakan</th></tr></thead>
                <tbody>
                  {data.attention.map((item, index) => (
                    <tr key={`${item.type}-${item.id}`}>
                      <td>{index + 1}</td>
                      <td>{item.title}</td>
                      <td>{item.category}</td>
                      <td>{item.assigneeName ?? item.ownerTeamCode ?? "Belum ditetapkan"}</td>
                      <td>{formatDate(item.dueDate)}</td>
                      <td><DeadlineTag state={item.deadlineState} /></td>
                      <td><Link className="table-action" href="/work-monitoring">Lihat</Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title="Tidak ada item yang perlu perhatian" description="Tidak ada tenggat terlambat, hari ini, atau dalam waktu dekat pada lingkup akses Anda." />
          )}
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
