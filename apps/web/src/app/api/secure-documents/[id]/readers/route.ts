import { rejectCrossSite } from "@/lib/request-guard";
import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";
import { isUuid } from "@/lib/secure-documents";

/** Grants read access to a RAHASIA document; the API enforces who may do this and audits it. */
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const blocked = rejectCrossSite(request, { json: true });
  if (blocked) return blocked;
  const { id } = await params;
  if (!isUuid(id)) return NextResponse.json({ code: "NOT_FOUND", message: "Dokumen tidak ditemukan" }, { status: 404 });
  const body = (await request.json().catch(() => null)) as { email?: unknown } | null;
  const email = typeof body?.email === "string" ? body.email.trim() : "";
  if (!email) return NextResponse.json({ code: "VALIDATION_ERROR", message: "Isi email pengguna" }, { status: 422 });
  try {
    const result = await apiRequest(`/secure-documents/${id}/readers`, { method: "POST", body: JSON.stringify({ email }) });
    return NextResponse.json(result, { status: 201, headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(error.body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" }, { status: error.status });
    }
    return NextResponse.json({ code: "INTERNAL_ERROR", message: "Terjadi kesalahan" }, { status: 500 });
  }
}
