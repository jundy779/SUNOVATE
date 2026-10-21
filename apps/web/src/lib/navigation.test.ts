import { describe, expect, it } from "vitest";
import { devLoginSchema, hermesQuerySchema } from "@sunovate/contracts";
import { visibleNavItems } from "./navigation";
import { zodResolver } from "./zod-resolver";

describe("visibleNavItems", () => {
  it("hides items without permission (cosmetic; API still enforces)", () => {
    const labels = visibleNavItems(["work:read", "knowledge:read"]).map((i) => i.label);
    expect(labels).toEqual(["Ringkasan", "Basis Pengetahuan", "Monitoring Kerja"]);
  });

  it("shows the review queue to requesters and decision makers", () => {
    expect(visibleNavItems(["approval:request"]).map((i) => i.href)).toEqual(["/approvals"]);
    expect(visibleNavItems(["approval:decide"]).map((i) => i.href)).toEqual(["/approvals"]);
  });

  it("shows administration for auditors", () => {
    expect(visibleNavItems(["audit:read"]).map((i) => i.href)).toEqual(["/admin"]);
  });

  it("shows the confidential document list to document readers", () => {
    expect(visibleNavItems(["document:read"]).map((i) => i.href)).toEqual(["/dokumen-rahasia"]);
  });

  it("shows SAVI validation only to the publication role", () => {
    expect(visibleNavItems(["knowledge:review"]).map((i) => i.href)).toEqual([]);
    expect(visibleNavItems(["knowledge:publish"]).map((i) => i.href)).toEqual([
      "/savi-validation",
    ]);
  });
});

describe("contracts", () => {
  it("accepts only simulated development accounts", () => {
    expect(devLoginSchema.safeParse({ email: "sim.admin@sunovate.local" }).success).toBe(true);
    expect(devLoginSchema.safeParse({ email: "pegawai@kemenkeu.go.id" }).success).toBe(false);
  });

  it("bounds SAVI AI question length", () => {
    expect(hermesQuerySchema.safeParse({ question: "ab" }).success).toBe(false);
    expect(hermesQuerySchema.safeParse({ question: "x".repeat(2001) }).success).toBe(false);
  });
});

describe("zodResolver", () => {
  it("maps zod issues to field errors", async () => {
    const resolve = zodResolver(hermesQuerySchema);
    const result = await resolve({ question: "" }, undefined, {
      fields: {},
      shouldUseNativeValidation: false,
    });
    expect(result.errors.question?.message).toBe("Pertanyaan minimal 3 karakter");
  });
});
