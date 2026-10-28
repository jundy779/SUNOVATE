import { NextResponse } from "next/server";

/**
 * Rejects state-changing calls that do not come from SUNOVATE's own pages (AUD-18).
 *
 * Browsers send `Origin` on same-origin POST and DELETE requests, so a missing or foreign
 * origin means the call was not made by the app. JSON endpoints also require a JSON content
 * type, which a plain cross-site form cannot send. This complements the SameSite cookie.
 */
function hostname(value: string | null): string | null {
  if (!value) return null;
  try {
    return new URL(value.includes("://") ? value : `http://${value}`).hostname;
  } catch {
    return null;
  }
}

export function rejectCrossSite(request: Request, options: { json?: boolean } = {}): NextResponse | null {
  // Host names are compared without ports because the demo proxy forwards `Host: $host`.
  const originHost = hostname(request.headers.get("origin"));
  const hosts = [request.headers.get("host"), request.headers.get("x-forwarded-host")].map(hostname);
  if (!originHost || !hosts.includes(originHost)) {
    return NextResponse.json(
      { code: "CROSS_SITE_REQUEST", message: "Permintaan ditolak karena tidak berasal dari halaman SUNOVATE" },
      { status: 403 },
    );
  }
  if (options.json) {
    const contentType = (request.headers.get("content-type") ?? "").toLowerCase();
    if (!contentType.startsWith("application/json")) {
      return NextResponse.json(
        { code: "UNSUPPORTED_MEDIA_TYPE", message: "Jenis isi permintaan tidak didukung" },
        { status: 415 },
      );
    }
  }
  return null;
}
