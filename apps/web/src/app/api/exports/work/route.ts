import { NextResponse } from "next/server";
import { apiBaseUrl, getSessionToken } from "@/lib/session";
import { EXPORT_KINDS } from "@/lib/work-table";

/** Same-origin download of a work-monitoring sheet; the API filters rows by the user's access. */
export async function GET(request: Request) {
  const kind = new URL(request.url).searchParams.get("kind") ?? "";
  if (!(EXPORT_KINDS as readonly string[]).includes(kind)) {
    return NextResponse.json({ code: "VALIDATION_ERROR", message: "Jenis data tidak dikenal" }, { status: 422 });
  }
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ code: "UNAUTHENTICATED", message: "Silakan masuk kembali" }, { status: 401 });

  let upstream: Response;
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1/exports/work?kind=${encodeURIComponent(kind)}`, {
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
