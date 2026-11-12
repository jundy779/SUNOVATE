# Konfigurasi Aman Hermes Agent untuk SAVI

**Status:** PROPOSED (siap dipakai saat model lokal ditetapkan)
**Owner:** Tim pengembang SUNOVATE
**Last Updated:** 2026-11-12

## Purpose

SAVI (SUN AI Virtual Intelligence) memakai Hermes Agent dari Nous Research sebagai runtime AI di belakang `HermesGateway` (ADR-004). Dokumen ini menjelaskan cara menjalankan Hermes Agent agar sesuai batas SUNOVATE. Bawaan Hermes Agent terlalu luas: menurut dokumentasinya sendiri, API server menjalankan agen dengan seluruh alatnya, termasuk perintah terminal, operasi berkas, pencarian web, memori, dan skill.

## Prinsip

- **CONFIRMED** (ADR-004): Hermes hanya menerima pertanyaan dan potongan sumber yang sudah diotorisasi `HermesGateway` untuk penanya. Hermes tidak menerima kredensial database, identitas pengguna, atau teks yang tidak boleh dibaca penanya.
- **CONFIRMED** (DEC-20261110-01): model dijalankan di server kantor. Layanan model eksternal hanya boleh dipakai dengan persetujuan tertulis dan batas biaya.
- **IMPLEMENTED**: SUNOVATE menolak `HERMES_AGENT_BASE_URL` di luar loopback atau jaringan privat, mewajibkan `HERMES_AGENT_API_KEY` minimal 16 karakter, tidak pernah mengirim definisi alat, dan memeriksa setiap penanda sitasi `[n]` terhadap potongan yang diotorisasi. Jawaban tanpa sitasi yang sah tidak ditampilkan.
- **OPERATIONAL CONTROL**: model yang dipakai Hermes Agent dikonfigurasi di Hermes, bukan di SUNOVATE. SUNOVATE tidak dapat memeriksa bahwa model itu lokal, sehingga konfigurasi di bawah wajib diterapkan dan diperiksa oleh pengelola server.

## Konfigurasi Hermes Agent

`~/.hermes/config.yaml` pada server yang menjalankan Hermes Agent:

```yaml
model:
  provider: custom
  base_url: http://127.0.0.1:11434/v1   # model lokal (contoh: Ollama); bukan layanan cloud
  default: <nama-model-lokal>           # ditetapkan setelah spesifikasi server diketahui

agent:
  # Semua alat dimatikan: SAVI hanya menyusun jawaban dari potongan yang dikirim SUNOVATE.
  disabled_toolsets:
    - terminal
    - file
    - code_execution
    - web
    - search
    - browser
    - vision
    - image_gen
    - tts
    - skills
    - memory
    - session_search
    - cronjob
    - delegation
    - messaging
    - todo
    - clarify
    - debugging

memory:
  memory_enabled: false        # tidak ada data kantor yang disimpan di luar audit SUNOVATE
  user_profile_enabled: false
  write_approval: true

skills:
  write_approval: true         # agen tidak boleh membuat atau mengubah skill sendiri
  guard_agent_created: true
```

`~/.hermes/.env`:

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=<acak, minimal 32 karakter; sama dengan HERMES_AGENT_API_KEY di SUNOVATE>
# Jangan set API_SERVER_CORS_ORIGINS: hanya SUNOVATE (server-ke-server) yang memanggil Hermes.
```

API server Hermes Agent mendengarkan di `127.0.0.1:8642` secara bawaan. Jangan membukanya ke jaringan lain.

## Konfigurasi SUNOVATE

```bash
HERMES_MODE=hermes_agent
HERMES_AGENT_BASE_URL=http://127.0.0.1:8642/v1
HERMES_AGENT_API_KEY=<sama dengan API_SERVER_KEY>
HERMES_AGENT_MODEL=hermes-agent
HERMES_AGENT_TIMEOUT_SECONDS=60
```

Bila Hermes Agent tidak dapat dihubungi, SAVI menjawab "SAVI sedang tidak dapat dihubungi" dan mengarahkan ke Pencarian. Tidak ada jawaban tebakan.

## Pemeriksaan Sebelum Dipakai

1. `curl -s -H "Authorization: Bearer $API_SERVER_KEY" http://127.0.0.1:8642/v1/toolsets` tidak menampilkan alat apa pun yang aktif.
2. Tanpa kunci, permintaan ke `http://127.0.0.1:8642/v1/chat/completions` ditolak.
3. `hermes config show` menunjukkan `model.base_url` mengarah ke server model di jaringan kantor.
4. Dari komputer lain di jaringan, port 8642 tidak dapat dibuka.
5. Satu pertanyaan uji di halaman SAVI AI menghasilkan jawaban dengan sitasi, dan jejak audit mencatat permintaannya.

Hasil pemeriksaan dicatat di `CHANGELOG.md` sebelum mode `hermes_agent` dipakai untuk demo.

## Open Questions

- Spesifikasi server kantor dan model lokal yang sanggup dijalankan (OQ-11, PARTIAL).
- Bila demo memakai model cloud dengan data contoh, perlu persetujuan tertulis mentor (DEC-20261110-01).

## Related Documents

- [hermes-overview.md](hermes-overview.md)
- [provider-abstraction.md](../03-architecture/provider-abstraction.md)
- [decision-log.md](../12-governance/decision-log.md)
