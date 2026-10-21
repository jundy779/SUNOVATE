"""View-only access to RAHASIA documents (ADR-020, PROPOSED).

There is deliberately no route that returns a file, its text, or a download link. The only
content route returns one watermarked raster page at a time to an explicitly granted reader who
has accepted the confidentiality notice within the last 30 minutes.
Unauthorized readers get the same 404 as a missing document, and the attempt is audited.
"""

from __future__ import annotations

import hashlib
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Path
from fastapi.responses import Response

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, not_found
from ..core.responses import envelope
from ..secure.crypto import DecryptionError
from ..secure.render import render_page, watermark_label
from ..secure.vault import SecureDocument, jakarta_now

router = APIRouter(prefix="/secure-documents", tags=["secure view-only documents"])

ENTITY = "secure_document"
_PAGE_HEADERS = {
    "Cache-Control": "no-store, private, max-age=0",
    "Pragma": "no-cache",
    "Content-Disposition": "inline",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'none'",
    "Cross-Origin-Resource-Policy": "same-origin",
}

Reader = Annotated[Principal, Depends(require("document:read", resource=ENTITY))]


def _readable(ctx: AppContext, principal: Principal, document: SecureDocument) -> bool:
    return principal.email.lower() in document.reader_emails and ctx.authz.classification_allowed(
        principal.clearance_code, document.classification_code
    )


def _get_readable(
    ctx: AppContext, principal: Principal, document_id: UUID, action: str
) -> SecureDocument:
    document = ctx.vault.get(document_id)
    if document is None or not _readable(ctx, principal, document):
        with ctx.store.transaction():
            ctx.store.audit_denial(
                actor_user_id=principal.user_id,
                action=action,
                entity_type=ENTITY,
                entity_id=document_id,
                detail={"reason": "NOT_FOUND_OR_NOT_GRANTED"},
            )
        raise not_found("Dokumen")
    return document


def _view(document: SecureDocument) -> dict[str, Any]:
    return {
        "id": str(document.id),
        "title": document.title,
        "classificationCode": document.classification_code,
        "ownerTeamCode": document.owner_team_code,
        "pageCount": document.page_count,
        "handling": "VIEW_ONLY",
    }


@router.get("")
def list_secure_documents(ctx: Ctx, principal: Reader) -> dict[str, Any]:
    """Only documents granted to the caller are listed; others are not revealed to exist."""
    rows = [_view(doc) for doc in ctx.vault.documents() if _readable(ctx, principal, doc)]
    return envelope(rows, total=len(rows))


@router.get("/{document_id}")
def get_secure_document(ctx: Ctx, principal: Reader, document_id: UUID) -> dict[str, Any]:
    return envelope(_view(_get_readable(ctx, principal, document_id, "SECURE_DOCUMENT_READ")))


@router.post("/{document_id}/acknowledgements", status_code=201)
def accept_notice(ctx: Ctx, principal: Reader, document_id: UUID) -> dict[str, Any]:
    """The reader confirms the confidentiality notice; pages stay locked until then."""
    document = _get_readable(ctx, principal, document_id, "SECURE_NOTICE_ACCEPTED")
    ctx.vault.notices.accept(principal.user_id, document.id)
    with ctx.store.transaction():
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="SECURE_NOTICE_ACCEPTED",
            entity_type=ENTITY,
            entity_id=document.id,
        )
    return envelope({"accepted": True, "validMinutes": ctx.vault.notices.ttl_seconds // 60})


@router.get("/{document_id}/pages/{page_number}", response_class=Response)
def render_secure_page(
    ctx: Ctx,
    principal: Reader,
    document_id: UUID,
    page_number: Annotated[int, Path(ge=1, le=500)],
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    document = _get_readable(ctx, principal, document_id, "SECURE_PAGE_VIEW")
    if page_number > document.page_count:
        raise not_found("Halaman")
    if not ctx.vault.notices.is_valid(principal.user_id, document.id):
        raise ApiError(
            428,
            "SECURE_NOTICE_REQUIRED",
            "Setujui pernyataan kerahasiaan sebelum membuka halaman dokumen.",
        )

    access = ctx.vault.limiter.check(principal.user_id)
    if not access.allowed:
        with ctx.store.transaction():
            ctx.store.audit_denial(
                actor_user_id=principal.user_id,
                action="SECURE_PAGE_VIEW",
                entity_type=ENTITY,
                entity_id=document.id,
                detail={"reason": "PAGE_RATE_LIMITED", "page": page_number},
            )
        raise ApiError(
            429,
            "SECURE_VIEW_RATE_LIMITED",
            "Terlalu banyak halaman dibuka dalam waktu singkat. Coba lagi sebentar lagi.",
            details={"retryAfterSeconds": access.retry_after_seconds},
            headers={"Retry-After": str(access.retry_after_seconds)},
        )

    try:
        body = ctx.vault.page_text(document, page_number)
    except DecryptionError as exc:
        raise ApiError(409, "SECURE_DOCUMENT_UNAVAILABLE", "Dokumen tidak dapat dibuka.") from exc

    viewed_at = jakarta_now()
    token = (authorization or "")[7:].strip()
    session_ref = hashlib.sha256(token.encode()).hexdigest()[:8] if token else "-"
    image = render_page(
        title=document.title,
        page_number=page_number,
        page_count=document.page_count,
        body=body,
        watermark=watermark_label(
            display_name=principal.display_name,
            email=principal.email,
            viewed_at=viewed_at,
            session_ref=session_ref,
        ),
    )
    with ctx.store.transaction():
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="SECURE_PAGE_VIEW",
            entity_type=ENTITY,
            entity_id=document.id,
            detail={"page": page_number, "sessionRef": session_ref, "keyId": ctx.vault.key_id},
        )
    return Response(content=image, media_type="image/png", headers=_PAGE_HEADERS)
