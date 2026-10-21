"use client";

import { useCallback, useEffect, useState } from "react";
import { UiIcon } from "@/components/ui-icons";
import { isBlockedShortcut } from "@/lib/secure-documents";

type Stage = "notice" | "opening" | "reading";

interface Props {
  documentId: string;
  pageCount: number;
  title: string;
}

/**
 * Reader for RAHASIA documents. The server sends watermarked images only; the measures here
 * (no context menu, no drag, blur when the window loses focus, blocked shortcuts) are deterrents,
 * not the security boundary.
 */
export function SecureViewer({ documentId, pageCount, title }: Props) {
  const [stage, setStage] = useState<Stage>("notice");
  const [agreed, setAgreed] = useState(false);
  const [page, setPage] = useState(1);
  const [hidden, setHidden] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  const accept = useCallback(async () => {
    setStage("opening");
    setMessage(null);
    const response = await fetch(`/api/secure-documents/${documentId}/acknowledgements`, { method: "POST" });
    if (response.ok) {
      setNonce((value) => value + 1);
      setStage("reading");
      return;
    }
    setStage("notice");
    setMessage("Pernyataan belum tercatat. Coba lagi atau hubungi pengelola pengetahuan.");
  }, [documentId]);

  useEffect(() => {
    if (stage !== "reading") return;
    const conceal = () => setHidden(true);
    const onVisibility = () => setHidden(document.visibilityState !== "visible");
    const onKey = (event: KeyboardEvent) => {
      if (!isBlockedShortcut(event)) return;
      event.preventDefault();
      setMessage("Dokumen ini hanya dapat dibaca. Menyimpan, mencetak, atau menyalin tidak diizinkan.");
    };
    window.addEventListener("blur", conceal);
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("blur", conceal);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("keydown", onKey);
    };
  }, [stage]);

  const onImageError = useCallback(() => {
    setStage("notice");
    setAgreed(false);
    setMessage("Halaman tidak dapat ditampilkan. Persetujuan mungkin sudah berakhir atau terlalu banyak halaman dibuka dalam waktu singkat.");
  }, []);

  if (stage !== "reading") {
    return (
      <section className="sv-notice" aria-labelledby="notice-title">
        <header className="ed-head">
          <h2 id="notice-title">Pernyataan kerahasiaan</h2>
          <p>Wajib disetujui setiap kali dokumen dibuka</p>
        </header>
        <ul>
          <li>Dokumen ini bersifat rahasia dan hanya boleh dibaca oleh pegawai yang diberi akses.</li>
          <li>Mengunduh, menyalin, mencetak, memotret, merekam layar, atau menyebarkan isi dokumen tidak diizinkan.</li>
          <li>Setiap halaman memuat tanda air nama, email, dan waktu akses Anda, dan setiap pembukaan halaman tercatat.</li>
          <li>Pelanggaran dapat dikenai sanksi disiplin dan sanksi hukum sesuai peraturan perundang-undangan.</li>
        </ul>
        <label className="sv-agree">
          <input type="checkbox" checked={agreed} onChange={(event) => setAgreed(event.target.checked)} />
          <span>Saya memahami dan menyetujui pernyataan di atas.</span>
        </label>
        {message ? <p className="field-error" role="alert">{message}</p> : null}
        <button className="button" type="button" disabled={!agreed || stage === "opening"} onClick={accept}>
          {stage === "opening" ? "Mencatat persetujuan..." : "Buka dokumen"}
        </button>
      </section>
    );
  }

  return (
    <section className="sv-reader" aria-label={`Pembaca dokumen ${title}`}>
      <div className="sv-toolbar">
        <button className="button secondary" type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
          Halaman sebelumnya
        </button>
        <span aria-live="polite">Halaman {page} dari {pageCount}</span>
        <button className="button secondary" type="button" disabled={page >= pageCount} onClick={() => setPage((value) => value + 1)}>
          Halaman berikutnya
        </button>
      </div>
      {message ? <p className="sv-message" role="status"><UiIcon name="shield" />{message}</p> : null}
      <div
        className={hidden ? "sv-page sv-page-hidden" : "sv-page"}
        onContextMenu={(event) => event.preventDefault()}
        onClick={() => setHidden(false)}
      >
        {/* eslint-disable-next-line @next/next/no-img-element -- per-request, uncached image that next/image must not optimise or cache */}
        <img
          alt={`Halaman ${page} dari ${pageCount}. Isi hanya dapat dibaca di layar.`}
          draggable={false}
          key={`${page}-${nonce}`}
          onError={onImageError}
          src={`/api/secure-documents/${documentId}/pages/${page}?v=${nonce}`}
        />
        {hidden ? (
          <p className="sv-cover">Tampilan disembunyikan karena jendela tidak aktif. Klik untuk melanjutkan membaca.</p>
        ) : null}
      </div>
    </section>
  );
}
