import type { Metadata } from "next";
import type { WorkItem } from "@sunovate/contracts";
import { TASK_STATUS_LABELS, type TaskStatus } from "@sunovate/shared-types";
import { DeadlineTag, EmptyState, PageHeader, Panel, SimulatedLabel } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { formatDate } from "@/lib/format";

export const metadata: Metadata = { title: "Monitoring Kerja" };

function statusLabel(status: string): string {
  return TASK_STATUS_LABELS[status as TaskStatus] ?? status;
}

function WorkTable({ items, dateKey }: { items: WorkItem[]; dateKey: "dueDate" | "targetDate" }) {
  if (!items.length) return <EmptyState title="Tidak ada data dalam cakupan Anda" />;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th scope="col">Judul</th>
            <th scope="col">Tim</th>
            <th scope="col">Status</th>
            <th scope="col">Progres</th>
            <th scope="col">{dateKey === "dueDate" ? "Tenggat" : "Target"}</th>
            <th scope="col">Status tenggat</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.title}</td>
              <td>{item.ownerTeamCode ?? "-"}</td>
              <td>{statusLabel(item.status)}</td>
              <td>{item.progress === undefined ? "-" : `${item.progress}%`}</td>
              <td>{formatDate(item[dateKey])}</td>
              <td>
                <DeadlineTag state={item.deadlineState} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function WorkMonitoringPage() {
  const [outputs, tasks, pending] = await Promise.all([
    apiGet<WorkItem[]>("/work-outputs?pageSize=100"),
    apiGet<WorkItem[]>("/tasks?pageSize=100"),
    apiGet<WorkItem[]>("/pending-matters?pageSize=100"),
  ]);
  return (
    <>
      <PageHeader
        eyebrow="Kinerja Tim Kerja"
        title="Monitoring pekerjaan"
        description="Output, tugas, dan pending matters dalam cakupan tim dan klasifikasi Anda. Status tenggat dihitung oleh backend."
        action={<SimulatedLabel />}
      />
      <Panel title="Output kerja">
        <WorkTable items={outputs.data} dateKey="targetDate" />
      </Panel>
      <Panel title="Tugas">
        <WorkTable items={tasks.data} dateKey="dueDate" />
      </Panel>
      <Panel title="Pending matters">
        <WorkTable items={pending.data} dateKey="dueDate" />
      </Panel>
    </>
  );
}
