"""Document references and versions. Files are never stored; only references (BR-08)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, not_found
from ..core.responses import ApiModel, Pagination, envelope, paginated, serialize
from ..providers.development import is_safe_local_location
from ..store.records import DocumentReference, DocumentVersion, KnowledgeEntry
from ._common import governed_view

router = APIRouter(prefix="/documents", tags=["document metadata and versions"])


class VersionCreate(ApiModel):
    version_label: str = Field(min_length=1, max_length=64)
    checksum_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    provider_location: str = Field(min_length=9, max_length=1000)
    size_bytes: int | None = Field(default=None, ge=0)


def document_readable(
    ctx: AppContext,
    principal: Principal,
    doc: DocumentReference,
    parents: Mapping[UUID, KnowledgeEntry],
) -> bool:
    """Readable directly, or through a readable parent knowledge entry (`parents`)."""
    if ctx.authz.can_read(principal, doc):
        return True
    entry = parents.get(doc.knowledge_entry_id) if doc.knowledge_entry_id else None
    return (
        entry is not None
        and doc.deleted_at is None
        and ctx.authz.can_read(principal, entry)
        and ctx.authz.classification_allowed(principal.clearance_code, doc.classification_code)
    )


def _parents(ctx: AppContext, docs: Iterable[DocumentReference]) -> dict[UUID, KnowledgeEntry]:
    return ctx.store.get_governed_many(
        KnowledgeEntry, {d.knowledge_entry_id for d in docs if d.knowledge_entry_id is not None}
    )


def _get(ctx: AppContext, principal: Principal, document_id: UUID) -> DocumentReference:
    doc = ctx.store.get_governed(DocumentReference, document_id)
    if doc is None or not document_readable(ctx, principal, doc, _parents(ctx, [doc])):
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
    # Never list_readable here: documents may be readable through their parent knowledge.
    docs = ctx.store.list_governed(
        DocumentReference, scope=ctx.authz.read_scope(principal, DocumentReference)
    )
    parents = _parents(ctx, docs)
    docs = [d for d in docs if document_readable(ctx, principal, d, parents)]
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
    with ctx.store.transaction():
        doc = _get(ctx, principal, document_id)
        if not ctx.authz.can_write(principal, doc):
            ctx.authz.deny_write(principal, doc, "document_reference")
        if not is_safe_local_location(body.provider_location):
            raise ApiError(
                422,
                "VALIDATION_ERROR",
                "Hanya referensi local:// dengan path sederhana yang didukung pada pengembangan",
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
        ctx.store.insert(version)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="VERSION_REGISTER",
            entity_type="document_version",
            entity_id=version.id,
            detail={"documentReferenceId": str(doc.id)},
        )
    return envelope(serialize(version))
