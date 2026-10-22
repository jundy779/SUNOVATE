import { NextResponse } from "next/server";
import { proxyDownload } from "@/lib/export-proxy";
import { EXPORT_KINDS } from "@/lib/work-table";

/** Same-origin download of a work-monitoring sheet; the API filters rows by the user's access. */
export async function GET(request: Request) {
  const kind = new URL(request.url).searchParams.get("kind") ?? "";
  if (!(EXPORT_KINDS as readonly string[]).includes(kind)) {
    return NextResponse.json({ code: "VALIDATION_ERROR", message: "Jenis data tidak dikenal" }, { status: 422 });
  }
  return proxyDownload(`/exports/work?kind=${encodeURIComponent(kind)}`);
}
