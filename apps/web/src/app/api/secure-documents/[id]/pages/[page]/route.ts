import { NextResponse } from "next/server";
import { apiBaseUrl, getSessionToken } from "@/lib/session";
import { isUuid, SECURE_PAGE_HEADERS } from "@/lib/secure-documents";

/**
 * Same-origin proxy for one watermarked page image. The session token stays on the server; the
 * browser only receives the PNG, never the document text, and nothing may be cached.
 */
export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string; page: string }> },
) {
  const { id, page } = await params;
  const pageNumber = Number(page);
  if (!isUuid(id) || !Number.isInteger(pageNumber) || pageNumber < 1 || pageNumber > 500) {
    return NextResponse.json({ code: "NOT_FOUND", message: "Halaman tidak ditemukan" }, { status: 404 });
  }
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ code: "UNAUTHENTICATED", message: "Silakan masuk kembali" }, { status: 401 });

  let upstream: Response;
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1/secure-documents/${id}/pages/${pageNumber}`, {
      headers: { Authorization: `Bearer ${token}`, Accept: "image/png" },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ code: "API_UNREACHABLE", message: "Layanan sedang tidak dapat dihubungi" }, { status: 503 });
  }
  if (!upstream.ok || upstream.headers.get("content-type") !== "image/png") {
    const body = await upstream.json().catch(() => ({ code: "HTTP_ERROR", message: "Halaman tidak dapat dibuka" }));
    const headers: Record<string, string> = { "Cache-Control": "no-store" };
    const retryAfter = upstream.headers.get("retry-after");
    if (retryAfter) headers["Retry-After"] = retryAfter;
    return NextResponse.json(body, { status: upstream.ok ? 502 : upstream.status, headers });
  }
  return new Response(await upstream.arrayBuffer(), { status: 200, headers: SECURE_PAGE_HEADERS });
}
