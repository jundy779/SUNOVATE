"""Knowledge entries: list, detail, create draft, update draft, submit for review."""

from __future__ import annotations

from hashlib import sha256
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import Field, field_validator

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, invalid_state, permission_denied
from ..core.responses import ApiModel, Pagination, envelope, paginated, serialize
from ..hermes.chunking import chunk_text
from ..hermes.document_extraction import (
    MAX_FILE_BYTES,
    ExtractionRejected,
    extract_simulated_document,
)
from ..hermes.scope_guard import is_instruction_like
from ..hermes.text import terms
from ..store.records import (
    ApprovalRequest,
    DocumentChunk,
    DocumentReference,
    DocumentVersion,
    KnowledgeEntry,
)
from ._common import governed_view, readable_or_404

router = APIRouter(prefix="/knowledge", tags=["knowledge entries"])

KnowledgeType = Literal[
    "REGULATION",
    "POLICY",
    "STUDY",
    "SOP",
    "PLAYBOOK",
    "REPORT",
    "MEETING_MATERIAL",
    "CLOSE_OUT_NOTE",
    "LESSON_LEARNED",
    "TACIT_KNOWLEDGE",
    "DECISION_RECORD",
    "ARCHIVE",
    "REFERENCE",
    "OTHER",
]
LifecycleStatus = Literal["DRAFT", "IN_REVIEW", "PUBLISHED", "SUPERSEDED", "ARCHIVED"]
ClassificationCode = Literal["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"]
SharingScope = Literal["TEAM", "DIRECTORATE"]


class KnowledgeCreate(ApiModel):
    title: str = Field(min_length=5, max_length=255)
    knowledge_type: KnowledgeType
    summary: str = Field(min_length=10, max_length=2000)
    classification_code: ClassificationCode
    sharing_scope: SharingScope = "TEAM"
    owner_team_id: UUID
    tags: list[Annotated[str, Field(min_length=1, max_length=48)]] = Field(
        default_factory=list, max_length=20
    )

    @field_validator("tags", mode="after")
    @classmethod
    def _dedupe_tags(cls, value: list[str]) -> list[str]:
        return _dedupe(value)


def _dedupe(value: list[str]) -> list[str]:
    """Duplicate tags are dropped; first occurrence wins, case-sensitive (ADR-015)."""
    return list(dict.fromkeys(value))


class KnowledgeUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=5, max_length=255)
    summary: str | None = Field(default=None, min_length=10, max_length=2000)
    classification_code: ClassificationCode | None = None
    sharing_scope: SharingScope | None = None
    tags: list[Annotated[str, Field(min_length=1, max_length=48)]] | None = Field(
        default=None, max_length=20
    )

    @field_validator("tags", mode="after")
    @classmethod
    def _dedupe_tags(cls, value: list[str] | None) -> list[str] | None:
        return None if value is None else _dedupe(value)


class KnowledgeSubmit(ApiModel):
    revision: int = Field(ge=1)
    note: str | None = Field(default=None, max_length=1000)


class ChunkPreviewRequest(ApiModel):
    document_label: str = Field(min_length=3, max_length=255)
    knowledge_type: KnowledgeType
    extracted_text: str = Field(min_length=20, max_length=100_000)
    max_words: int = Field(default=400, ge=50, le=800)


class ChunkDraftCreate(ChunkPreviewRequest):
    summary: str = Field(min_length=10, max_length=2000)
    classification_code: ClassificationCode
    sharing_scope: SharingScope = "TEAM"
    owner_team_id: UUID

    @field_validator("document_label")
    @classmethod
    def _simulated_title_only(cls, value: str) -> str:
        title = value.strip()
        if not title.upper().startswith("SIMULASI -"):
            raise ValueError("Nama bahan pengembangan harus diawali 'SIMULASI -'")
        return title


