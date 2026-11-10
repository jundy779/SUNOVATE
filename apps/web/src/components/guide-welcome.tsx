"use client";

import Link from "next/link";
import { useCallback, useEffect, useSyncExternalStore } from "react";
import { welcomeCookieName, welcomeStorageKey } from "@/lib/guide-welcome-keys";

const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function readLocal(userId: string): boolean {
  try {
    return window.localStorage.getItem(welcomeStorageKey(userId)) === "1";
  } catch {
    return false; // storage unavailable: rely on the cookie
  }
}

function remember(userId: string) {
  try {
    window.localStorage.setItem(welcomeStorageKey(userId), "1");
  } catch {
    // storage unavailable: the cookie below still records the choice
  }
  document.cookie = `${welcomeCookieName(userId)}=1; Path=/; Max-Age=${ONE_YEAR_SECONDS}; SameSite=Lax`;
}

/**
 * First-visit note on the dashboard pointing to the quick guide; hidden once dismissed.
 * The server passes whether this account already dismissed it, so nothing moves after the page
 * is shown (the earlier client-only check pushed the dashboard down after loading).
 */
export function GuideWelcome({ userId, initiallyDismissed }: { userId: string; initiallyDismissed: boolean }) {
  const read = useCallback(() => readLocal(userId), [userId]);
  // The browser copy covers accounts that dismissed the note before the cookie existed.
  const locallyDismissed = useSyncExternalStore(subscribe, read, () => false);
  const dismissed = initiallyDismissed || locallyDismissed;

  useEffect(() => {
    if (locallyDismissed && !initiallyDismissed) remember(userId); // record the cookie for next time
  }, [initiallyDismissed, locallyDismissed, userId]);

  const dismiss = useCallback(() => {
    remember(userId);
    listeners.forEach((listener) => listener());
  }, [userId]);

  if (dismissed) return null;
  return (
    <aside className="guide-welcome" aria-labelledby="guide-welcome-title">
      <div>
        <h2 id="guide-welcome-title">Baru menggunakan SUNOVATE?</h2>
        <p>Pelajari cara mencari dokumen, bertanya kepada SAVI AI, dan memperbarui pekerjaan dalam beberapa menit.</p>
      </div>
      <div className="guide-welcome-actions">
        <Link className="button" href="/panduan">Lihat panduan singkat</Link>
        <button className="text-button" type="button" onClick={dismiss}>Tutup</button>
      </div>
    </aside>
  );
}
