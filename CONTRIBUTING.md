# Contributing

1. Baca `AGENTS.md`, `docs/README.md`, dan `docs/13-handover/developer-handover.md`.
2. Siapkan lingkungan: `pnpm install`, `pnpm api:setup`. Salin `.env.example` ke `.env` bila perlu; jangan commit secret.
3. Data contoh wajib fiktif dan berlabel `SIMULATED_DATA`. Tambahkan lewat `apps/api/sunovate_api/store/dataset.py`.
4. Endpoint baru wajib: dependency `require(...)` untuk permission, pemeriksaan team scope dan klasifikasi, test negatif (401/403/404), dan entri di `docs/07-api/endpoint-catalog.md` serta `docs/06-security/permission-matrix.md`.
5. Perubahan skema wajib revisi Alembic baru dan dicek dengan `pnpm db:sql` atau `pnpm db:check`.
6. Perubahan arsitektur dicatat di `docs/12-governance/decision-log.md`. Informasi bisnis baru diberi label CONFIRMED (dengan sumber), PROPOSED, OPEN QUESTION, atau OUT OF SCOPE.
7. Sebelum pull request: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`.

Pull request menjelaskan scope, hasil validasi aktual, risiko, dan open question terkait.
Commit mengikuti format `type(scope): ringkasan` (misalnya `feat(knowledge): ...`, `fix(authz): ...`).
