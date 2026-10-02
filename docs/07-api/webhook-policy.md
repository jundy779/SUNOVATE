# Webhook Policy

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Kebijakan untuk webhook masuk di masa depan (Telegram, WhatsApp, document provider). **Tidak ada webhook yang diimplementasikan.**

## Confirmed Information
- **CONFIRMED** Telegram dan WhatsApp adalah fondasi fase lanjutan; penggunaannya belum diizinkan (sumber: brief sesi 2026-10-01; OQ-08).

## Aturan wajib sebelum webhook diaktifkan
1. **Verifikasi tanda tangan** sesuai mekanisme penyedia (HMAC atau token rahasia), dibandingkan dengan waktu konstan. Secret di secret store, bukan di repository.
2. **Proteksi replay**: tolak request dengan timestamp di luar jendela waktu kecil; simpan ID event yang sudah diproses.
3. **Idempotensi**: proses ulang event yang sama tidak menimbulkan efek ganda.
4. **Allowlist** sumber bila penyedia mendukung; endpoint terpisah per penyedia di bawah `/api/v1/webhooks/<provider>`.
5. **Payload minimal**: simpan hanya yang diperlukan; jangan log isi pesan pengguna atau dokumen.
6. **Otorisasi tetap berlaku**: identitas kanal harus terhubung ke pengguna SUNOVATE; setiap pertanyaan melalui `HermesGateway` dengan permission pengguna tersebut.
7. **Tanpa aksi tulis langsung**: perintah tulis dari kanal menjadi approval request.
8. **Rate limiting** per sumber dan per pengguna.
9. **Audit** setiap event yang diterima, ditolak, atau gagal.
10. **Respons cepat**: balas 2xx setelah validasi dan antrekan pemrosesan bila lama (antrean memerlukan keputusan arsitektur baru; message broker saat ini tidak dipakai).

## Risks
Spoofing webhook, kebocoran data RESTRICTED ke kanal eksternal (R-02), dan penyalahgunaan bot.

## Related Documents
- [telegram-proposal.md](../08-integrations/telegram-proposal.md)
- [whatsapp-proposal.md](../08-integrations/whatsapp-proposal.md)
- [integration-readiness-checklist.md](../08-integrations/integration-readiness-checklist.md)
