import { describe, expect, it } from "vitest";
import type { WorkItem } from "@sunovate/contracts";
import { filterItems, sortItems } from "./work-table";

const item = (overrides: Partial<WorkItem>): WorkItem => ({
  id: overrides.title ?? "x",
  title: "Contoh",
  status: "IN_PROGRESS",
  ownerTeamCode: "PPSUN",
  classificationCode: "INTERNAL",
  deadlineState: "SAFE",
  dueDate: null,
  revision: 1,
  ...overrides,
});

const rows = [
  item({ title: "Validasi regulasi", ownerTeamCode: "PSUN", dueDate: "2026-10-05", deadlineState: "OVERDUE" }),
  item({ title: "Arsip notulen", status: "COMPLETED", dueDate: null, deadlineState: "COMPLETED" }),
  item({ title: "Kurasi playbook", dueDate: "2026-10-30", deadlineState: "SAFE" }),
];

describe("work table helpers", () => {
  it("filters by title text, status, and team together", () => {
    expect(filterItems(rows, { query: "KURASI", status: "", team: "" }).map((r) => r.title)).toEqual(["Kurasi playbook"]);
    expect(filterItems(rows, { query: "", status: "COMPLETED", team: "" }).map((r) => r.title)).toEqual(["Arsip notulen"]);
    expect(filterItems(rows, { query: "", status: "", team: "PSUN" }).map((r) => r.title)).toEqual(["Validasi regulasi"]);
    expect(filterItems(rows, { query: "a", status: "IN_PROGRESS", team: "PPSUN" }).map((r) => r.title)).toEqual(["Kurasi playbook"]);
  });

  it("sorts by date with undated rows last in both directions", () => {
    expect(sortItems(rows, "date", "asc").map((r) => r.title)).toEqual(["Validasi regulasi", "Kurasi playbook", "Arsip notulen"]);
    expect(sortItems(rows, "date", "desc").map((r) => r.title)).toEqual(["Kurasi playbook", "Validasi regulasi", "Arsip notulen"]);
  });

  it("sorts deadlines with the most urgent first and titles alphabetically", () => {
    expect(sortItems(rows, "deadline", "asc")[0]?.title).toBe("Validasi regulasi");
    expect(sortItems(rows, "title", "asc").map((r) => r.title)).toEqual(["Arsip notulen", "Kurasi playbook", "Validasi regulasi"]);
    expect(sortItems(rows, "title", "desc")[0]?.title).toBe("Validasi regulasi");
  });
});
