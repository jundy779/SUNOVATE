"use client";

import Link from "next/link";
import { useCallback, useSyncExternalStore } from "react";

const STORAGE_KEY = "sunovate.guide-welcome.dismissed.v1";
const listeners = new Set<() => void>();

function readDismissed(): boolean {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false; // storage unavailable: keep showing the note
  }
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** First-visit note on the dashboard pointing to the quick guide; hidden once dismissed. */
export function GuideWelcome() {
  // Server render and first client render treat the note as dismissed, so it never flashes.
  const dismissed = useSyncExternalStore(subscribe, readDismissed, () => true);
  const dismiss = useCallback(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // ignore: the note simply returns on the next visit
    }
    listeners.forEach((listener) => listener());
  }, []);

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
