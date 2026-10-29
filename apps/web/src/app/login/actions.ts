"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { devLoginSchema, type Envelope } from "@sunovate/contracts";
import { apiRequest, ApiRequestError } from "@/lib/api";
import { SESSION_COOKIE } from "@/lib/session";

export interface LoginResult {
  ok: boolean;
  message?: string;
}

interface LoginData {
  accessToken: string;
  expiresAt: string;
}

export async function loginAction(input: unknown): Promise<LoginResult> {
  const parsed = devLoginSchema.safeParse(input);
  if (!parsed.success) {
    return { ok: false, message: parsed.error.issues[0]?.message ?? "Input tidak valid" };
  }
  let result: Envelope<LoginData>;
  try {
    result = await apiRequest<LoginData>("/auth/dev/login", {
      method: "POST",
      body: JSON.stringify(parsed.data),
    });
  } catch (error) {
    const message =
      error instanceof ApiRequestError
        ? (error.body?.message ?? "Login gagal")
        : "Login gagal";
    return { ok: false, message };
  }
  const store = await cookies();
  store.set(SESSION_COOKIE, result.data.accessToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    expires: new Date(result.data.expiresAt),
  });
  return { ok: true };
}

export async function logoutAction(): Promise<void> {
  // Revoke the token on the server first, so a copy of it stops working too (AUD-05).
  // apiRequest attaches the session token from the cookie; failures must not block logout.
  try {
    await apiRequest<{ loggedOut: boolean }>("/auth/logout", { method: "POST" });
  } catch {
    // Expired or already revoked sessions still end locally below.
  }
  const store = await cookies();
  store.delete(SESSION_COOKIE);
  redirect("/login");
}
