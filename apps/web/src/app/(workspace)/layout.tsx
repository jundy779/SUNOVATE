import { redirect } from "next/navigation";
import type { Principal } from "@sunovate/contracts";
import { AppShell } from "@/components/app-shell";
import { apiGet } from "@/lib/api";
import { getSessionToken } from "@/lib/session";
import { Providers } from "../providers";

export default async function WorkspaceLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  if (!(await getSessionToken())) redirect("/login");
  const { data: principal } = await apiGet<Principal>("/auth/me");
  return (
    <Providers>
      <AppShell principal={principal}>{children}</AppShell>
    </Providers>
  );
}
