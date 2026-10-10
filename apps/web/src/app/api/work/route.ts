import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";

const ALLOWED_PATH = /^\/(work-outputs|tasks|milestones|pending-matters|follow-ups)(\/[0-9a-f-]{36})?(\?revision=\d+)?$/;

async function mutate(request: Request) {
  const payload = (await request.json()) as {
    path?: string;
    method?: "POST" | "PATCH" | "DELETE";
    body?: unknown;
  };
  if (!payload.path || !payload.method || !ALLOWED_PATH.test(payload.path)) {
    return NextResponse.json({ message: "Permintaan monitoring tidak valid" }, { status: 400 });
  }
  try {
    const result = await apiRequest(payload.path, {
      method: payload.method,
      body: payload.method === "DELETE" ? undefined : JSON.stringify(payload.body ?? {}),
    });
    return NextResponse.json(result, { status: payload.method === "POST" ? 201 : 200 });
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(
        error.body ?? { message: error.message },
        { status: error.status },
      );
    }
    return NextResponse.json({ message: "Terjadi kesalahan saat menyimpan data" }, { status: 500 });
  }
}

export const POST = mutate;
