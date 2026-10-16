# Batas Data Privat SUNOVATE

**Status:** ACTIVE PROJECT SAFETY BASELINE
**Last Updated:** 2026-10-17

## Keputusan Kerja

**CONFIRMED (arahan project lead, sesi 2026-10-17):** SUNOVATE harus diperlakukan sebagai sistem privat. Seluruh data selain fixture `SIMULATED_DATA` dianggap sangat sensitif sampai klasifikasi dan izin pemrosesan resminya ditetapkan oleh pihak berwenang. Arahan ini tidak menjadi izin memasukkan data asli ke lingkungan pengembangan atau demo.

## Larangan Mutlak

- Tidak memublikasikan data, dokumen, potongan, metadata sensitif, prompt, atau hasil SAVI ke internet publik.
- Tidak membuat isi SUNOVATE dapat ditemukan melalui mesin pencari, crawler, scraper, AI Search, SEO, GEO, AIO, dataset pelatihan, agent eksternal, plugin, MCP, webhook, atau model AI publik.
- Tidak mengirim data SUNOVATE ke ChatGPT, Claude, Gemini, Copilot, provider embedding, telemetry, analytics, atau layanan luar sebelum ada keputusan tertulis mengenai provider, lokasi pemrosesan, klasifikasi data, perjanjian, dan pengendalian teknis.
- Tidak mengaktifkan web search, URL fetch, tool eksternal, tindakan otomatis, atau akses basis data langsung bagi SAVI.
- Tidak menggunakan prompt, encoding, pemecahan pesan, terjemahan, role-play, atau jailbreak untuk melewati izin dan klasifikasi.
- Tidak menyimpan data asli pada Git, fixture, tangkapan layar, log, issue, pull request, chat pengembangan, atau kanal publik.

## Kontrol yang Diimplementasikan

| Lapisan | Kontrol aplikasi | Batas kontrol |
|---|---|---|
| Konfigurasi API | Mode privat dikunci; public indexing, egress AI, agent eksternal, dan telemetry egress hanya menerima nilai aman. Konfigurasi berbahaya menggagalkan startup. | Tidak menggantikan firewall jaringan. |
| Web dan API | `noindex`, `nofollow`, `noarchive`, `nosnippet`, `noimageindex`, `robots.txt` menolak seluruh path, respons `no-store`, CSP membatasi koneksi ke origin sendiri, referrer dinonaktifkan. | `robots.txt` bukan kontrol autentikasi. Crawler jahat dapat mengabaikannya. |
| Alat build web | Telemetry Next.js dinonaktifkan sebelum perintah development, build, dan start; environment contoh juga menetapkan `NEXT_TELEMETRY_DISABLED=1`. | Dependency scan dan kebijakan egress host tetap diperlukan. |
| API non-pengembangan | Dokumentasi interaktif dan OpenAPI disembunyikan pada staging/production. | Endpoint tetap wajib berada di jaringan privat dan menggunakan autentikasi resmi. |
| SAVI | Pertanyaan jailbreak, pengungkapan secret, akses lintas izin, publikasi, indexing, serta pengiriman data ke AI/agent eksternal ditolak sebelum retrieval. | Deteksi berbasis aturan tidak boleh menjadi satu-satunya kontrol. |
| Retrieval | Permission, scope tim, dan batas klasifikasi diperiksa sebelum pencocokan serta jawaban. | Matriks resmi masih membutuhkan validasi mentor/pemilik kewenangan. |

## Kontrol Infrastruktur Wajib Sebelum Data Asli

Kode aplikasi saja tidak dapat menjamin data tidak pernah keluar. Sebelum satu pun data asli diproses, pihak TIK/keamanan dan pemilik data harus menyetujui serta memverifikasi:

1. jaringan privat atau allowlist yang menolak akses publik;
2. firewall egress deny-by-default dengan daftar tujuan yang disetujui;
3. SSO/MFA resmi, akun bernama, least privilege, dan pencabutan akses;
4. TLS, enkripsi penyimpanan, pengelolaan secret, backup terenkripsi, dan uji pemulihan;
5. audit akses, alert anomali, retensi log tanpa isi sensitif, serta prosedur insiden;
6. pengujian penetrasi, prompt-injection, jailbreak, kebocoran lintas tim, dan data exfiltration;
7. persetujuan tertulis klasifikasi, lokasi pemrosesan, provider, retensi, dan daftar data yang boleh digunakan.

Cloudflare Tunnel, akses internet langsung, provider AI eksternal, Telegram, WhatsApp, SharePoint, Power BI, telemetry, atau RAG pihak ketiga tidak boleh dianggap aman atau aktif hanya karena tercantum pada roadmap.

## Kriteria Blokir Rilis

Rilis diblokir bila ada data yang dapat diakses tanpa autentikasi, respons sensitif dapat di-cache, izin dapat dilewati, data terkirim ke tujuan luar yang tidak disetujui, dokumen terindeks publik, atau jailbreak mencapai retrieval yang tidak semestinya. Kejadian tersebut diperlakukan sebagai bug P0 dan insiden keamanan.

## Related Documents

- [security-overview](security-overview.md)
- [threat-model](threat-model.md)
- [prompt-injection-defense](../05-ai-rag/prompt-injection-defense.md)
- [incident-response](incident-response.md)
- [deployment-runbook](../11-operations/deployment-runbook.md)