def _chunk_preview_payload(
    *, document_label: str, knowledge_type: str, extracted_text: str, max_words: int
) -> dict[str, Any]:
    chunks = chunk_text(
        extracted_text,
        knowledge_type,
        document_label=document_label,
        max_words=max_words,
    )
    return {
        "documentLabel": document_label,
        "knowledgeType": knowledge_type,
        "chunkCount": len(chunks),
        "totalWords": sum(chunk.word_count for chunk in chunks),
        "persisted": False,
        "chunks": [
            {
                "index": chunk.index,
                "sectionLabel": chunk.section_label,
                "content": chunk.content,
                "wordCount": chunk.word_count,
                "contentHash": chunk.content_hash,
            }
            for chunk in chunks
        ],
    }


def _view(ctx: AppContext, entry: KnowledgeEntry, *, detail: bool = False) -> dict[str, Any]:
    view = governed_view(ctx, entry)
    if detail:
        docs = ctx.store.list_governed(
            DocumentReference, where={"knowledge_entry_id": entry.id, "deleted_at": None}
        )
        view["documents"] = [serialize(d, exclude=("deleted_at",)) for d in docs]
        view["sections"] = [
            {"index": c.chunk_index, "sectionLabel": c.section_label, "content": c.content}
            for c in ctx.store.chunks_of_entry(entry.id)
        ]
    return view


def _check_target(
    ctx: AppContext, principal: Principal, team_id: UUID, classification: str
) -> None:
    if ctx.store.team(team_id) is None:
        raise ApiError(422, "VALIDATION_ERROR", "Tim pemilik tidak dikenal")
    if not ctx.authz.team_in_scope(principal, team_id):
        raise permission_denied("Anda hanya dapat membuat pengetahuan untuk tim Anda")
    if not ctx.authz.classification_allowed(principal.clearance_code, classification):
        raise permission_denied("Klasifikasi melebihi batas akses informasi Anda")


@router.get("")
def list_knowledge(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:read", resource="knowledge"))],
    pagination: Annotated[Pagination, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    status: Annotated[LifecycleStatus | None, Query()] = None,
    knowledge_type: Annotated[KnowledgeType | None, Query(alias="type")] = None,
    team_code: Annotated[str | None, Query(alias="teamCode", max_length=32)] = None,
) -> dict[str, Any]:
    items = ctx.authz.list_readable(principal, KnowledgeEntry)
    if q:
        needle = q.lower()
        items = [e for e in items if needle in f"{e.title} {e.summary}".lower()]
    if status:
        items = [e for e in items if e.lifecycle_status == status]
    if knowledge_type:
        items = [e for e in items if e.knowledge_type == knowledge_type]
    if team_code:
        items = [e for e in items if ctx.store.team_code(e.owner_team_id) == team_code]
    items.sort(key=lambda e: e.updated_at, reverse=True)
    page, meta = paginated(items, pagination)
    return envelope([_view(ctx, e) for e in page], **meta)


@router.post("/chunk-preview")
def preview_chunks(
    body: ChunkPreviewRequest,
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("knowledge:review", resource="knowledge_chunk_preview"))
    ],
) -> dict[str, Any]:
    """Preview deterministic text sections without persisting source text or chunks."""
    del ctx, principal
    return envelope(
        _chunk_preview_payload(
            document_label=body.document_label,
            knowledge_type=body.knowledge_type,
            extracted_text=body.extracted_text,
            max_words=body.max_words,
        ),
        previewMode=True,
    )


