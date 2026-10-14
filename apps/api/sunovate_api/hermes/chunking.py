"""Deterministic structure-aware chunk previews for extracted text.

This module does not read files, write to the database, or publish knowledge.
It is the reviewable Python boundary between text extraction and a future,
approved ingestion pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

_PASAL = re.compile(r"(?im)^(?=\s*Pasal\s*\d+[A-Za-z]?\b)")
_STEP = re.compile(r"(?im)^(?=\s*(?:Langkah|Tahap)\s+\d+[A-Za-z]?\b)")
_REPORT_HEADING = re.compile(
    r"(?m)^(?=\s*(?:#{1,6}\s+.+|(?:RINGKASAN EKSEKUTIF|PENDAHULUAN|METODOLOGI|"
    r"HASIL|PEMBAHASAN|KESIMPULAN|REKOMENDASI)\s*)$)"
)
_SECTION_LABEL = re.compile(
    r"(?i)^\s*(Pasal\s*\d+[A-Za-z]?|(?:Langkah|Tahap)\s+\d+[A-Za-z]?|#{1,6}\s+[^\n]+|"
    r"RINGKASAN EKSEKUTIF|PENDAHULUAN|METODOLOGI|HASIL|PEMBAHASAN|KESIMPULAN|REKOMENDASI)"
)


@dataclass(frozen=True, slots=True)
class ChunkPreview:
    """A stable preview record; deliberately not a database entity."""

    index: int
    section_label: str
    content: str
    word_count: int
    content_hash: str


def _clean(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _structural_units(text: str, knowledge_type: str) -> list[str]:
    kind = knowledge_type.upper().strip()
    splitter = {
        "REGULATION": _PASAL,
        "SOP": _STEP,
        "PLAYBOOK": _STEP,
        "STUDY": _REPORT_HEADING,
        "REPORT": _REPORT_HEADING,
    }.get(kind)
    if splitter is None:
        return [text]
    prefix, *units = [part.strip() for part in splitter.split(text) if part.strip()]
    if not units:
        return [prefix]
    # Introductory text remains its own unit and is never merged across a Pasal.
    return ([prefix] if prefix else []) + units


def _bounded_parts(unit: str, max_words: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", unit) if part.strip()]
    parts: list[str] = []
    current: list[str] = []
    current_words = 0
    for paragraph in paragraphs:
        words = paragraph.split()
        slices = [
            words[start : start + max_words]
            for start in range(0, len(words), max_words)
        ] or [[]]
        for word_slice in slices:
            candidate = " ".join(word_slice)
            if current and current_words + len(word_slice) > max_words:
                parts.append("\n\n".join(current))
                current, current_words = [], 0
            if candidate:
                current.append(candidate)
                current_words += len(word_slice)
    if current:
        parts.append("\n\n".join(current))
    return parts


def chunk_text(
    text: str,
    knowledge_type: str,
    *,
    document_label: str = "Dokumen",
    max_words: int = 400,
) -> tuple[ChunkPreview, ...]:
    """Create a deterministic review preview from already-extracted text.

    ``max_words`` is a development guard, not the production token threshold.
    Structural boundaries are stronger than size targets.
    """
    if max_words < 20:
        raise ValueError("max_words must be at least 20")
    cleaned = _clean(text)
    if not cleaned:
        return ()

    result: list[ChunkPreview] = []
    for unit in _structural_units(cleaned, knowledge_type):
        match = _SECTION_LABEL.match(unit)
        label = re.sub(r"^#+\s*", "", match.group(1)).strip() if match else document_label
        for content in _bounded_parts(unit, max_words):
            result.append(
                ChunkPreview(
                    index=len(result),
                    section_label=label,
                    content=content,
                    word_count=len(content.split()),
                    content_hash=sha256(content.encode("utf-8")).hexdigest(),
                )
            )
    return tuple(result)
