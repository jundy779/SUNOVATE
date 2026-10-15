"""Text search over PUBLISHED knowledge the caller may read.

Authorization filtering happens before candidate selection. PostgreSQL uses
GIN-backed FTS; the simulated backend keeps the deterministic lexical fallback.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.responses import Pagination, envelope, paginated
from ..hermes.retrieval import RetrievalService
from ..hermes.text import terms
from ..store.records import KnowledgeEntry

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("search:query", "knowledge:read", resource="search"))
    ],
    pagination: Annotated[Pagination, Depends()],
    q: Annotated[str, Query(min_length=2, max_length=200)],
) -> dict[str, Any]:
    query_terms = terms(q)
    retrieval = RetrievalService(ctx.store, ctx.authz)
    hits: list[dict[str, Any]] = []
    entries = retrieval.authorized_entries(principal)
    scope = ctx.authz.read_scope(principal, KnowledgeEntry)
    candidates = ctx.store.text_search_candidates(
        [e.id for e in entries], q, classification_codes=scope.classification_codes
    )
    for entry in entries:
        if entry.id not in candidates.entry_ids:
            continue
        entry_terms = terms(f"{entry.title} {entry.summary}")
        best_section, best_snippet, best = None, entry.summary, len(query_terms & entry_terms)
        for chunk in candidates.chunks_by_entry.get(entry.id, []):
            matched = len(query_terms & (entry_terms | terms(chunk.content)))
            if matched > best:
                best_section, best_snippet, best = chunk.section_label, chunk.content, matched
        if best == 0:
            continue
        hits.append(
            {
                "knowledgeEntryId": entry.id,
                "title": entry.title,
                "knowledgeType": entry.knowledge_type,
                "ownerTeamCode": ctx.store.team_code(entry.owner_team_id),
                "classificationCode": entry.classification_code,
                "sectionLabel": best_section,
                "snippet": best_snippet[:280],
                "score": round(best / max(len(query_terms), 1), 3),
            }
        )
    hits.sort(key=lambda h: (-float(h["score"]), str(h["title"])))
    ctx.store.audit(
        actor_user_id=principal.user_id,
        action="SEARCH",
        entity_type="search",
        detail={"queryLength": len(q), "resultCount": len(hits)},
    )
    page, meta = paginated(hits, pagination)
    mode = "postgres_fts" if ctx.data_backend == "postgres" else "lexical"
    return envelope(page, **meta, mode=mode)
