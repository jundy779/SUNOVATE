import { NextResponse, type NextRequest } from "next/server";

/**
 * Per-request Content-Security-Policy for pages.
 *
 * The site-wide policy in next.config.ts has to allow inline scripts, because the framework
 * writes its page data as inline script blocks. Here every page view gets a fresh random nonce:
 * only scripts carrying that nonce (the framework's own) may run, so text that somehow reaches
 * the page as markup cannot execute as a script. `strict-dynamic` lets those trusted scripts
 * load the application bundles.
 *
 * Styles keep `'unsafe-inline'`: one component sets an inline `style` attribute and style
 * injection cannot run code. API routes, build assets, and brand files are not matched here and
 * keep the static headers from next.config.ts (including the stricter policy for RAHASIA pages).
 */
export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  const development = process.env.NODE_ENV !== "production";
  const policy = [
    "default-src 'self'",
    "base-uri 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "object-src 'none'",
    "img-src 'self' data:",
    "font-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    // React needs eval only for development error overlays.
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${development ? " 'unsafe-eval'" : ""}`,
    "connect-src 'self'",
    "worker-src 'self'",
    "media-src 'self'",
    "manifest-src 'self'",
  ].join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  // Next.js reads the nonce from this request header and applies it to its own scripts.
  requestHeaders.set("Content-Security-Policy", policy);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", policy);
  return response;
}

export const config = {
  matcher: [
    {
      source: "/((?!api/|_next/static|_next/image|brand/|favicon.ico|robots.txt).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
