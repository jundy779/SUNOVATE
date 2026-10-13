import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import type { Principal } from "@sunovate/contracts";
import { logoutAction } from "@/app/login/actions";
import { WorkspaceNav } from "@/components/workspace-nav";
import { UiIcon } from "@/components/ui-icons";
import { classificationLabel } from "@/lib/ui-labels";

export function AppShell({ principal, children }: { principal: Principal; children: ReactNode }) {
  const scope = principal.allTeams
    ? "Semua tim"
    : principal.teams.map((team) => team.code).join(", ") || "Tanpa tim";
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-inner">
          <Link className="brand" href="/dashboard">
            <Image src="/brand/logo-dsun.png" alt="Direktorat Surat Utang Negara" width={142} height={63} priority />
            <span>SUNOVATE</span>
            <small>Ruang pengetahuan dan transformasi</small>
          </Link>
          <WorkspaceNav permissions={principal.permissions} />
          <div className="sidebar-note">
            <strong>Lingkungan pengembangan</strong>
            <span>Seluruh informasi: data contoh</span>
            <span>Belum terhubung ke layanan operasional</span>
          </div>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <form className="global-search" role="search" action="/search">
            <label className="sr-only" htmlFor="global-search">Cari pengetahuan</label>
            <input id="global-search" name="q" type="search" minLength={2} maxLength={200}
              placeholder="Cari dokumen, informasi, atau topik" />
          </form>
          <button className="notification-button" type="button" aria-label="Notifikasi pengembangan">
            <UiIcon name="bell" />
            <span aria-hidden="true" />
          </button>
          <details className="account-menu">
            <summary className="topbar-account">
              <div className="user-avatar" aria-hidden="true">{principal.displayName.slice(0, 1)}</div>
              <div>
                <strong>{principal.displayName}</strong>
                <span>{scope} · {classificationLabel(principal.clearanceCode)}</span>
              </div>
              <UiIcon className="account-chevron" name="chevron" />
            </summary>
            <div className="account-popover">
              <span>Akun simulasi</span>
              <form action={logoutAction}>
                <button className="text-button" type="submit">Keluar</button>
              </form>
            </div>
          </details>
        </header>
        <main id="main-content">{children}</main>
      </div>
    </div>
  );
}
