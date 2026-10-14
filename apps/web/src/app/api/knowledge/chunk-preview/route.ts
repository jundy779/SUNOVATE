import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => null);
  if (!payload || typeof payload !== "object") {
    return NextResponse.json({ message: "Bahan pemeriksaan tidak valid" }, { status: 422 });
  }
  try {
    const result = await apiRequest("/knowledge/chunk-preview", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(error.body ?? { message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Pemeriksaan belum dapat dilakukan" }, { status: 500 });
  }
}
