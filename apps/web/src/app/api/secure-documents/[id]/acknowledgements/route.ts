import { rejectCrossSite } from "@/lib/request-guard";
import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";
import { isUuid } from "@/lib/secure-documents";

/** Records the reader's acceptance of the confidentiality notice; the API audits it. */
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const blocked = rejectCrossSite(request);
  if (blocked) return blocked;
  const { id } = await params;
  if (!isUuid(id)) return NextResponse.json({ code: "NOT_FOUND", message: "Dokumen tidak ditemukan" }, { status: 404 });
  try {
    const result = await apiRequest<{ accepted: boolean; validMinutes: number }>(
      `/secure-documents/${id}/acknowledgements`,
      { method: "POST" },
    );
    return NextResponse.json(result, { status: 201, headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(error.body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" }, { status: error.status });
    }
    return NextResponse.json({ code: "INTERNAL_ERROR", message: "Terjadi kesalahan" }, { status: 500 });
  }
}
