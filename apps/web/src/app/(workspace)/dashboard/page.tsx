import type { Metadata } from "next";
import Link from "next/link";
import type { DashboardSummary } from "@sunovate/contracts";
import { DeadlineTag, EmptyState } from "@/components/page-elements";
import { TaskStatusChart } from "@/components/task-status-chart";
import { UiIcon, type IconName } from "@/components/ui-icons";
import { apiGet } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/format";
import { classificationLabel, knowledgeTypeLabel } from "@/lib/ui-labels";

export const metadata: Metadata = { title: "Dashboard" };

interface MetricItem {
  label: string;
  value: number;
  detail: string;
  icon: IconName;
  tone: "navy" | "gold" | "success";
}

export default async function DashboardPage() {
  const { data } = await apiGet<DashboardSummary>("/dashboard/summary");
  const scope = data.scope.allTeams ? "Direktorat Surat Utang Negara" : data.scope.teamCodes.join(", ");
  const metrics: MetricItem[] = [
    { label: "Tugas aktif", value: data.metrics.totalActiveTasks, detail: "Belum berstatus selesai", icon: "document", tone: "navy" },
    { label: "Perlu perhatian", value: data.metrics.attentionCount, detail: "Tenggat perlu ditindaklanjuti", icon: "clock", tone: "gold" },
    { label: "Dalam proses", value: data.metrics.inProgressTasks, detail: "Sedang dikerjakan", icon: "users", tone: "navy" },
    { label: "Selesai minggu ini", value: data.metrics.completedThisWeek, detail: "Berdasarkan waktu pembaruan", icon: "check", tone: "success" },
  ];
  const focusItems = [
    { label: "Tugas terlambat", value: data.metrics.tasksOverdue, href: "/work-monitoring", tone: "risk" },
    { label: "Jatuh tempo dekat", value: data.metrics.tasksDueSoon, href: "/work-monitoring", tone: "warning" },
    { label: "Persetujuan menunggu", value: data.metrics.pendingApprovals, href: "/approvals", tone: "neutral" },
    { label: "Tindak lanjut terbuka", value: data.metrics.openFollowUps, href: "/work-monitoring", tone: "neutral" },
  ] as const;

  return (
    <div className="dashboard-page">
      <header className="dashboard-heading">
        <div>
          <p className="eyebrow">Ruang kerja SUNOVATE</p>
          <h1>Ringkasan kerja</h1>
          <p>Fokus pada pekerjaan prioritas, pengetahuan terbaru, dan tindak lanjut sesuai kewenangan Anda.</p>
        </div>
        <div className="dashboard-heading-side">
          <time dateTime={data.referenceDate}>{formatDate(data.referenceDate)}</time>
          <div className="dashboard-actions">
            <Link className="button secondary" href="/work-monitoring">Buka monitoring</Link>
            <Link className="button" href="/savi-ai">Tanya SAVI AI</Link>
          </div>
        </div>
      </header>

      <section className="dashboard-governance" aria-label="Konteks akses dashboard">
        <div>
          <UiIcon name="users" />
          <span><small>Cakupan akses</small><strong>{scope || "Belum ada tim"}</strong></span>
        </div>
        <div>
          <UiIcon name="shield" />
          <span><small>Klasifikasi tertinggi</small><strong>{classificationLabel(data.scope.clearanceCode)}</strong></span>
        </div>
        <div>
          <UiIcon name="book" />
          <span><small>Sumber ringkasan</small><strong>Data contoh sesuai hak akses</strong></span>
        </div>
      </section>

      <section className="dashboard-metrics" aria-label="Ringkasan pekerjaan">
        {metrics.map((metric) => (
          <article className={`dashboard-metric dashboard-metric-${metric.tone}`} key={metric.label}>
            <span className="metric-icon"><UiIcon name={metric.icon} /></span>
            <div>
              <p>{metric.label}</p>
              <strong>{metric.value}</strong>
              <small>{metric.detail}</small>
            </div>
          </article>
        ))}
      </section>

      <div className="dashboard-command-grid">
        <section className="dashboard-section dashboard-priority" aria-labelledby="priority-heading">
          <header className="dashboard-section-heading">
            <div>
              <p className="eyebrow">Prioritas</p>
              <h2 id="priority-heading">Perlu ditindaklanjuti</h2>
            </div>
            <Link href="/work-monitoring">Lihat semua</Link>
          </header>
          {data.attention.length ? (
            <div className="table-wrap dashboard-task-table">
              <table>
                <thead><tr><th>Uraian</th><th>Penanggung jawab</th><th>Batas waktu</th><th>Status tenggat</th><th><span className="sr-only">Tindakan</span></th></tr></thead>
                <tbody>
                  {data.attention.slice(0, 6).map((item) => (
                    <tr key={`${item.type}-${item.id}`}>
                      <td><strong>{item.title}</strong><small>{item.category} · {item.ownerTeamCode ?? "Tim belum ditetapkan"}</small></td>
                      <td>{item.assigneeName ?? "Belum ditetapkan"}</td>
                      <td>{formatDate(item.dueDate)}</td>
                      <td><DeadlineTag state={item.deadlineState} /></td>
                      <td><Link className="table-action" href="/work-monitoring" aria-label={`Lihat ${item.title}`}>Lihat</Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title="Tidak ada item yang perlu perhatian" description="Tidak ada tenggat terlambat, hari ini, atau dalam waktu dekat pada lingkup akses Anda." />
          )}
        </section>

        <aside className="dashboard-section dashboard-focus" aria-labelledby="focus-heading">
          <header className="dashboard-section-heading">
            <div>
              <p className="eyebrow">Kendali kerja</p>
              <h2 id="focus-heading">Fokus saat ini</h2>
            </div>
          </header>
          <div className="dashboard-focus-list">
            {focusItems.map((item) => (
              <Link href={item.href} key={item.label}>
                <span className={`focus-value focus-${item.tone}`}>{item.value}</span>
                <span><strong>{item.label}</strong><small>Buka rincian dan tindak lanjuti</small></span>
                <UiIcon name="chevron" />
              </Link>
            ))}
          </div>
          <p className="dashboard-focus-note">Angka hanya mencakup catatan yang boleh Anda lihat.</p>
        </aside>
      </div>

      <div className="dashboard-insight-grid">
        <section className="dashboard-section" aria-labelledby="status-heading">
          <header className="dashboard-section-heading">
            <div>
              <p className="eyebrow">Perkembangan</p>
              <h2 id="status-heading">Sebaran status tugas</h2>
            </div>
            <Link href="/work-monitoring">Buka monitoring</Link>
          </header>
          <TaskStatusChart data={data.tasksByStatus} />
        </section>

        <section className="dashboard-section" aria-labelledby="knowledge-heading">
          <header className="dashboard-section-heading">
            <div>
              <p className="eyebrow">Basis pengetahuan</p>
              <h2 id="knowledge-heading">Pengetahuan terbaru</h2>
            </div>
            <Link href="/knowledge">Lihat semua</Link>
          </header>
          {data.recentKnowledge.length ? (
            <ol className="dashboard-knowledge-list">
              {data.recentKnowledge.map((item, index) => (
                <li key={item.id}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <Link href={`/knowledge/${item.id}`}>{item.title}</Link>
                    <small>{knowledgeTypeLabel(item.knowledgeType)} · {item.ownerTeamCode ?? "Direktorat"} · {formatDateTime(item.updatedAt)}</small>
                  </div>
                </li>
              ))}
            </ol>
          ) : (
            <EmptyState title="Belum ada pengetahuan terbaru" description="Bahan yang telah diterbitkan dan boleh Anda akses akan tampil di sini." />
          )}
        </section>
      </div>

      <section className="dashboard-savi" aria-labelledby="savi-heading">
        <div className="dashboard-savi-intro">
          <span className="dashboard-savi-mark"><UiIcon name="chat" /></span>
          <div>
            <p className="eyebrow">Asisten pengetahuan</p>
            <h2 id="savi-heading">SAVI AI</h2>
            <p>Membantu menemukan jawaban dari pengetahuan SUN yang sudah diterbitkan dan boleh Anda akses.</p>
          </div>
        </div>
        <div className="dashboard-savi-capabilities" aria-label="Pengaman SAVI AI">
          <span><UiIcon name="check" /> Menyertakan sumber</span>
          <span><UiIcon name="check" /> Menolak pertanyaan di luar SUN</span>
          <span><UiIcon name="check" /> Meminta pemeriksaan manusia bila perlu</span>
        </div>
        <div className="dashboard-savi-entry">
          <div className="assistant-prompts" aria-label="Contoh pertanyaan">
            <Link href="/savi-ai">Cari panduan kerja terkait SUN</Link>
            <Link href="/savi-ai">Jelaskan ketentuan dari sumber</Link>
            <Link href="/savi-ai">Ringkas bahan yang diterbitkan</Link>
          </div>
          <Link className="assistant-input" href="/savi-ai">
            <span>Tulis pertanyaan kepada SAVI AI</span><span className="assistant-send"><UiIcon name="send" /></span>
          </Link>
        </div>
        <p className="dashboard-savi-policy"><UiIcon name="shield" /> Tahap uji memakai bahan contoh di server internal. Tidak ada data yang dikirim ke layanan AI eksternal.</p>
      </section>

      <section className="dashboard-source-status" aria-labelledby="source-status-title">
        <div className="dashboard-source-heading">
          <UiIcon name="chart" />
          <div>
            <h2 id="source-status-title">Kesiapan sumber indikator SUN</h2>
            <p>Nilai belum ditampilkan sampai sumber, definisi, dan kewenangan akses disetujui.</p>
          </div>
        </div>
        <dl>
          <div><dt>Yield SUN</dt><dd>Sumber data belum tersedia</dd></div>
          <div><dt>Kepemilikan SBN</dt><dd>Sumber data belum tersedia</dd></div>
        </dl>
      </section>

      <p className="dashboard-data-note">Data contoh · Indikator bisnis SUN belum ditampilkan tanpa sumber yang disetujui.</p>
    </div>
  );
}
