"""HermesGateway: the only entry point to Hermes inside the API.

Flow: scope guard -> authorization context -> retrieval of authorized passages
(filtered before scoring) -> rerank -> injection filter -> HermesClient ->
citation validation -> output guard -> audit -> response.

Hermes (HermesClient) receives only authorized passages and never touches the store.
The gateway reads through the permission-checked application services first and
writes everything (conversation, messages, citations, approval, audit) in one
transaction afterwards, so nothing is held open during generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..authz.principal import Principal
from ..authz.service import AuthorizationService
from ..core.errors import ApiError, not_found
from ..providers.interfaces import ContextPassage, GenerationRequest, HermesClient
from ..store.records import AiCitation, AiConversation, AiMessage, ApprovalRequest
from ..store.repository import Repository
from .guards import CitationValidator, OutputGuard
from .retrieval import LexicalReranker, RetrievalService, RetrievedChunk, exclude_instruction_like
from .scope_guard import ScopeGuard
from .text import terms

MIN_COVERAGE = 0.4
MIN_SCORE = 0.45
MAX_PASSAGES = 3
RELATIVE_CUTOFF = 0.6

INSUFFICIENT_MESSAGE = (
    "Bukti pada sumber yang dapat Anda akses belum cukup untuk menjawab pertanyaan ini. "
    "Hermes tidak menebak jawaban."
)
BLOCKED_MESSAGE = (
    "Jawaban ditahan oleh pemeriksaan keluaran karena berpotensi memuat data sensitif."
)


@dataclass(frozen=True)
class HermesCitation:
    index: int
    knowledge_entry_id: UUID
    document_chunk_id: UUID
    title: str
    section_label: str
    version_label: str
    knowledge_type: str
    classification_code: str


@dataclass(frozen=True)
class HermesResult:
    conversation_id: UUID
    message_id: UUID
    decision: str
    reason: str
    answer: str
    citations: tuple[HermesCitation, ...]
    excluded_passages: int
    approval_request_id: UUID | None


class HermesGateway:
    def __init__(
        self,
        *,
        store: Repository,
        authz: AuthorizationService,
        client: HermesClient,
        max_classification: str,
        enabled: bool,
    ) -> None:
        self._store = store
        self._authz = authz
        self._client = client
        self._max_classification = max_classification
        self._enabled = enabled
        self._scope = ScopeGuard()
        self._retrieval = RetrievalService(store, authz)
        self._reranker = LexicalReranker()
        self._citations = CitationValidator()

    # Helpers -----------------------------------------------------------------

    def _ceiling(self, principal: Principal) -> str:
        """Lower of the user's clearance and the Hermes processing ceiling."""
        user_rank = self._store.classification_rank(principal.clearance_code) or 0
        hermes_rank = self._store.classification_rank(self._max_classification) or 0
        target = min(user_rank, hermes_rank)
        return next(c.code for c in self._store.classifications() if c.rank == target)

    def _conversation(
        self, principal: Principal, conversation_id: UUID | None, question: str
    ) -> tuple[AiConversation, bool]:
        """Existing conversation of the caller (404 otherwise) or a new, unsaved one."""
        if conversation_id is not None:
            existing = self._store.conversation(conversation_id)
            if existing is None or existing.user_id != principal.user_id:
                raise not_found("Percakapan")
            return existing, False
        return AiConversation(user_id=principal.user_id, title=question[:80]), True

    def _select(
        self, items: list[RetrievedChunk], query_terms: frozenset[str]
    ) -> list[RetrievedChunk]:
        """Evidence threshold (PROPOSED values, see docs/05-ai-rag/retrieval-strategy.md):
        - coverage (title + section + content) >= MIN_COVERAGE,
        - >= 2 matched terms (or the only term for single-term queries),
        - reranked score >= MIN_SCORE, so title/section-only matches are not evidence.
        """
        required_terms = min(2, len(query_terms))
        if (
            not items
            or items[0].coverage < MIN_COVERAGE
            or len(items[0].matched) < required_terms
            or items[0].score < MIN_SCORE
        ):
            return []
        floor = max(items[0].score * RELATIVE_CUTOFF, MIN_SCORE)
        chosen = [i for i in items if i.coverage >= MIN_COVERAGE and i.score >= floor]
        return chosen[:MAX_PASSAGES]

    def _approval_for_write(self, principal: Principal, question: str) -> ApprovalRequest | None:
        """Builds (does not save) the human-approval request. Execution is never implemented."""
        if not principal.has("approval:request") or not principal.team_ids:
            return None
        return ApprovalRequest(
            request_type="HERMES_WRITE_ACTION",
            target_entity_type="hermes_proposed_action",
            target_entity_id=None,
            requested_by=principal.user_id,
            owner_team_id=sorted(principal.team_ids)[0],
            owner_user_id=principal.user_id,
            classification_code="INTERNAL",
            created_by=principal.user_id,
            payload={"proposedActionText": question[:500], "executed": False},
            data_origin="USER_ENTERED",
        )

    # Pipeline ----------------------------------------------------------------

    def query(
        self, principal: Principal, question: str, conversation_id: UUID | None = None
    ) -> HermesResult:
        if not self._enabled:
            raise ApiError(503, "HERMES_DISABLED", "Hermes dinonaktifkan pada lingkungan ini")
        classifications = self._store.classifications()
        output_guard = OutputGuard({c.code: c.rank for c in classifications})

        # Read phase: no writes; every record below is built in memory.
        conversation, is_new = self._conversation(principal, conversation_id, question)
        user_message = AiMessage(conversation_id=conversation.id, role="USER", content=question)

        decision, reason, answer = "ANSWERED", "ok", ""
        citations: tuple[HermesCitation, ...] = ()
        excluded = 0
        approval: ApprovalRequest | None = None

        scope = self._scope.evaluate(question)
        if scope.decision is not None:
            decision, reason, answer = scope.decision, scope.reason, scope.message
            if decision == "REQUIRES_HUMAN_APPROVAL":
                approval = self._approval_for_write(principal, question)
                if approval is None:
                    answer += " Anda tidak memiliki izin untuk mengajukan approval."
        else:
            ceiling = self._ceiling(principal)
            query_terms = terms(question)
            ranked = self._reranker.rerank(
                query_terms,
                self._retrieval.candidates(principal, query_terms, max_classification=ceiling),
            )
            safe, excluded = exclude_instruction_like(ranked)
            selected = self._select(safe, query_terms)
            if not selected:
                decision, reason, answer = (
                    "INSUFFICIENT_EVIDENCE",
                    "low_coverage",
                    (INSUFFICIENT_MESSAGE),
                )
            else:
                citation_map = {n: item for n, item in enumerate(selected, start=1)}
                passages = [
                    ContextPassage(n, i.entry.title, i.chunk.section_label, i.chunk.content)
                    for n, i in citation_map.items()
                ]
                draft = self._client.answer(GenerationRequest(question, passages, query_terms))
                check = self._citations.validate(
                    draft.text, citation_map, frozenset(i.chunk.id for i in safe)
                )
                guard = output_guard.check(
                    draft.text,
                    [
                        citation_map[n].entry.classification_code
                        for n in check.used_indexes
                        if n in citation_map
                    ],
                    ceiling=ceiling,
                )
                if not check.valid:
                    decision, reason, answer = (
                        "INSUFFICIENT_EVIDENCE",
                        check.reason,
                        (INSUFFICIENT_MESSAGE),
                    )
                elif not guard.allowed:
                    decision, reason, answer = (
                        "BLOCKED_BY_OUTPUT_GUARD",
                        guard.reason,
                        (BLOCKED_MESSAGE),
                    )
                else:
                    answer = draft.text
                    citations = tuple(
                        HermesCitation(
                            index=n,
                            knowledge_entry_id=citation_map[n].entry.id,
                            document_chunk_id=citation_map[n].chunk.id,
                            title=citation_map[n].entry.title,
                            section_label=citation_map[n].chunk.section_label,
                            version_label=citation_map[n].entry.version_label,
                            knowledge_type=citation_map[n].entry.knowledge_type,
                            classification_code=citation_map[n].entry.classification_code,
                        )
                        for n in check.used_indexes
                    )

        cited_ranks = [
            self._store.classification_rank(c.classification_code) or 0 for c in citations
        ]
        message_rank = max(cited_ranks, default=1)
        assistant = AiMessage(
            conversation_id=conversation.id,
            role="ASSISTANT",
            content=answer,
            decision=decision,
            classification_code=next(c.code for c in classifications if c.rank == message_rank),
        )
        citation_records = [
            AiCitation(
                message_id=assistant.id,
                citation_index=citation.index,
                knowledge_entry_id=citation.knowledge_entry_id,
                document_chunk_id=citation.document_chunk_id,
                score=0.0,
            )
            for citation in citations
        ]

        # Write phase: all or nothing.
        with self._store.transaction():
            if is_new:
                self._store.insert(conversation)
            self._store.insert(user_message)
            self._store.insert(assistant)
            for record in citation_records:
                self._store.insert(record)
            if approval is not None:
                self._store.insert(approval)
                self._store.audit(
                    actor_user_id=principal.user_id,
                    action="CREATE",
                    entity_type="approval_request",
                    entity_id=approval.id,
                    detail={"requestType": approval.request_type},
                )
            self._store.audit(
                actor_user_id=principal.user_id,
                action="AI_QUERY",
                entity_type="ai_message",
                entity_id=assistant.id,
                outcome="SUCCESS" if decision == "ANSWERED" else "REFUSED",
                detail={
                    "decision": decision,
                    "reason": reason,
                    "citationCount": len(citations),
                    "excludedPassages": excluded,
                    "questionLength": len(question),
                },
            )
        return HermesResult(
            conversation.id,
            assistant.id,
            decision,
            reason,
            answer,
            citations,
            excluded,
            approval.id if approval is not None else None,
        )
