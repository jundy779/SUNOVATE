import { rejectCrossSite } from "@/lib/request-guard";
import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";
import { isUuid } from "@/lib/secure-documents";

/** Revokes read access; the API closes any open viewer session for that reader. */
export async function DELETE(request: Request, { params }: { params: Promise<{ id: string; email: string }> }) {
  const blocked = rejectCrossSite(request);
  if (blocked) return blocked;
  const { id, email } = await params;
  if (!isUuid(id)) return NextResponse.json({ code: "NOT_FOUND", message: "Dokumen tidak ditemukan" }, { status: 404 });
  try {
    const result = await apiRequest(`/secure-documents/${id}/readers/${encodeURIComponent(decodeURIComponent(email))}`, {
      method: "DELETE",
    });
    return NextResponse.json(result, { headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(error.body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" }, { status: error.status });
    }
    return NextResponse.json({ code: "INTERNAL_ERROR", message: "Terjadi kesalahan" }, { status: 500 });
  }
}