@router.post("/extract-preview")
async def extract_preview(
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("knowledge:review", resource="knowledge_extract_preview"))
    ],
    document_label: Annotated[str, Form(alias="documentLabel", min_length=3, max_length=255)],
    knowledge_type: Annotated[KnowledgeType, Form(alias="knowledgeType")],
    source_file: Annotated[UploadFile, File(alias="sourceFile")],
    max_words: Annotated[int, Form(alias="maxWords", ge=50, le=800)] = 400,
) -> dict[str, Any]:
    """Extract and chunk a bounded simulated file entirely in memory."""
    if not document_label.strip().upper().startswith("SIMULASI -"):
        raise ApiError(422, "SIMULATED_FILE_REQUIRED", "Nama bahan harus diawali 'SIMULASI -'")
    source_filename = source_file.filename or ""
    source_content_type = source_file.content_type
    payload = await source_file.read(MAX_FILE_BYTES + 1)
    await source_file.close()
    try:
        extracted = extract_simulated_document(
            filename=source_filename,
            content_type=source_content_type,
            payload=payload,
        )
        if is_instruction_like(extracted.text):
            raise ExtractionRejected(
                "Isi berkas memerlukan pemeriksaan keamanan oleh petugas berwenang",
                extraction_status="QUARANTINED",
                reason_code="PROMPT_INJECTION_SUSPECTED",
            )
    except ExtractionRejected as exc:
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="EXTRACT_PREVIEW_REJECTED",
            entity_type="simulated_document",
            detail={
                "extractionStatus": exc.extraction_status,
                "reasonCode": exc.reason_code,
                "sizeBytes": len(payload),
            },
        )
        raise ApiError(
            422,
            "UNSAFE_SIMULATED_FILE",
            str(exc),
            {
                "extractionStatus": exc.extraction_status,
                "reasonCode": exc.reason_code,
                "persisted": False,
            },
        ) from None

    result = _chunk_preview_payload(
        document_label=document_label.strip(),
        knowledge_type=knowledge_type,
        extracted_text=extracted.text,
        max_words=max_words,
    )
    result["extractedText"] = extracted.text
    result["extraction"] = {
        "format": extracted.extension.removeprefix(".").upper(),
        "sizeBytes": extracted.size_bytes,
        "checksum": extracted.checksum_sha256,
        "pageCount": extracted.page_count,
        "paragraphCount": extracted.paragraph_count,
        "sheetCount": extracted.sheet_count,
        "status": "EXTRACTED",
        "nextStep": "HUMAN_REVIEW",
        "statusHistory": ["PENDING", "EXTRACTED"],
        "persisted": False,
    }
    ctx.store.audit(
        actor_user_id=principal.user_id,
        action="EXTRACT_PREVIEW",
        entity_type="simulated_document",
        detail={
            "format": extracted.extension.removeprefix("."),
            "sizeBytes": extracted.size_bytes,
            "extractedCharacters": len(extracted.text),
            "chunkCount": result["chunkCount"],
            "extractionStatus": "EXTRACTED",
        },
    )
    return envelope(result, previewMode=True)


@router.post("/chunk-drafts", status_code=201)
def create_chunk_draft(
    body: ChunkDraftCreate,
    ctx: Ctx,
    principal: Annotated[
        Principal,
        Depends(
            require(
                "knowledge:review",
                "knowledge:create",
                "document:create",
                "document:version",
                resource="knowledge_chunk_draft",
            )
        ),
    ],
) -> dict[str, Any]:
    """Persist a reviewed SIMULATED_DATA preview as a non-retrievable draft."""
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    if is_instruction_like(body.extracted_text):
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="KNOWLEDGE_DRAFT_QUARANTINED",
            entity_type="simulated_document",
            detail={
                "extractionStatus": "QUARANTINED",
                "reasonCode": "PROMPT_INJECTION_SUSPECTED",
            },
        )
        raise ApiError(
            422,
            "DOCUMENT_REQUIRES_SECURITY_REVIEW",
            "Isi bahan memerlukan pemeriksaan keamanan oleh petugas berwenang",
            {
                "extractionStatus": "QUARANTINED",
                "reasonCode": "PROMPT_INJECTION_SUSPECTED",
                "persisted": False,
            },
        )
    chunks = chunk_text(
        body.extracted_text,
        body.knowledge_type,
        document_label=body.document_label,
        max_words=body.max_words,
    )
    checksum = sha256(body.extracted_text.encode("utf-8")).hexdigest()
    entry = KnowledgeEntry(
        title=body.document_label,
        knowledge_type=body.knowledge_type,
        summary=body.summary,
        classification_code=body.classification_code,
        sharing_scope=body.sharing_scope,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        source_note="SIMULATED_DATA - draf hasil pemeriksaan pembagian isi",
        tags=["simulasi", "hasil-pemeriksaan"],
    )
    document = DocumentReference(
        knowledge_entry_id=entry.id,
        title=body.document_label,
        provider_location=f"local://simulated/chunk-drafts/{entry.id}.txt",
        mime_type="text/plain",
        owner_team_id=body.owner_team_id,
        classification_code=body.classification_code,
        owner_user_id=principal.user_id,
        created_by=principal.user_id,
        updated_by=principal.user_id,
    )
    version = DocumentVersion(
        document_reference_id=document.id,
        version_label="v0.1",
        checksum_sha256=checksum,
        size_bytes=len(body.extracted_text.encode("utf-8")),
        provider_location=document.provider_location,
        extraction_status="EXTRACTED",
        created_by=principal.user_id,
    )
    stored_chunks = [
        DocumentChunk(
            document_version_id=version.id,
            knowledge_entry_id=entry.id,
            chunk_index=chunk.index,
            section_label=chunk.section_label,
            content=chunk.content,
        )
        for chunk in chunks
    ]
    with ctx.store.transaction():
        ctx.store.insert(entry)
        ctx.store.insert(document)
        ctx.store.insert(version)
        for chunk in stored_chunks:
            ctx.store.insert(chunk)
        ctx.store.update_revisioned(
            DocumentReference,
            document.id,
            expected_revision=1,
            changes={"current_version_id": version.id},
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="knowledge_entry",
            entity_id=entry.id,
            detail={
                "source": "reviewed_chunk_preview",
                "chunkCount": len(stored_chunks),
                "documentReferenceId": str(document.id),
                "documentVersionId": str(version.id),
            },
        )
    return envelope(_view(ctx, entry, detail=True), persisted=True)


