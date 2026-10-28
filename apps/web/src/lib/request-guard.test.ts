import { describe, expect, it } from "vitest";
import { rejectCrossSite } from "./request-guard";

const request = (headers: Record<string, string>) =>
  new Request("http://localhost:3000/api/hermes", { method: "POST", headers });

describe("rejectCrossSite", () => {
  it("allows the app's own pages", () => {
    expect(rejectCrossSite(request({ origin: "http://localhost:3000", host: "localhost:3000" }))).toBeNull();
    expect(
      rejectCrossSite(
        request({ origin: "https://sunovate.local:8443", host: "sunovate.local", "content-type": "application/json" }),
        { json: true },
      ),
    ).toBeNull();
  });

  it("rejects missing, foreign, or malformed origins", () => {
    expect(rejectCrossSite(request({ host: "localhost:3000" }))?.status).toBe(403);
    expect(rejectCrossSite(request({ origin: "https://penyerang.example", host: "localhost:3000" }))?.status).toBe(403);
    expect(rejectCrossSite(request({ origin: "null", host: "localhost:3000" }))?.status).toBe(403);
  });

  it("requires JSON for JSON endpoints", () => {
    const form = request({ origin: "http://localhost:3000", host: "localhost:3000", "content-type": "text/plain" });
    expect(rejectCrossSite(form, { json: true })?.status).toBe(415);
  });
});
