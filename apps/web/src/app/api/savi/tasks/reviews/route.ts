import { NextResponse } from "next/server";
import { z } from "zod";
import { apiRequest, ApiRequestError } from "@/lib/api";
import { rejectCrossSite } from "@/lib/request-guard";

const reviewSchema = z.object({
  draftId: z.string().uuid(),
  kind: z.literal("WORK_REPORT"),
  decision: z.enum(["ACCEPTED", "REJECTED"]),
  edited: z.boolean(),
});

export async function POST(request: Request) {
  const blocked = rejectCrossSite(request, { json: true });
  if (blocked) return blocked;
  const parsed = reviewSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ code: "VALIDATION_ERROR", message: "Input tidak valid" }, { status: 422 });
  }
  try {
    const result = await apiRequest("/savi/tasks/reviews", { method: "POST", body: JSON.stringify(parsed.data) });
    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    const status = error instanceof ApiRequestError ? error.status : 500;
    const body = error instanceof ApiRequestError ? error.body : null;
    return NextResponse.json(body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" }, { status });
  }
}
