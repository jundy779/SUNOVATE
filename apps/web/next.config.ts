import type { NextConfig } from "next";
import packageJson from "./package.json" with { type: "json" };

const nextConfig: NextConfig = {
  output: "standalone",
  // Workspace packages ship TypeScript sources.
  transpilePackages: ["@sunovate/contracts", "@sunovate/shared-types"],
  poweredByHeader: false,
  // Shown in the public footer so testers can tell which release they are using.
  env: { NEXT_PUBLIC_APP_VERSION: packageJson.version },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Cache-Control", value: "no-store, private, max-age=0, must-revalidate" },
          { key: "Pragma", value: "no-cache" },
          { key: "Expires", value: "0" },
          {
            key: "X-Robots-Tag",
            value: "noindex, nofollow, noarchive, nosnippet, noimageindex",
          },
          {
            key: "Content-Security-Policy",
            value:
              "default-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'; object-src 'none'; img-src 'self' data:; font-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; worker-src 'self'; media-src 'self'; manifest-src 'self'",
          },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "no-referrer" },
          { key: "X-Frame-Options", value: "DENY" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), browsing-topics=()",
          },
          { key: "Cross-Origin-Resource-Policy", value: "same-origin" },
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
        ],
      },
      {
        // RAHASIA page images (ADR-020): the image itself needs no scripts, styles, or fetches.
        // Declared after the site-wide rule so this stricter policy wins (last match overrides).
        source: "/api/secure-documents/:id/pages/:page",
        headers: [
          {
            key: "Content-Security-Policy",
            value: "default-src 'none'; frame-ancestors 'none'; sandbox",
          },
          { key: "Content-Disposition", value: "inline" },
        ],
      },
    ];
  },
};

export default nextConfig;
