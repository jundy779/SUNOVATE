"use client";

import { useState } from "react";

interface Props {
  documentId: string;
  initialReaders: string[];
}

export function ReaderManager({ documentId, initialReaders }: Props) {
  const [readers, setReaders] = useState(initialReaders);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ tone: "ok" | "error"; text: string } | null>(null);

  async function grant(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = email.trim().toLowerCase();
    if (!value) return;
    setBusy(true);
    setMessage(null);
    const response = await fetch(`/api/secure-documents/${documentId}/readers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: value }),
    });
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    setBusy(false);
    if (!response.ok) {
      setMessage({ tone: "error", text: body?.message ?? "Akses belum dapat diberikan." });
      return;
    }
    setReaders((current) => (current.includes(value) ? current : [...current, value].sort()));
    setEmail("");
    setMessage({ tone: "ok", text: `Akses baca diberikan kepada ${value}.` });
  }

  async function revoke(reader: string) {
    setBusy(true);
    setMessage(null);
    const response = await fetch(`/api/secure-documents/${documentId}/readers/${encodeURIComponent(reader)}`, {
      method: "DELETE",
    });
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    setBusy(false);
    if (!response.ok) {
      setMessage({ tone: "error", text: body?.message ?? "Akses belum dapat dicabut." });
      return;
    }
    setReaders((current) => current.filter((item) => item !== reader));
    setMessage({ tone: "ok", text: `Akses baca ${reader} dicabut. Penampil yang sedang terbuka langsung tertutup.` });
  }

  return (
    <div className="sv-readers">
      {readers.length ? (
        <ul>
          {readers.map((reader) => (
            <li key={reader}>
              <span>{reader}</span>
              <button className="text-button" type="button" disabled={busy} onClick={() => revoke(reader)}>
                Cabut akses
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="sv-readers-empty">Belum ada pembaca yang diberi akses.</p>
      )}
      <form className="sv-grant" onSubmit={grant}>
        <label htmlFor={`grant-${documentId}`}>Email pegawai</label>
        <div>
          <input
            id={`grant-${documentId}`}
            type="email"
            autoComplete="off"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="nama@sunovate.local"
          />
          <button className="button" type="submit" disabled={busy || !email.trim()}>
            Beri akses baca
          </button>
        </div>
      </form>
      {message ? (
        <p className={message.tone === "ok" ? "sv-feedback" : "field-error"} role={message.tone === "ok" ? "status" : "alert"}>
          {message.text}
        </p>
      ) : null}
    </div>
  );
}
