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


@dataclass(frozen=True)
class EvidenceDecision:
    """Auditable outcome of the deterministic evidence gate."""

    accepted: tuple[RetrievedChunk, ...]
    reason: str
    candidate_count: int
    top_coverage: float
    top_score: float


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
        term_variants: dict[str, frozenset[str]] | None = None,
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
                matched = _matched_query_terms(query_terms, text_terms, term_variants)
                if not matched:
                    continue
                coverage = len(matched) / len(query_terms)
                results.append(RetrievedChunk(chunk, entry, matched, coverage, coverage))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]


class LexicalReranker:
    """Boosts passages whose content (not only title) covers the query terms."""

    def rerank(
        self,
        query_terms: frozenset[str],
        items: list[RetrievedChunk],
        term_variants: dict[str, frozenset[str]] | None = None,
    ) -> list[RetrievedChunk]:
        def rescore(item: RetrievedChunk) -> RetrievedChunk:
            content_matched = _matched_query_terms(
                query_terms, terms(item.chunk.content), term_variants
            )
            content_cov = len(content_matched) / max(len(query_terms), 1)
            score = round(0.6 * item.coverage + 0.4 * content_cov, 4)
            return RetrievedChunk(item.chunk, item.entry, item.matched, item.coverage, score)

        return sorted((rescore(i) for i in items), key=lambda r: r.score, reverse=True)


class EvidenceGate:
    """Reject weak retrieval before any passage reaches the answer provider."""

    def __init__(
        self,
        *,
        min_coverage: float = 0.6,
        min_score: float = 0.45,
        relative_cutoff: float = 0.6,
        max_passages: int = 3,
    ) -> None:
        self._min_coverage = min_coverage
        self._min_score = min_score
        self._relative_cutoff = relative_cutoff
        self._max_passages = max_passages

    def evaluate(
        self, items: list[RetrievedChunk], query_terms: frozenset[str]
    ) -> EvidenceDecision:
        if not items:
            return EvidenceDecision((), "no_candidates", 0, 0.0, 0.0)

        top = items[0]
        def reject(reason: str) -> EvidenceDecision:
            return EvidenceDecision((), reason, len(items), top.coverage, top.score)

        if top.coverage < self._min_coverage:
            return reject("insufficient_coverage")
        required_terms = min(2, len(query_terms))
        if len(top.matched) < required_terms:
            return reject("insufficient_term_support")
        if top.score < self._min_score:
            return reject("insufficient_rerank_score")

        floor = max(top.score * self._relative_cutoff, self._min_score)
        accepted = tuple(
            item
            for item in items
            if item.coverage >= self._min_coverage and item.score >= floor
        )[: self._max_passages]
        if not accepted:
            return reject("no_passage_above_gate")
        return EvidenceDecision(
            accepted, "evidence_sufficient", len(items), top.coverage, top.score
        )


def _matched_query_terms(
    query_terms: frozenset[str],
    text_terms: frozenset[str],
    term_variants: dict[str, frozenset[str]] | None,
) -> frozenset[str]:
    if term_variants is None:
        return query_terms & text_terms
    return frozenset(
        term for term in query_terms if term_variants.get(term, frozenset({term})) & text_terms
    )


def exclude_instruction_like(items: list[RetrievedChunk]) -> tuple[list[RetrievedChunk], int]:
    """Indirect prompt-injection defense: drop passages containing instruction-like text."""
    kept = [i for i in items if not is_instruction_like(i.chunk.content)]
    return kept, len(items) - len(kept)
