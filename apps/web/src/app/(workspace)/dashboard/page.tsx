import type { Metadata } from "next";
import Link from "next/link";
import type { DashboardSummary } from "@sunovate/contracts";
import {
  DeadlineTag,
  EmptyState,
  PageHeader,
  Panel,
  SimulatedLabel,
} from "@/components/page-elements";
import { TaskStatusChart } from "@/components/task-status-chart";
import { apiGet } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/format";

export const metadata: Metadata = { title: "Dashboard" };

export default async function DashboardPage() {
  const { data } = await apiGet<DashboardSummary>("/dashboard/summary");
  const metrics = [
    ["Output aktif", data.metrics.activeOutputs],
    ["Tugas jatuh tempo dekat", data.metrics.tasksDueSoon],
    ["Tugas terlambat", data.metrics.tasksOverdue],
    ["Pending matters terbuka", data.metrics.openPendingMatters],
  ] as const;
  const scope = data.scope.allTeams ? "semua tim" : data.scope.teamCodes.join(", ");

  return (
    <>
      <PageHeader
        eyebrow="Management cockpit"
        title="Ringkasan kerja sesuai hak akses"
        description={`Cakupan: ${scope}. Tanggal acuan ${formatDate(data.referenceDate)}. Indikator berstatus usulan dan menunggu validasi mentor.`}
        action={<SimulatedLabel />}
      />

      <section className="metric-grid" aria-label="Ringkasan status">
        {metrics.map(([label, value]) => (
          <article className="metric" key={label}>
            <p>{label}</p>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <Panel
        eyebrow="Prioritas"
        title="Perlu perhatian"
        action={<Link href="/work-monitoring">Lihat monitoring kerja</Link>}
      >
        {data.attention.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Item</th>
                  <th scope="col">Jenis</th>
                  <th scope="col">Tim</th>
                  <th scope="col">Tenggat</th>
                  <th scope="col">Status tenggat</th>
                </tr>
              </thead>
              <tbody>
                {data.attention.map((item) => (
                  <tr key={item.id}>
                    <td>{item.title}</td>
                    <td>{item.type === "TASK" ? "Tugas" : "Tindak lanjut"}</td>
                    <td>{item.ownerTeamCode ?? "-"}</td>
                    <td>{formatDate(item.dueDate)}</td>
                    <td>
                      <DeadlineTag state={item.deadlineState} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="Tidak ada item mendesak"
            description="Tidak ada tugas atau tindak lanjut yang terlambat atau jatuh tempo dekat dalam cakupan Anda."
          />
        )}
      </Panel>

      <div className="two-column">
        <Panel title="Tugas per status">
          <TaskStatusChart data={data.tasksByStatus} />
        </Panel>
        <Panel title="Knowledge terbaru" action={<Link href="/knowledge">Buka Knowledge Hub</Link>}>
          {data.recentKnowledge.length ? (
            <ul className="list">
              {data.recentKnowledge.map((entry) => (
                <li key={entry.id}>
                  <Link href={`/knowledge/${entry.id}`}>{entry.title}</Link>
                  <span>
                    {entry.knowledgeType} - {entry.ownerTeamCode} -{" "}
                    {formatDateTime(entry.updatedAt)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="Belum ada knowledge terbit" />
          )}
        </Panel>
      </div>
    </>
  );
}
