import { rejectCrossSite } from "@/lib/request-guard";
import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";

export async function POST(request: Request) {
  const blocked = rejectCrossSite(request, { json: true });
  if (blocked) return blocked;
  const payload = await request.json().catch(() => null);
  if (!payload || typeof payload !== "object") return NextResponse.json({ message: "Bahan draf tidak valid" }, { status: 422 });
  try {
    const result = await apiRequest("/knowledge/chunk-drafts", { method: "POST", body: JSON.stringify(payload) });
    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    if (error instanceof ApiRequestError) return NextResponse.json(error.body ?? { message: error.message }, { status: error.status });
    return NextResponse.json({ message: "Draf belum dapat disimpan" }, { status: 500 });
  }
}
