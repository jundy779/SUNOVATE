/** Names shared by the server (dashboard page) and the browser (welcome note). */

const STORAGE_PREFIX = "sunovate.guide-welcome.dismissed.v1:";
const COOKIE_PREFIX = "sunovate_guide_dismissed_";

/** Per account, so a shared office computer still greets each new user (BUG-037). */
export function welcomeStorageKey(userId: string): string {
  return `${STORAGE_PREFIX}${userId}`;
}

/** Cookie read by the server so the dashboard is laid out correctly on the first paint. */
export function welcomeCookieName(userId: string): string {
  return `${COOKIE_PREFIX}${userId.replace(/[^A-Za-z0-9-]/g, "")}`;
}
