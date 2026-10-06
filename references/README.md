# references/

Place for source references used to write documentation. `source/` is git-ignored.

Current source documents remain read-only in the repository root and are excluded from git
until storage is approved (ADR-014, OQ-18):

| File | Nature |
|---|---|
| `SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx` | Developer proposal deck (PROPOSED) |
| `v1_SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx` | **Fixed (authoritative) version** of the proposal deck, confirmed by the user on 2026-10-02. Read-only, git-ignored (`/*.pptx`); never edit, move, or delete. Slide 24 is titled "Keputusan yang memerlukan konfirmasi knowledge owner" and carries the knowledge owner's answers (recorded as `CONFIRMED (knowledge owner, deck v1_ slide 24)`; mentor acknowledgement pending, OQ-24) |
| `Pengayaan_Kelas_Magang_6_Mei_2026.pdf` | Dit. SUN intern sharing session (domain background) |
| `Kompilasi_Peraturan_SUN_formal.pdf` | Compilation of public regulations |
| `SUNOVATE_WEB_IMPLEMENTATION_BLUEPRINT_v0.1.md` | Older blueprint (historical PROPOSED) |
| `14_NEW_SESSION_HANDOFF_PROMPT.txt`, `20_NEW_CHAT_MASTER_PROMPT.txt` | Earlier session prompts |

Rules: record origin and classification for anything added; never add internal, personal, or
financial data; never feed these files to Hermes ingestion without approval (OQ-04).

### Changes in the `v1_` deck compared with `SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx`

Verified by extracting slide text from both files (26 slides each).

| Slide | Change |
|---|---|
| 9 (user groups) | "Enam tim kerja dan SME" became "Ketua tim kerja"; "Pengelola Knowledge" became "Pengelola Knowledge / PIC" |
| 18 (governance) | "Pengelola MP / Product Owner" became "Pengelola MP / Product Owner / Ketua Tim" (the deck spells "TIm"); "Knowledge Coordinator" became "Knowledge Coordinator / PMP" (PMP is not expanded in the deck) |
| 24 (decisions) | Title changed from "konfirmasi mentor" to "konfirmasi knowledge owner"; all eight questions now carry short answers (see `docs/00-project/open-questions.md` and `docs/12-governance/decision-log.md`, DEC-20261002-01 to DEC-20261002-09) |
| 4 | Same content; a stray word "Field" appears after "Fokus" (treated as a typo, not propagated) |
| 1, 2, 12, 25 | Same text (only run splitting differs) |
| All other slides | Unchanged |

Where the two decks differ, the `v1_` deck is authoritative. Answers on slide 24 are the knowledge owner's answers, not the mentor's.
