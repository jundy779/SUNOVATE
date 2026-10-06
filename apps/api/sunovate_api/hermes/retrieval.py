"""RetrievalService: authorization filtering BEFORE scoring, then lexical scoring.

Current implementation is lexical over the SIMULATED store. Hybrid PostgreSQL
FTS + pgvector retrieval is PROPOSED (docs/05-ai-rag/retrieval-strategy.md).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..authz.principal import Principal
from ..authz.service import AuthorizationService
from ..store.records import DocumentChunk, KnowledgeEntry
from ..store.repository import Repository
from .scope_guard import is_instruction_like
from .text import terms


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    entry: KnowledgeEntry
    matched: frozenset[str]
    coverage: float
    score: float


class RetrievalService:
    def __init__(self, store: Repository, authz: AuthorizationService) -> None:
        self._store = store
        self._authz = authz

    def authorized_entries(
        self, principal: Principal, *, max_classification: str | None = None
    ) -> list[KnowledgeEntry]:
        """Entries the principal may read that are eligible for retrieval."""
        entries = self._authz.list_readable(
            principal,
            KnowledgeEntry,
            where={"lifecycle_status": "PUBLISHED"},
            max_classification=max_classification,
        )
        # Defense in depth: drafts and in-review entries never reach retrieval (BR-04).
        return [e for e in entries if e.lifecycle_status == "PUBLISHED"]

    def candidates(
        self,
        principal: Principal,
        query_terms: frozenset[str],
        *,
        max_classification: str | None,
        limit: int = 20,
    ) -> list[RetrievedChunk]:
        if not query_terms:
            return []
        results: list[RetrievedChunk] = []
        entries = self.authorized_entries(principal, max_classification=max_classification)
        chunks = self._store.chunks_of_entries([e.id for e in entries])
        for entry in entries:
            for chunk in chunks.get(entry.id, []):
                text_terms = terms(f"{entry.title} {chunk.section_label} {chunk.content}")
                matched = query_terms & text_terms
                if not matched:
                    continue
                coverage = len(matched) / len(query_terms)
                results.append(RetrievedChunk(chunk, entry, matched, coverage, coverage))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]


class LexicalReranker:
    """Boosts passages whose content (not only title) covers the query terms."""

    def rerank(
        self, query_terms: frozenset[str], items: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        def rescore(item: RetrievedChunk) -> RetrievedChunk:
            content_cov = len(query_terms & terms(item.chunk.content)) / max(len(query_terms), 1)
            score = round(0.6 * item.coverage + 0.4 * content_cov, 4)
            return RetrievedChunk(item.chunk, item.entry, item.matched, item.coverage, score)

        return sorted((rescore(i) for i in items), key=lambda r: r.score, reverse=True)


def exclude_instruction_like(items: list[RetrievedChunk]) -> tuple[list[RetrievedChunk], int]:
    """Indirect prompt-injection defense: drop passages containing instruction-like text."""
    kept = [i for i in items if not is_instruction_like(i.chunk.content)]
    return kept, len(items) - len(kept)
