import type { WorkItem } from "@sunovate/contracts";

export const EXPORT_KINDS = ["outputs", "tasks", "milestones", "pending", "followUps"] as const;
export type ExportKind = (typeof EXPORT_KINDS)[number];

export type SortKey = "title" | "team" | "status" | "date" | "deadline";
export type SortDirection = "asc" | "desc";

export interface TableFilters {
  query: string;
  status: string;
  team: string;
}

// Most urgent first when sorting by deadline state ascending.
const DEADLINE_ORDER: Record<string, number> = { OVERDUE: 0, DUE_TODAY: 1, DUE_SOON: 2, SAFE: 3, COMPLETED: 4 };

export function itemDate(item: WorkItem): string | null {
  return item.targetDate ?? item.dueDate ?? null;
}

export function filterItems(items: WorkItem[], filters: TableFilters): WorkItem[] {
  const query = filters.query.trim().toLocaleLowerCase("id");
  return items.filter(
    (item) =>
      (!query || item.title.toLocaleLowerCase("id").includes(query)) &&
      (!filters.status || item.status === filters.status) &&
      (!filters.team || item.ownerTeamCode === filters.team),
  );
}

function compare(a: WorkItem, b: WorkItem, key: SortKey): number {
  switch (key) {
    case "title":
      return a.title.localeCompare(b.title, "id");
    case "team":
      return (a.ownerTeamCode ?? "").localeCompare(b.ownerTeamCode ?? "", "id");
    case "status":
      return a.status.localeCompare(b.status);
    case "deadline":
      return (DEADLINE_ORDER[a.deadlineState ?? ""] ?? 9) - (DEADLINE_ORDER[b.deadlineState ?? ""] ?? 9);
    case "date": {
      const left = itemDate(a);
      const right = itemDate(b);
      if (left === right) return 0;
      if (left === null) return 1; // undated rows stay last
      if (right === null) return -1;
      return left.localeCompare(right);
    }
  }
}

export function sortItems(items: WorkItem[], key: SortKey, direction: SortDirection): WorkItem[] {
  const sign = direction === "asc" ? 1 : -1;
  return [...items].sort((a, b) => {
    const result = compare(a, b, key);
    if (key === "date" && (itemDate(a) === null || itemDate(b) === null)) return result;
    return sign * result || a.title.localeCompare(b.title, "id");
  });
}
