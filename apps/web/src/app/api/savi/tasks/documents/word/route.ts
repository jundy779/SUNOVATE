import { NextResponse } from "next/server";
import { z } from "zod";
import { rejectCrossSite } from "@/lib/request-guard";
import { apiBaseUrl, getSessionToken } from "@/lib/session";

const exportSchema = z.object({
  draftId: z.string().uuid(),
  kind: z.literal("WORK_REPORT"),
  text: z.string().min(1).max(20_000),
});

/** Word file of an employee-approved SAVI draft; the API builds it and stores nothing. */
export async function POST(request: Request) {
  const blocked = rejectCrossSite(request, { json: true });
  if (blocked) return blocked;
  const parsed = exportSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ code: "VALIDATION_ERROR", message: "Input tidak valid" }, { status: 422 });
  }
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ code: "UNAUTHENTICATED", message: "Silakan masuk kembali" }, { status: 401 });

  let upstream: Response;
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1/savi/tasks/documents/word`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(parsed.data),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ code: "API_UNREACHABLE", message: "Layanan sedang tidak dapat dihubungi" }, { status: 503 });
  }
  if (!upstream.ok) {
    const body = await upstream.json().catch(() => ({ code: "HTTP_ERROR", message: "Berkas Word tidak dapat dibuat" }));
    return NextResponse.json(body, { status: upstream.status, headers: { "Cache-Control": "no-store" } });
  }
  return new Response(await upstream.arrayBuffer(), {
    status: 200,
    headers: {
      "Content-Type": upstream.headers.get("content-type") ?? "application/octet-stream",
      "Content-Disposition": upstream.headers.get("content-disposition") ?? 'attachment; filename="SUNOVATE-draf.docx"',
      "Cache-Control": "no-store, private, max-age=0",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
