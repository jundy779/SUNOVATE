import { notFound, redirect } from "next/navigation";
import type { ApiErrorBody, Envelope } from "@sunovate/contracts";
import { apiBaseUrl, getSessionToken } from "./session";

/** Server-side API client. Authorization is enforced by the API; the UI only reacts. */
export class ApiRequestError extends Error {
  constructor(
    readonly status: number,
    readonly body: ApiErrorBody | null,
  ) {
    super(body?.message ?? `API request failed with status ${status}`);
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<Envelope<T>> {
  const token = await getSessionToken();
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/v1${path}`, { ...init, headers, cache: "no-store" });
  } catch {
    throw new ApiRequestError(503, {
      code: "API_UNREACHABLE",
      message: "API SUNOVATE tidak dapat dihubungi",
      details: null,
      requestId: "-",
    });
  }
  if (response.ok) return (await response.json()) as Envelope<T>;
  const body = (await response.json().catch(() => null)) as ApiErrorBody | null;
  throw new ApiRequestError(response.status, body);
}

/** For server components: map auth errors to navigation, rethrow everything else. */
export async function apiGet<T>(path: string): Promise<Envelope<T>> {
  try {
    return await apiRequest<T>(path);
  } catch (error) {
    if (error instanceof ApiRequestError) {
      if (error.status === 401) redirect("/login");
      if (error.status === 403) redirect("/unauthorized");
      if (error.status === 404 || error.status === 422) notFound();
    }
    throw error;
  }
}
