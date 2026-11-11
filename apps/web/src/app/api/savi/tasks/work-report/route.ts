import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";
import { rejectCrossSite } from "@/lib/request-guard";

export async function POST(request: Request) {
  const blocked = rejectCrossSite(request);
  if (blocked) return blocked;
  try {
    return NextResponse.json(await apiRequest("/savi/tasks/work-report", { method: "POST" }), { status: 201 });
  } catch (error) {
    const status = error instanceof ApiRequestError ? error.status : 500;
    const body = error instanceof ApiRequestError ? error.body : null;
    return NextResponse.json(body ?? { code: "HTTP_ERROR", message: "Permintaan gagal" }, { status });
  }
}
