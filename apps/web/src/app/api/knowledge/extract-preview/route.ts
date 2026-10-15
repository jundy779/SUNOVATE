import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";

export async function POST(request: Request) {
  const form = await request.formData().catch(() => null);
  if (!form) return NextResponse.json({ message: "Berkas simulasi tidak valid" }, { status: 422 });
  try {
    const result = await apiRequest("/knowledge/extract-preview", { method: "POST", body: form });
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(error.body ?? { message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Berkas belum dapat dibaca" }, { status: 500 });
  }
}