@router.get("/drafts/search")
def search_drafts(
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("knowledge:read", resource="knowledge_draft_search"))
    ],
    pagination: Annotated[Pagination, Depends()],
    q: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    team_code: Annotated[str | None, Query(alias="teamCode", max_length=32)] = None,
) -> dict[str, Any]:
    """Search drafts owned by the caller or reviewable within their authorized scope."""
    may_review = principal.has("knowledge:review")
    may_own = "knowledge_owner" in principal.role_codes
    if not (may_review or may_own):
        ctx.store.audit_denial(
            actor_user_id=principal.user_id,
            action="ACCESS_DENIED",
            entity_type="knowledge_draft_search",
            detail={"reason": "not_owner_or_reviewer"},
        )
        raise permission_denied("Pencarian draf hanya tersedia bagi pemilik dan pemeriksa")

    authorized_entries = ctx.authz.list_readable(
        principal, KnowledgeEntry, where={"lifecycle_status": "DRAFT"}
    )
    drafts = [
        entry
        for entry in authorized_entries
        if entry.owner_user_id == principal.user_id
        or (may_review and ctx.authz.team_in_scope(principal, entry.owner_team_id))
    ]
    if team_code:
        drafts = [e for e in drafts if ctx.store.team_code(e.owner_team_id) == team_code]

    query_terms = terms(q or "")
    draft_scope = ctx.authz.read_scope(principal, KnowledgeEntry)
    search_candidates = (
        ctx.store.text_search_candidates(
            [entry.id for entry in drafts],
            q,
            classification_codes=draft_scope.classification_codes,
        )
        if q
        else None
    )
    hits: list[dict[str, Any]] = []
    for entry in drafts:
        if search_candidates is not None and entry.id not in search_candidates.entry_ids:
            continue
        entry_terms = terms(f"{entry.title} {entry.summary}")
        best_section: str | None = None
        best_snippet = entry.summary
        best = len(query_terms & entry_terms) if query_terms else 0
        entry_chunks = (
            search_candidates.chunks_by_entry.get(entry.id, [])
            if search_candidates is not None
            else []
        )
        for chunk in entry_chunks:
            matched = len(query_terms & (entry_terms | terms(chunk.content))) if query_terms else 0
            if matched > best:
                best_section, best_snippet, best = chunk.section_label, chunk.content, matched
        if query_terms and best == 0:
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
                "score": round(best / max(len(query_terms), 1), 3) if query_terms else 0.0,
                "updatedAt": entry.updated_at,
                "accessReason": "OWNER" if entry.owner_user_id == principal.user_id else "REVIEWER",
            }
        )
    if query_terms:
        hits.sort(key=lambda hit: (-float(hit["score"]), str(hit["title"])))
    else:
        hits.sort(key=lambda hit: str(hit["updatedAt"]), reverse=True)

    ctx.store.audit(
        actor_user_id=principal.user_id,
        action="SEARCH",
        entity_type="knowledge_draft_search",
        detail={"queryLength": len(q or ""), "resultCount": len(hits)},
    )
    page, meta = paginated(hits, pagination)
    mode = (
        "draft_postgres_fts"
        if q and ctx.data_backend == "postgres"
        else "draft_lexical"
    )
    return envelope(page, **meta, mode=mode)


