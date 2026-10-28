"""A document classified above its knowledge entry never reaches readers below it (AUD-02).

SIMULATED_DATA only. The store is built in the test so the mismatched document can be added
without a production write path (every API write keeps document and entry classification equal).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from sunovate_api.context import build_runtime
from sunovate_api.main import create_app
from sunovate_api.store.dataset import sid
from sunovate_api.store.records import DocumentChunk, DocumentReference, DocumentVersion
from sunovate_api.store.simulated import SimulatedBackend, SimulatedStore
from sunovate_api.testing import REFERENCE_DATE, login, make_settings

ENTRY_ID = sid("knowledge:K1")  # PSUN, INTERNAL, shared with the directorate, published
MARKER = "PENANDA-UJI-DOKUMEN-TERBATAS"
HIDDEN_TITLE = "SIMULASI - Lampiran terbatas"


def _client_with_restricted_attachment() -> TestClient:
    store = SimulatedStore()
    owner = sid("user:sim.lead.psun")
    document = DocumentReference(
        knowledge_entry_id=ENTRY_ID,
        title=HIDDEN_TITLE,
        provider_location="local://simulated/lampiran-terbatas.txt",
        mime_type="text/plain",
        owner_team_id=sid("team:PSUN"),
        classification_code="RESTRICTED",
        owner_user_id=owner,
        created_by=owner,
        updated_by=owner,
    )
    version = DocumentVersion(
        document_reference_id=document.id,
        version_label="v0.1",
        checksum_sha256="0" * 64,
        size_bytes=len(MARKER),
        provider_location=document.provider_location,
        extraction_status="EXTRACTED",
        created_by=owner,
    )
    document.current_version_id = version.id  # chunks are read from the current version only
    chunk = DocumentChunk(
        document_version_id=version.id,
        knowledge_entry_id=ENTRY_ID,
        chunk_index=99,
        section_label="Lampiran",
        content=MARKER,
    )
    with store.transaction():
        store.insert(document)
        store.insert(version)
        store.insert(chunk)
    settings = make_settings(data_backend="simulated")
    runtime = build_runtime(
        settings, backend=SimulatedBackend(store), clock=lambda: REFERENCE_DATE
    )
    return TestClient(create_app(settings, runtime))


def test_detail_hides_documents_and_text_above_the_reader_clearance() -> None:
    client = _client_with_restricted_attachment()
    response = client.get(
        f"/api/v1/knowledge/{ENTRY_ID}", headers=login(client, "sim.staff.pppsun")
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert HIDDEN_TITLE not in [doc["title"] for doc in body["documents"]]
    assert body["documents"], "the entry's own INTERNAL document stays visible"
    assert MARKER not in response.text
    assert body["sections"], "the entry's own INTERNAL text stays visible"


def test_detail_shows_the_document_to_readers_with_enough_clearance() -> None:
    client = _client_with_restricted_attachment()
    response = client.get(f"/api/v1/knowledge/{ENTRY_ID}", headers=login(client, "sim.lead.psun"))
    assert response.status_code == 200
    body = response.json()["data"]
    assert HIDDEN_TITLE in [doc["title"] for doc in body["documents"]]
    assert MARKER in [section["content"] for section in body["sections"]]


def test_search_never_uses_text_from_a_document_above_the_reader_clearance() -> None:
    client = _client_with_restricted_attachment()
    staff = login(client, "sim.staff.pppsun")
    response = client.get("/api/v1/search", params={"q": MARKER}, headers=staff)
    assert response.status_code == 200
    assert MARKER not in response.text

    lead = login(client, "sim.lead.psun")
    allowed = client.get("/api/v1/search", params={"q": MARKER}, headers=lead)
    assert MARKER in allowed.text, "readers with enough clearance still find the text"


def test_savi_never_cites_text_from_a_document_above_the_reader_clearance() -> None:
    client = _client_with_restricted_attachment()
    staff = login(client, "sim.staff.pppsun")
    question = f"Apa isi lampiran SUN {MARKER}?"
    response = client.post("/api/v1/hermes/query", json={"question": question}, headers=staff)
    assert response.status_code == 200
    data = response.json()["data"]
    assert MARKER not in (data.get("answer") or "")
    assert all(MARKER not in str(citation) for citation in data["citations"])
