"""Lightweight Indonesian text normalization for lexical retrieval.

A deliberately simple affix stripper; it is applied identically to queries and
passages, so imperfect stems still match. Replace with PostgreSQL FTS and an
approved embedding model later (docs/05-ai-rag/retrieval-strategy.md).
"""

from __future__ import annotations

import re

_WORD = re.compile(r"[a-z0-9]+")

STOPWORDS = frozenset(
    [
        "apa",
        "saja",
        "saat",
        "yang",
        "dan",
        "di",
        "ke",
        "dari",
        "untuk",
        "dengan",
        "bagaimana",
        "siapa",
        "mana",
        "apakah",
        "adalah",
        "ini",
        "itu",
        "pada",
        "dalam",
        "atau",
        "tolong",
        "mohon",
        "jelaskan",
        "sebutkan",
        "isi",
        "simulasi",
        "tentang",
        "seperti",
        "berapa",
        "kapan",
        "mengapa",
        "kenapa",
        "bisa",
        "dapat",
        "harus",
        "akan",
        "sudah",
        "belum",
        "juga",
        "oleh",
        "sebagai",
        "para",
        "kami",
        "kita",
        "saya",
        "anda",
        "the",
        "a",
        "an",
        "of",
        "to",
        "and",
        "or",
        "is",
        "are",
        "what",
        "how",
        "which",
        "please",
        "tell",
        "me",
        "about",
    ]
)

_SUFFIXES = ("nya", "kan", "an", "i")
_PREFIXES = (
    "meng",
    "meny",
    "mem",
    "men",
    "me",
    "peng",
    "peny",
    "pem",
    "pen",
    "per",
    "pe",
    "ber",
    "ter",
    "di",
)


def normalize_term(word: str) -> str:
    term = word.lower()
    for suffix in _SUFFIXES:
        if term.endswith(suffix) and len(term) - len(suffix) >= 4:
            term = term[: -len(suffix)]
            break
    for prefix in _PREFIXES:
        if term.startswith(prefix) and len(term) - len(prefix) >= 4:
            term = term[len(prefix) :]
            break
    return term


def terms(text: str) -> frozenset[str]:
    """Distinct normalized content terms of a text."""
    return frozenset(
        normalize_term(w) for w in _WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 1
    )
