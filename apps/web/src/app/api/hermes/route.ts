import { rejectCrossSite } from "@/lib/request-guard";
import { NextResponse } from "next/server";
import { hermesQuerySchema, type HermesAnswer } from "@sunovate/contracts";
import { apiRequest, ApiRequestError } from "@/lib/api";

/** Server-side proxy: the browser never sees the token; the API enforces authorization. */
export async function POST(request: Request) {
  const blocked = rejectCrossSite(request, { json: true });
  if (blocked) return blocked;
  const parsed = hermesQuerySchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json(
      { code: "VALIDATION_ERROR", message: parsed.error.issues[0]?.message ?? "Input tidak valid" },
      { status: 422 },
    );
  }
  try {
    const result = await apiRequest<HermesAnswer>("/hermes/query", {
      method: "POST",
      body: JSON.stringify(parsed.data),
    });
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(
        error.body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" },
        { status: error.status },
      );
    }
    return NextResponse.json({ code: "INTERNAL_ERROR", message: "Terjadi kesalahan" }, { status: 500 });
  }
}
