import { NextResponse } from "next/server";
import { apiRequest, ApiRequestError } from "@/lib/api";

const KNOWLEDGE_PATH = /^\/knowledge\/[0-9a-f-]{36}(\/submit)?$/;
const DECISION_PATH = /^\/approvals\/[0-9a-f-]{36}\/decision$/;

export async function POST(request: Request) {
  const payload = (await request.json()) as {
    path?: string;
    method?: "POST" | "PATCH";
    body?: unknown;
  };
  const validKnowledgeUpdate = payload.method === "PATCH" && payload.path && KNOWLEDGE_PATH.test(payload.path) && !payload.path.endsWith("/submit");
  const validKnowledgeSubmit = payload.method === "POST" && payload.path && KNOWLEDGE_PATH.test(payload.path) && payload.path.endsWith("/submit");
  const validDecision = payload.method === "POST" && payload.path && DECISION_PATH.test(payload.path);
  if (!validKnowledgeUpdate && !validKnowledgeSubmit && !validDecision) {
    return NextResponse.json({ message: "Permintaan pengetahuan tidak valid" }, { status: 400 });
  }
  const path = payload.path as string;
  const method = payload.method as "POST" | "PATCH";
  try {
    const result = await apiRequest(path, {
      method,
      body: JSON.stringify(payload.body ?? {}),
    });
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof ApiRequestError) {
      return NextResponse.json(error.body ?? { message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Perubahan tidak dapat disimpan" }, { status: 500 });
  }
}
