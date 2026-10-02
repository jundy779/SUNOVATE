"""Document references and versions. Files are never stored; only references (BR-08)."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, not_found
from ..core.responses import ApiModel, Pagination, envelope, paginated, serialize
from ..store.records import DocumentReference, DocumentVersion
from ._common import governed_view

router = APIRouter(prefix="/documents", tags=["document metadata and versions"])


class VersionCreate(ApiModel):
    version_label: str = Field(min_length=1, max_length=64)
    checksum_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    provider_location: str = Field(min_length=9, max_length=1000)
    size_bytes: int | None = Field(default=None, ge=0)


def document_readable(ctx: AppContext, principal: Principal, doc: DocumentReference) -> bool:
    if ctx.authz.can_read(principal, doc):
        return True
    entry = ctx.store.knowledge.get(doc.knowledge_entry_id) if doc.knowledge_entry_id else None
    return (
        entry is not None
        and doc.deleted_at is None
        and ctx.authz.can_read(principal, entry)
        and ctx.authz.classification_allowed(principal.clearance_code, doc.classification_code)
    )


def _get(ctx: AppContext, principal: Principal, document_id: UUID) -> DocumentReference:
    doc = ctx.store.documents.get(document_id)
    if doc is None or not document_readable(ctx, principal, doc):
        raise not_found("Dokumen")
    return doc


def _view(ctx: AppContext, doc: DocumentReference) -> dict[str, Any]:
    location = ctx.providers.document.describe(doc.provider_location)
    return governed_view(ctx, doc, providerNote=location.note, fileAvailable=location.available)


@router.get("")
def list_documents(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("document:read", resource="document"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    docs = [d for d in ctx.store.documents.values() if document_readable(ctx, principal, d)]
    docs.sort(key=lambda d: d.title)
    page, meta = paginated(docs, pagination)
    return envelope([_view(ctx, d) for d in page], **meta)


@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("document:read", resource="document"))],
) -> dict[str, Any]:
    return envelope(_view(ctx, _get(ctx, principal, document_id)))


@router.get("/{document_id}/versions")
def list_versions(
    document_id: UUID,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("document:read", resource="document"))],
) -> dict[str, Any]:
    doc = _get(ctx, principal, document_id)
    versions = ctx.store.versions_of(doc.id)
    return envelope([serialize(v) for v in versions], total=len(versions))


@router.post("/{document_id}/versions", status_code=201)
def register_version(
    document_id: UUID,
    body: VersionCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("document:version", resource="document"))],
) -> dict[str, Any]:
    with ctx.store.lock:
        doc = _get(ctx, principal, document_id)
        if not ctx.authz.can_write(principal, doc):
            ctx.authz.deny_write(principal, doc, "document_reference")
        if not ctx.providers.document.describe(body.provider_location).location.startswith(
            "local://"
        ):
            raise ApiError(
                422, "VALIDATION_ERROR", "Hanya referensi local:// yang didukung pada pengembangan"
            )
        if any(v.checksum_sha256 == body.checksum_sha256 for v in ctx.store.versions_of(doc.id)):
            raise ApiError(
                409, "DUPLICATE_CHECKSUM", "Versi dengan checksum yang sama sudah terdaftar"
            )
        version = DocumentVersion(
            document_reference_id=doc.id,
            version_label=body.version_label,
            checksum_sha256=body.checksum_sha256,
            size_bytes=body.size_bytes,
            provider_location=body.provider_location,
            # No extraction pipeline yet: new versions are registered, not indexed.
            extraction_status="PENDING",
            created_by=principal.user_id,
            data_origin="USER_ENTERED",
        )
        ctx.store.versions[version.id] = version
    ctx.store.audit(
        actor_user_id=principal.user_id,
        action="VERSION_REGISTER",
        entity_type="document_version",
        entity_id=version.id,
        detail={"documentReferenceId": str(doc.id)},
    )
    return envelope(serialize(version))
