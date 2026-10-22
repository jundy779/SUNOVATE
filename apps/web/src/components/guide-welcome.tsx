"use client";

import Link from "next/link";
import { useCallback, useSyncExternalStore } from "react";

const STORAGE_PREFIX = "sunovate.guide-welcome.dismissed.v1:";
const listeners = new Set<() => void>();

/** Per account, so a shared office computer still greets each new user (BUG-037). */
export function welcomeStorageKey(userId: string): string {
  return `${STORAGE_PREFIX}${userId}`;
}

function readDismissed(key: string): boolean {
  try {
    return window.localStorage.getItem(key) === "1";
  } catch {
    return false; // storage unavailable: keep showing the note
  }
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** First-visit note on the dashboard pointing to the quick guide; hidden once dismissed. */
export function GuideWelcome({ userId }: { userId: string }) {
  const key = welcomeStorageKey(userId);
  const read = useCallback(() => readDismissed(key), [key]);
  // Server render and first client render treat the note as dismissed, so it never flashes.
  const dismissed = useSyncExternalStore(subscribe, read, () => true);
  const dismiss = useCallback(() => {
    try {
      window.localStorage.setItem(key, "1");
    } catch {
      // ignore: the note simply returns on the next visit
    }
    listeners.forEach((listener) => listener());
  }, [key]);

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
