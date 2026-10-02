import Link from "next/link";
import type { ReactNode } from "react";
import type { Principal } from "@sunovate/contracts";
import { logoutAction } from "@/app/login/actions";
import { visibleNavItems } from "@/lib/navigation";

export function AppShell({ principal, children }: { principal: Principal; children: ReactNode }) {
  const scope = principal.allTeams
    ? "Semua tim"
    : principal.teams.map((team) => team.code).join(", ") || "Tanpa tim";
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-inner">
          <Link className="brand" href="/dashboard">
            <span>SUNOVATE</span>
            <small>DJPPR - Direktorat SUN</small>
          </Link>
          <nav aria-label="Navigasi utama">
            {visibleNavItems(principal.permissions).map((item) => (
              <Link href={item.href} key={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="sidebar-note">
            <strong>Lingkungan pengembangan</strong>
            <span>Seluruh data: SIMULATED_DATA</span>
            <span>Integrasi produksi: nonaktif</span>
          </div>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <strong>{principal.displayName}</strong>
            <span>
              {principal.roles.join(", ")} - {scope} - clearance {principal.clearanceCode}
            </span>
          </div>
          <form action={logoutAction}>
            <button className="button secondary" type="submit">
              Keluar
            </button>
          </form>
        </header>
        <main id="main-content">{children}</main>
      </div>
    </div>
  );
}
