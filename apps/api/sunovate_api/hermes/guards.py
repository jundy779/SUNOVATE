"""CitationValidator and OutputGuard."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

from .retrieval import RetrievedChunk

_MARKER = re.compile(r"\[(\d+)\]")

SENSITIVE_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"\b(api[_-]?key|secret|password|kata\s+sandi|token)\s*[:=]\s*\S+",
        r"\bsk-[A-Za-z0-9]{20,}\b",
        r"\b\d{16}\b",  # 16-digit identifiers such as NIK
        r"\b(DEV_AUTH_SECRET|DATABASE_URL|HERMES_API_KEY)\b",
    )
)


@dataclass(frozen=True)
class CitationCheck:
    valid: bool
    used_indexes: tuple[int, ...]
    reason: str


class CitationValidator:
    """Every marker must map to an authorized retrieved passage; at least one is required."""

    def validate(
        self,
        text: str,
        citation_map: Mapping[int, RetrievedChunk],
        authorized_chunk_ids: frozenset[UUID],
    ) -> CitationCheck:
        used = tuple(sorted({int(m) for m in _MARKER.findall(text)}))
        if not used:
            return CitationCheck(False, used, "no_citation")
        for index in used:
            item = citation_map.get(index)
            if item is None:
                return CitationCheck(False, used, "unknown_citation")
            if item.chunk.id not in authorized_chunk_ids:
                return CitationCheck(False, used, "unauthorized_citation")
        return CitationCheck(True, used, "ok")


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    reason: str


class OutputGuard:
    def __init__(self, rank: Mapping[str, int]) -> None:
        self._rank = rank

    def check(self, text: str, cited_classifications: list[str], *, ceiling: str) -> GuardResult:
        if any(p.search(text) for p in SENSITIVE_PATTERNS):
            return GuardResult(False, "sensitive_pattern")
        limit = self._rank.get(ceiling)
        for code in cited_classifications:
            rank = self._rank.get(code)
            if limit is None or rank is None or rank > limit:
                return GuardResult(False, "classification_ceiling")
        return GuardResult(True, "ok")
