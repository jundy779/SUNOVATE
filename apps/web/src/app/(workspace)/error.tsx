"use client";

export default function WorkspaceError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <section className="empty-state" role="alert">
      <p className="eyebrow">Gangguan tampilan</p>
      <h1>Data belum dapat ditampilkan</h1>
      <p>
        Layanan SUNOVATE sedang tidak tersedia. Silakan coba kembali beberapa saat lagi atau
        hubungi pengelola sistem.
      </p>
      <button className="button" onClick={reset} type="button">
        Coba lagi
      </button>
    </section>
  );
}
