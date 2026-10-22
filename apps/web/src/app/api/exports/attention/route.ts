import { proxyDownload } from "@/lib/export-proxy";

/** Same-origin download of every urgent task and follow-up in the user's scope. */
export async function GET() {
  return proxyDownload("/exports/attention");
}
