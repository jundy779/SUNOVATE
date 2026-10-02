export default function Loading() {
  return (
    <div className="loading" role="status" aria-live="polite">
      <span className="loading-bar" aria-hidden="true" />
      <p>Memuat data yang boleh Anda akses...</p>
    </div>
  );
}
