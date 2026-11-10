import { describe, expect, it } from "vitest";

import nextConfig from "../../next.config";
import robots from "./robots";

describe("private web boundary", () => {
  it("disallows every crawler path", () => {
    expect(robots()).toEqual({ rules: { userAgent: "*", disallow: "/" } });
  });

  const headersFor = async (source: string) => {
    const rules = (await nextConfig.headers?.()) ?? [];
    const rule = rules.find((candidate) => candidate.source === source);
    return Object.fromEntries((rule?.headers ?? []).map(({ key, value }) => [key.toLowerCase(), value]));
  };

  it("sets anti-index and security headers on every path", async () => {
    const headers = await headersFor("/:path*");
    expect(headers["x-robots-tag"]).toContain("noindex");
    expect(headers["referrer-policy"]).toBe("no-referrer");
    expect(headers["content-security-policy"]).toContain("connect-src 'self'");
    expect(headers["x-frame-options"]).toBe("DENY");
  });

  it("never stores pages or API responses, but lets build assets be cached", async () => {
    const source = "/((?!_next/static/|_next/image|brand/).*)";
    expect((await headersFor(source))["cache-control"]).toContain("no-store");
    const pattern = new RegExp(`^${source}$`);
    for (const path of ["/", "/dashboard", "/api/exports/work", "/api/secure-documents/x/pages/1", "/login"]) {
      expect(pattern.test(path), path).toBe(true);
    }
    for (const path of ["/_next/static/chunks/app.js", "/_next/image", "/brand/logo-dsun.png"]) {
      expect(pattern.test(path), path).toBe(false);
    }
    expect((await headersFor("/brand/:path*"))["cache-control"]).toContain("max-age=86400");
  });
});