@router.get("/{entry_id}")
def get_knowledge(
    entry_id: UUID,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:read", resource="knowledge"))],
) -> dict[str, Any]:
    entry = readable_or_404(ctx, principal, KnowledgeEntry, entry_id, "Knowledge")
    return envelope(_view(ctx, entry, detail=True))


@router.post("", status_code=201)
def create_knowledge(
    body: KnowledgeCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:create", resource="knowledge"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    entry = KnowledgeEntry(
        title=body.title,
        knowledge_type=body.knowledge_type,
        summary=body.summary,
        classification_code=body.classification_code,
        sharing_scope=body.sharing_scope,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        tags=body.tags,
        data_origin="USER_ENTERED",
    )
    with ctx.store.transaction():
        ctx.store.insert(entry)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="knowledge_entry",
            entity_id=entry.id,
        )
    return envelope(_view(ctx, entry))


@router.patch("/{entry_id}")
def update_knowledge(
    entry_id: UUID,
    body: KnowledgeUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:update", resource="knowledge"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        entry = readable_or_404(ctx, principal, KnowledgeEntry, entry_id, "Knowledge")
        if not ctx.authz.can_write(principal, entry):
            ctx.authz.deny_write(principal, entry, "knowledge_entry")
        if entry.lifecycle_status != "DRAFT":
            raise invalid_state("Hanya pengetahuan berstatus draf yang dapat diubah")
        if body.classification_code:
            _check_target(ctx, principal, entry.owner_team_id, body.classification_code)
        # Explicit null means "unchanged" (ADR-015).
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        updated = ctx.store.update_revisioned(
            KnowledgeEntry,
            entry.id,
            expected_revision=body.revision,
            changes=changes,
            actor_id=principal.user_id,
            expected_state={"lifecycle_status": "DRAFT"},
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="knowledge_entry",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(_view(ctx, updated))


@router.post("/{entry_id}/submit")
def submit_knowledge(
    entry_id: UUID,
    body: KnowledgeSubmit,
    ctx: Ctx,
    principal: Annotated[
        Principal,
        Depends(require("knowledge:submit", "approval:request", resource="knowledge")),
    ],
) -> dict[str, Any]:
    with ctx.store.transaction():
        entry = readable_or_404(ctx, principal, KnowledgeEntry, entry_id, "Knowledge")
        if not ctx.authz.can_write(principal, entry):
            ctx.authz.deny_write(principal, entry, "knowledge_entry")
        if entry.lifecycle_status != "DRAFT":
            raise invalid_state("Hanya pengetahuan berstatus draf yang dapat diajukan")
        updated = ctx.store.update_revisioned(
            KnowledgeEntry,
            entry.id,
            expected_revision=body.revision,
            changes={"lifecycle_status": "IN_REVIEW"},
            actor_id=principal.user_id,
            expected_state={"lifecycle_status": "DRAFT"},
        )
        request = ApprovalRequest(
            request_type="KNOWLEDGE_PUBLICATION",
            target_entity_type="knowledge_entry",
            target_entity_id=updated.id,
            requested_by=principal.user_id,
            owner_team_id=updated.owner_team_id,
            owner_user_id=principal.user_id,
            classification_code=updated.classification_code,
            created_by=principal.user_id,
            payload={"knowledgeRevision": updated.revision, "note": body.note},
            data_origin="USER_ENTERED",
        )
        ctx.store.insert(request)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="SUBMIT",
            entity_type="knowledge_entry",
            entity_id=updated.id,
            detail={"approvalRequestId": str(request.id)},
        )
    return envelope({"knowledge": _view(ctx, updated), "approvalRequestId": request.id})
