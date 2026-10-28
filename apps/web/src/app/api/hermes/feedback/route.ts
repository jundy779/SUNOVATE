import { rejectCrossSite } from "@/lib/request-guard";
import { NextResponse } from "next/server";
import { hermesFeedbackSchema } from "@sunovate/contracts";
import { apiRequest, ApiRequestError } from "@/lib/api";

export async function POST(request: Request) {
  const blocked = rejectCrossSite(request, { json: true });
  if (blocked) return blocked;
  const parsed = hermesFeedbackSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ code: "VALIDATION_ERROR", message: "Input tidak valid" }, { status: 422 });
  }
  try {
    const result = await apiRequest(`/hermes/messages/${parsed.data.messageId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ rating: parsed.data.rating }),
    });
    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    const status = error instanceof ApiRequestError ? error.status : 500;
    const body = error instanceof ApiRequestError ? error.body : null;
    return NextResponse.json(body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" }, { status });
  }
}
