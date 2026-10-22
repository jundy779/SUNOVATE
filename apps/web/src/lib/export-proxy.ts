import { NextResponse } from "next/server";
import { apiBaseUrl, getSessionToken } from "@/lib/session";

/**
 * Streams an Excel download from the API to the browser. The session token stays on the server
 * and the API decides which rows the user may receive.
 */
export async function proxyDownload(apiPath: string): Promise<Response> {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ code: "UNAUTHENTICATED", message: "Silakan masuk kembali" }, { status: 401 });

  let upstream: Response;
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1${apiPath}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ code: "API_UNREACHABLE", message: "Layanan sedang tidak dapat dihubungi" }, { status: 503 });
  }
  if (!upstream.ok) {
    const body = await upstream.json().catch(() => ({ code: "HTTP_ERROR", message: "Unduhan tidak dapat dibuat" }));
    return NextResponse.json(body, { status: upstream.status, headers: { "Cache-Control": "no-store" } });
  }
  return new Response(await upstream.arrayBuffer(), {
    status: 200,
    headers: {
      "Content-Type": upstream.headers.get("content-type") ?? "application/octet-stream",
      "Content-Disposition": upstream.headers.get("content-disposition") ?? 'attachment; filename="SUNOVATE.xlsx"',
      "Cache-Control": "no-store, private, max-age=0",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
