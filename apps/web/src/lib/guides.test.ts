import { describe, expect, it } from "vitest";
import { GUIDES, visibleGuides } from "./guides";

describe("quick guides", () => {
  it("shows only guides the user can act on", () => {
    expect(visibleGuides(["work:read"]).map((g) => g.id)).toEqual(["pekerjaan"]);
    expect(visibleGuides([]).map((g) => g.id)).toEqual([]);
    expect(visibleGuides(["hermes:query", "search:query"]).map((g) => g.id)).toEqual(["mencari", "savi"]);
  });

  it("reserves the reader-management guide for team leads and Kasubdit PMP", () => {
    expect(visibleGuides(["document:read"]).map((g) => g.id)).toEqual(["rahasia"]);
    expect(visibleGuides(["secure_document:manage_team"]).map((g) => g.id)).toEqual(["akses-rahasia"]);
    expect(visibleGuides(["secure_document:manage_all"]).map((g) => g.id)).toEqual(["akses-rahasia"]);
  });

  it("keeps every guide short, linked, and free of technical terms", () => {
    for (const guide of GUIDES) {
      expect(guide.steps.length).toBeGreaterThanOrEqual(3);
      expect(guide.steps.length).toBeLessThanOrEqual(4);
      expect(guide.href.startsWith("/")).toBe(true);
      const text = [guide.title, guide.summary, ...guide.steps.flatMap((s) => [s.title, s.detail])].join(" ");
      expect(text).not.toMatch(/\b(API|endpoint|database|token|Hermes|RAG|upload|dashboard)\b/i);
    }
  });
});
