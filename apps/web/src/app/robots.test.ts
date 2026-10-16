import { describe, expect, it } from "vitest";

import nextConfig from "../../next.config";
import robots from "./robots";

describe("private web boundary", () => {
  it("disallows every crawler path", () => {
    expect(robots()).toEqual({ rules: { userAgent: "*", disallow: "/" } });
  });

  it("sets anti-index and anti-cache headers globally", async () => {
    const rules = await nextConfig.headers?.();
    const headers = Object.fromEntries(
      (rules?.[0]?.headers ?? []).map(({ key, value }) => [key.toLowerCase(), value]),
    );
    expect(headers["cache-control"]).toContain("no-store");
    expect(headers["x-robots-tag"]).toContain("noindex");
    expect(headers["referrer-policy"]).toBe("no-referrer");
    expect(headers["content-security-policy"]).toContain("connect-src 'self'");
  });
});
