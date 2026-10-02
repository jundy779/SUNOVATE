"""Hermes gateway API. Hermes reaches data only through HermesGateway (ADR-004)."""

from __future__ import annotations

from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.errors import not_found
from ..core.responses import ApiModel, envelope
from ..store.records import AiFeedback

router = APIRouter(prefix="/hermes", tags=["Hermes gateway"])


class HermesQuery(ApiModel):
    question: str = Field(min_length=3, max_length=2000)
    conversation_id: UUID | None = None


class FeedbackRequest(ApiModel):
    rating: Literal["HELPFUL", "NOT_HELPFUL"]
    comment: str | None = Field(default=None, max_length=1000)


@router.post("/query")
def query(
    body: HermesQuery,
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("hermes:query", "search:query", resource="hermes"))
    ],
) -> dict[str, Any]:
    result = ctx.hermes.query(principal, body.question.strip(), body.conversation_id)
    return envelope(
        {
            "conversationId": result.conversation_id,
            "messageId": result.message_id,
            "decision": result.decision,
            "reason": result.reason,
            "answer": result.answer,
            "citations": [
                {
                    "index": c.index,
                    "knowledgeEntryId": c.knowledge_entry_id,
                    "documentChunkId": c.document_chunk_id,
                    "title": c.title,
                    "sectionLabel": c.section_label,
                    "versionLabel": c.version_label,
                    "knowledgeType": c.knowledge_type,
                    "classificationCode": c.classification_code,
                }
                for c in result.citations
            ],
            "excludedPassages": result.excluded_passages,
            "approvalRequestId": result.approval_request_id,
        },
        provider=ctx.providers.hermes.name,
    )


@router.post("/messages/{message_id}/feedback", status_code=201)
def feedback(
    message_id: UUID,
    body: FeedbackRequest,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("hermes:feedback", resource="hermes"))],
) -> dict[str, Any]:
    message = ctx.store.messages.get(message_id)
    conversation = ctx.store.conversations.get(message.conversation_id) if message else None
    if (
        message is None
        or conversation is None
        or message.role != "ASSISTANT"
        or conversation.user_id != principal.user_id
    ):
        raise not_found("Pesan")
    item = AiFeedback(
        message_id=message.id,
        user_id=principal.user_id,
        rating=body.rating,
        comment=body.comment,
        data_origin="USER_ENTERED",
    )
    with ctx.store.lock:
        ctx.store.feedback.append(item)
    ctx.store.audit(
        actor_user_id=principal.user_id,
        action="AI_FEEDBACK",
        entity_type="ai_message",
        entity_id=message.id,
        detail={"rating": body.rating},
    )
    return envelope({"id": item.id, "messageId": message.id, "rating": item.rating})
