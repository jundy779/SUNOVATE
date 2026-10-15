export interface NavItem {
  label: string;
  href: string;
  /** Any of these permissions shows the item. Cosmetic only: the API enforces access. */
  anyOf: string[];
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Ringkasan", href: "/dashboard", anyOf: ["work:read"] },
  { label: "Basis Pengetahuan", href: "/knowledge", anyOf: ["knowledge:read"] },
  { label: "Antrean Pemeriksaan", href: "/approvals", anyOf: ["approval:request", "approval:decide"] },
  { label: "Pencarian", href: "/search", anyOf: ["search:query"] },
  { label: "Monitoring Kerja", href: "/work-monitoring", anyOf: ["work:read"] },
  { label: "SAVI AI", href: "/savi-ai", anyOf: ["hermes:query"] },
  { label: "Pemeriksaan SAVI", href: "/savi-validation", anyOf: ["knowledge:publish"] },
  { label: "Administrasi", href: "/admin", anyOf: ["user:read", "role:read", "audit:read"] },
];

export function visibleNavItems(permissions: readonly string[]): NavItem[] {
  const granted = new Set(permissions);
  return NAV_ITEMS.filter((item) => item.anyOf.some((permission) => granted.has(permission)));
}
