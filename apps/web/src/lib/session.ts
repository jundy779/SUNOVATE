import { cookies } from "next/headers";

/** httpOnly cookie that holds the development token. The browser never reads it. */
export const SESSION_COOKIE = "sunovate_dev_token";

export async function getSessionToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(SESSION_COOKIE)?.value ?? null;
}

export function apiBaseUrl(): string {
  return (process.env.SUNOVATE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
}
