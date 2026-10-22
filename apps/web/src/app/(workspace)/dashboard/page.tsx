import type { Metadata } from "next";
import Link from "next/link";
import { GuideWelcome } from "@/components/guide-welcome";
import type { DashboardSummary, Principal } from "@sunovate/contracts";
import { DeadlineTag, EmptyState } from "@/components/page-elements";
import { TaskStatusChart } from "@/components/task-status-chart";
import { UiIcon } from "@/components/ui-icons";
import { apiGet } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/format";
import { classificationLabel, knowledgeTypeLabel } from "@/lib/ui-labels";

export const metadata: Metadata = { title: "Dashboard" };

type Tone = "plain" | "attention" | "done";

export default async function DashboardPage() {
  const [{ data }, { data: principal }] = await Promise.all([
    apiGet<DashboardSummary>("/dashboard/summary"),
    apiGet<Principal>("/auth/me"),
  ]);
  const scope = data.scope.allTeams ? "Seluruh tim Direktorat SUN" : data.scope.teamCodes.join(", ");
  const ledger: { label: string; value: number; detail: string; tone: Tone }[] = [
    { label: "Tugas aktif", value: data.metrics.totalActiveTasks, detail: "Belum berstatus selesai", tone: "plain" },
    { label: "Perlu perhatian", value: data.metrics.attentionCount, detail: "Tenggat terlambat, hari ini, atau dekat", tone: "attention" },
    { label: "Dalam proses", value: data.metrics.inProgressTasks, detail: "Sedang dikerjakan", tone: "plain" },
    { label: "Selesai minggu ini", value: data.metrics.completedThisWeek, detail: "Berdasarkan waktu pembaruan", tone: "done" },
  ];
  const focus = [
    { label: "Tugas terlambat", value: data.metrics.tasksOverdue, href: "/work-monitoring", risk: true },
    { label: "Jatuh tempo dekat", value: data.metrics.tasksDueSoon, href: "/work-monitoring", risk: false },
    { label: "Persetujuan menunggu", value: data.metrics.pendingApprovals, href: "/approvals", risk: false },
    { label: "Tindak lanjut terbuka", value: data.metrics.openFollowUps, href: "/work-monitoring", risk: false },
  ];

  return (
    <div className="db">
      <header className="db-masthead">
        <div>
          <p className="kicker">Ruang kerja</p>
          <h1>Ringkasan kerja</h1>
          <p className="db-standfirst">Pekerjaan yang perlu ditindaklanjuti, pengetahuan terbaru, dan akses ke SAVI AI sesuai kewenangan Anda.</p>
        </div>
        <div className="db-masthead-side">
          <time dateTime={data.referenceDate}>{formatDate(data.referenceDate)}</time>
          <div className="db-actions">
            <Link className="button secondary" href="/work-monitoring">Buka monitoring</Link>
            <Link className="button" href="/savi-ai">Tanya SAVI AI</Link>
          </div>
        </div>
      </header>

      <GuideWelcome userId={principal.id} />

      <dl className="db-context" aria-label="Cakupan ringkasan">
        <div><dt>Cakupan</dt><dd>{scope || "Belum ada tim"}</dd></div>
        <div><dt>Kerahasiaan tertinggi</dt><dd>{classificationLabel(data.scope.clearanceCode)}</dd></div>
        <div><dt>Sumber angka</dt><dd>Data contoh sesuai hak akses</dd></div>
      </dl>

      <section className="db-ledger" aria-label="Ringkasan pekerjaan">
        {ledger.map((item) => (
          <div className={`db-ledger-item db-tone-${item.tone}`} key={item.label}>
            <p>{item.label}</p>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </div>
        ))}
      </section>

      <div className="db-grid">
        <section className="db-block db-block-wide" aria-labelledby="priority-heading">
          <header className="ed-head ed-head-split">
            <div>
              <h2 id="priority-heading">Perlu ditindaklanjuti</h2>
              <p>Diurutkan dari tenggat paling dekat</p>
            </div>
            <div className="db-head-actions">
              {data.attention.length ? (
                <a className="text-link" href="/api/exports/attention" download title="Unduh seluruh pekerjaan mendesak dalam cakupan Anda">Unduh Excel</a>
              ) : null}
              <Link className="text-link" href="/work-monitoring">Lihat semua</Link>
            </div>
          </header>
          {data.attention.length ? (
            <div className="table-wrap db-table">
              <table>
                <thead>
                  <tr><th>Uraian</th><th>Penanggung jawab</th><th>Batas waktu</th><th>Status tenggat</th><th><span className="sr-only">Tindakan</span></th></tr>
                </thead>
                <tbody>
                  {data.attention.slice(0, 6).map((item) => (
                    <tr key={`${item.type}-${item.id}`}>
                      <td><strong>{item.title}</strong><small>{item.category}, {item.ownerTeamCode ?? "tim belum ditetapkan"}</small></td>
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
            <EmptyState title="Tidak ada pekerjaan yang mendesak" description="Tidak ada tenggat terlambat, hari ini, atau dalam waktu dekat pada cakupan Anda." />
          )}
        </section>

        <aside className="db-block" aria-labelledby="focus-heading">
          <header className="ed-head">
            <h2 id="focus-heading">Fokus saat ini</h2>
            <p>Hanya mencakup catatan yang boleh Anda lihat</p>
          </header>
          <ul className="db-focus">
            {focus.map((item) => (
              <li key={item.label}>
                <Link href={item.href}>
                  <strong className={item.risk && item.value > 0 ? "db-focus-risk" : undefined}>{item.value}</strong>
                  <span>{item.label}</span>
                  <UiIcon name="chevron" />
                </Link>
              </li>
            ))}
          </ul>
        </aside>

        <section className="db-block" aria-labelledby="status-heading">
          <header className="ed-head">
            <h2 id="status-heading">Sebaran status tugas</h2>
            <p>Jumlah tugas per status pada cakupan Anda</p>
          </header>
          <TaskStatusChart data={data.tasksByStatus} />
          <p className="ed-source">Sumber: data contoh SUNOVATE</p>
        </section>

        <section className="db-block" aria-labelledby="knowledge-heading">
          <header className="ed-head ed-head-split">
            <div>
              <h2 id="knowledge-heading">Pengetahuan terbaru</h2>
              <p>Bahan yang sudah diterbitkan dan boleh Anda baca</p>
            </div>
            <Link className="text-link" href="/knowledge">Lihat semua</Link>
          </header>
          {data.recentKnowledge.length ? (
            <ul className="db-headlines">
              {data.recentKnowledge.map((item) => (
                <li key={item.id}>
                  <span className="db-headline-type">{knowledgeTypeLabel(item.knowledgeType)}</span>
                  <Link href={`/knowledge/${item.id}`}>{item.title}</Link>
                  <small>{item.ownerTeamCode ?? "Direktorat"}, diperbarui {formatDateTime(item.updatedAt)}</small>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="Belum ada pengetahuan terbaru" description="Bahan yang telah diterbitkan dan boleh Anda akses akan tampil di sini." />
          )}
        </section>
      </div>

      <section className="db-savi" aria-labelledby="savi-heading">
        <div className="db-savi-text">
          <h2 id="savi-heading">Tanya SAVI AI</h2>
          <p>Jawaban disusun dari pengetahuan SUN yang sudah diterbitkan, selalu dengan rujukan. Bila sumber tidak cukup, SAVI AI akan mengatakannya.</p>
        </div>
        <div className="db-savi-entry">
          <Link className="db-savi-input" href="/savi-ai">
            <span>Tulis pertanyaan tentang SUN</span>
            <UiIcon name="send" />
          </Link>
          <div className="db-savi-prompts" aria-label="Contoh pertanyaan">
            <Link href="/savi-ai">Cari panduan kerja terkait lelang</Link>
            <Link href="/savi-ai">Jelaskan ketentuan dari sumber</Link>
            <Link href="/savi-ai">Ringkas bahan yang diterbitkan</Link>
          </div>
        </div>
        <p className="db-savi-policy">Tahap uji memakai bahan contoh di server internal. Tidak ada data yang dikirim ke layanan AI di luar lingkungan ini.</p>
      </section>

      <section className="db-indicators" aria-labelledby="indicator-heading">
        <header className="ed-head">
          <h2 id="indicator-heading">Indikator SUN</h2>
          <p>Nilai baru ditampilkan setelah sumber, definisi, dan kewenangan aksesnya disetujui</p>
        </header>
        <dl>
          <div><dt>Yield SUN</dt><dd>Sumber data belum tersedia</dd></div>
          <div><dt>Kepemilikan SBN</dt><dd>Sumber data belum tersedia</dd></div>
        </dl>
      </section>

      <p className="db-note">Data contoh. Angka di halaman ini belum mewakili data Direktorat SUN.</p>
    </div>
  );
}
