# RAG-Anything isolated pilot

**Status:** PROPOSED, NOT ENABLED
**Last Updated:** 2026-10-16

Folder ini hanya menyediakan preflight untuk pilot RAG-Anything. Tidak ada dependency RAG-Anything yang ditambahkan dan tidak ada dokumen yang diproses.

Jalankan pemeriksaan aman:

```bash
python scripts/experiments/rag_anything/preflight.py \
  --input-dir /tmp/sunovate-rag-anything/input \
  --output-dir /tmp/sunovate-rag-anything/output
```

Preflight hanya lulus bila:

- direktori input dan output berbeda, lokal, bukan symlink, dan berada di bawah root pilot yang sama;
- nama fixture diawali `SIMULASI`;
- semua format berada dalam allowlist pilot;
- jaringan eksternal tidak diizinkan;
- bila paket terpasang, versi bukan `1.4.1` dan minimal `1.4.2`.

Lulusnya preflight bukan izin menjalankan parser. Implementasi parser, container, resource limit, dan dataset fixture memerlukan gate di `docs/05-ai-rag/rag-anything-pilot.md`.
