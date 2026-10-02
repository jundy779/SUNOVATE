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
        API mungkin belum berjalan atau sedang bermasalah. Detail teknis tidak ditampilkan kepada
        pengguna.
      </p>
      <button className="button" onClick={reset} type="button">
        Coba lagi
      </button>
    </section>
  );
}
