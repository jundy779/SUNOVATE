import type { Metadata } from "next";
import type { Principal, TeamSummary, WorkItem } from "@sunovate/contracts";
import { PageHeader, SimulatedLabel } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { WorkManagement } from "./work-management";

export const metadata: Metadata = { title: "Monitoring Kerja" };

export default async function WorkMonitoringPage() {
  const [outputs, tasks, milestones, pending, followUps, principal, teams] = await Promise.all([
    apiGet<WorkItem[]>("/work-outputs?pageSize=100"),
    apiGet<WorkItem[]>("/tasks?pageSize=100"),
    apiGet<WorkItem[]>("/milestones?pageSize=100"),
    apiGet<WorkItem[]>("/pending-matters?pageSize=100"),
    apiGet<WorkItem[]>("/follow-ups?pageSize=100"),
    apiGet<Principal>("/auth/me"),
    apiGet<TeamSummary[]>("/teams?pageSize=100"),
  ]);
  return (
    <>
      <PageHeader
        eyebrow="Kinerja Tim Kerja"
        title="Monitoring pekerjaan"
        description="Output, tugas, dan hal yang perlu ditindaklanjuti dalam cakupan tim serta klasifikasi Anda. Status tenggat diperbarui oleh sistem."
        action={<SimulatedLabel />}
      />
      <WorkManagement
        initial={{ outputs: outputs.data, tasks: tasks.data, milestones: milestones.data, pending: pending.data, followUps: followUps.data }}
        principal={principal.data}
        teams={teams.data}
      />
    </>
  );
}
