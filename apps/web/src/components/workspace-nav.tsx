"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { visibleNavItems } from "@/lib/navigation";
import { UiIcon, type IconName } from "@/components/ui-icons";

const icons: Record<string, IconName> = {
  "/dashboard": "home",
  "/knowledge": "book",
  "/approvals": "check",
  "/search": "search",
  "/work-monitoring": "chart",
  "/savi-ai": "chat",
  "/savi-validation": "shield",
  "/admin": "settings",
};

export function WorkspaceNav({ permissions }: { permissions: readonly string[] }) {
  const pathname = usePathname();

  return (
    <nav aria-label="Navigasi utama">
      {visibleNavItems(permissions).map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <Link aria-current={active ? "page" : undefined} href={item.href} key={item.href}>
            <span className="nav-marker" aria-hidden="true" />
            <UiIcon className="nav-icon" name={icons[item.href] ?? "home"} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

