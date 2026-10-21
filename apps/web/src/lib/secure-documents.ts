const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function isUuid(value: string): boolean {
  return UUID_PATTERN.test(value);
}

/** Response headers for page images: never cached, never offered as a download. */
export const SECURE_PAGE_HEADERS: Record<string, string> = {
  "Content-Type": "image/png",
  "Cache-Control": "no-store, private, max-age=0",
  Pragma: "no-cache",
  "Content-Disposition": "inline",
  "X-Content-Type-Options": "nosniff",
  "Cross-Origin-Resource-Policy": "same-origin",
  "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; sandbox",
};

/** Keyboard shortcuts that would save, print, copy, or open developer tools. */
export function isBlockedShortcut(event: Pick<KeyboardEvent, "key" | "ctrlKey" | "metaKey" | "shiftKey">): boolean {
  const key = event.key.toLowerCase();
  if (key === "printscreen" || key === "f12") return true;
  const modifier = event.ctrlKey || event.metaKey;
  if (!modifier) return false;
  if (["s", "p", "c", "u", "a"].includes(key)) return true;
  return event.shiftKey && ["i", "j", "c", "s"].includes(key);
}
