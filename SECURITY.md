# Security Policy

## Reporting
Jangan membuka issue publik untuk dugaan kerentanan atau data sensitif yang terekspos. Laporkan secara
privat kepada pemilik repository dengan dampak, langkah reproduksi, dan versi terdampak. Kontak keamanan
resmi instansi belum ditetapkan (OPEN QUESTION). Prosedur insiden: `docs/06-security/incident-response.md`.

## Baseline
- Jangan commit kredensial, dokumen internal, atau data operasional asli. Data pengembangan berlabel `SIMULATED_DATA`.
- Otorisasi ditegakkan di API: permission, team scope, dan klasifikasi data; deny by default. Record yang tidak boleh dibaca dikembalikan sebagai 404.
- Login pengembangan (token HMAC) hanya untuk development; API menolak start bila `APP_ENV=production` dengan `DEV_AUTH_ENABLED=true` atau `DATA_BACKEND=simulated`.
- Token disimpan di cookie httpOnly SameSite=Lax; browser tidak membaca token.
- Hermes hanya mengakses data melalui `HermesGateway`; tidak ada kredensial database untuk Hermes. Aksi tulis memerlukan persetujuan manusia.
- `audit_logs` append-only (trigger PostgreSQL menolak UPDATE/DELETE).
- Integrasi produksi tetap nonaktif sampai disetujui.

Scaffold ini belum melalui security review, penetration test, atau audit aksesibilitas formal.
