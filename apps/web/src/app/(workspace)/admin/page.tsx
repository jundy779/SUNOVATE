import type { Metadata } from "next";
import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { EmptyState, PageHeader, Panel, SimulatedLabel, StatusTag } from "@/components/page-elements";
import { apiGet } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export const metadata: Metadata = { title: "Administrasi" };

interface UserRow {
  id: string;
  email: string;
  displayName: string;
  clearanceCode: string;
  roles: string[];
  teamCodes: string[];
}
interface RoleRow {
  code: string;
  name: string;
  permissions: string[];
}
interface AuditRow {
  id: string;
  occurredAt: string;
  action: string;
  entityType: string;
  outcome: string;
  actorUserId: string | null;
}
interface ProviderRow {
  kind: string;
  implementation: string;
  mode: string;
  note: string;
}

export default async function AdminPage() {
  const { data: me } = await apiGet<Principal>("/auth/me");
  const can = (permission: string) => me.permissions.includes(permission);
  if (!can("user:read") && !can("role:read") && !can("audit:read")) redirect("/unauthorized");

  const [users, roles, audit, providers] = await Promise.all([
    can("user:read") ? apiGet<UserRow[]>("/users?pageSize=100") : null,
    can("role:read") ? apiGet<RoleRow[]>("/roles") : null,
    can("audit:read") ? apiGet<AuditRow[]>("/audit-logs?pageSize=20") : null,
    can("provider:read") ? apiGet<ProviderRow[]>("/providers") : null,
  ]);

  return (
    <>
      <PageHeader
        eyebrow="Administrasi"
        title="Pengguna, peran, audit, dan provider"
        description="Tampilan baca saja pada lingkungan pengembangan. Peran dan izin berstatus usulan dan menunggu validasi mentor."
        action={<SimulatedLabel />}
      />
      {users ? (
        <Panel title="Pengguna simulasi">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Nama</th>
                  <th scope="col">Email</th>
                  <th scope="col">Peran</th>
                  <th scope="col">Tim</th>
                  <th scope="col">Clearance</th>
                </tr>
              </thead>
              <tbody>
                {users.data.map((user) => (
                  <tr key={user.id}>
                    <td>{user.displayName}</td>
                    <td>{user.email}</td>
                    <td>{user.roles.join(", ")}</td>
                    <td>{user.teamCodes.join(", ") || "Semua tim (scope)"}</td>
                    <td>{user.clearanceCode}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      ) : null}
      {roles ? (
        <Panel title="Peran dan izin (PROPOSED)">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Peran</th>
                  <th scope="col">Jumlah izin</th>
                  <th scope="col">Izin</th>
                </tr>
              </thead>
              <tbody>
                {roles.data.map((role) => (
                  <tr key={role.code}>
                    <td>{role.code}</td>
                    <td>{role.permissions.length}</td>
                    <td className="wrap">{role.permissions.join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      ) : null}
      {providers ? (
        <Panel title="Status provider integrasi">
          <ul className="list">
            {providers.data.map((p) => (
              <li key={p.kind}>
                <strong>{p.kind}</strong>
                <span>
                  <StatusTag tone={p.mode === "DISABLED" ? "risk" : "warning"}>{p.mode}</StatusTag>{" "}
                  {p.implementation} - {p.note}
                </span>
              </li>
            ))}
          </ul>
        </Panel>
      ) : null}
      {audit ? (
        <Panel title="Audit log terbaru">
          {audit.data.length ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Waktu</th>
                    <th scope="col">Aksi</th>
                    <th scope="col">Entitas</th>
                    <th scope="col">Hasil</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.data.map((row) => (
                    <tr key={row.id}>
                      <td>{formatDateTime(row.occurredAt)}</td>
                      <td>{row.action}</td>
                      <td>{row.entityType}</td>
                      <td>{row.outcome}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title="Belum ada aktivitas tercatat" />
          )}
        </Panel>
      ) : null}
    </>
  );
}
