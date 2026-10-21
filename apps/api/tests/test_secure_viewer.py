"""RAHASIA view-only viewer and envelope encryption (ADR-020). SIMULATED_DATA only."""

from uuid import uuid4

import pytest

from sunovate_api.secure.crypto import (
    DecryptionError,
    LocalDevelopmentKeyProvider,
    open_sealed,
    seal,
    shred,
)
from sunovate_api.secure.vault import PageRateLimiter
from sunovate_api.testing import login, make_client

API = "/api/v1/secure-documents"
MARKER = "KODE-UJI-RAHASIA-7781"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


# Envelope encryption ---------------------------------------------------------


def test_sealed_content_round_trips_and_hides_plaintext() -> None:
    provider = LocalDevelopmentKeyProvider()
    sealed = seal(MARKER.encode(), provider, associated_data=b"doc:0")
    assert MARKER.encode() not in sealed.ciphertext
    assert sealed.wrapped_key is not None and len(sealed.wrapped_key) > 32
    assert open_sealed(sealed, provider, associated_data=b"doc:0") == MARKER.encode()


def test_wrong_document_binding_or_tampering_is_rejected() -> None:
    provider = LocalDevelopmentKeyProvider()
    sealed = seal(b"isi rahasia", provider, associated_data=b"doc:0")
    with pytest.raises(DecryptionError):
        open_sealed(sealed, provider, associated_data=b"doc:1")
    tampered = type(sealed)(
        key_id=sealed.key_id,
        wrapped_key=sealed.wrapped_key,
        nonce=sealed.nonce,
        ciphertext=bytes([sealed.ciphertext[0] ^ 1]) + sealed.ciphertext[1:],
    )
    with pytest.raises(DecryptionError):
        open_sealed(tampered, provider, associated_data=b"doc:0")


def test_other_key_provider_cannot_open_content() -> None:
    sealed = seal(b"isi rahasia", LocalDevelopmentKeyProvider(), associated_data=b"doc:0")
    with pytest.raises(DecryptionError):
        open_sealed(sealed, LocalDevelopmentKeyProvider(), associated_data=b"doc:0")


def test_crypto_shredding_makes_content_unrecoverable() -> None:
    provider = LocalDevelopmentKeyProvider()
    sealed = shred(seal(b"isi rahasia", provider, associated_data=b"doc:0"))
    assert sealed.wrapped_key is None
    with pytest.raises(DecryptionError):
        open_sealed(sealed, provider, associated_data=b"doc:0")


# Viewer access ---------------------------------------------------------------


def _doc_id(client, headers):  # type: ignore[no-untyped-def]
    rows = client.get(API, headers=headers).json()["data"]
    assert len(rows) == 1
    return rows[0]["id"]


def test_only_granted_readers_see_the_document() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    rows = client.get(API, headers=coordinator).json()["data"]
    assert [row["handling"] for row in rows] == ["VIEW_ONLY"]
    assert rows[0]["pageCount"] == 2
    assert MARKER not in str(rows)

    for user in ("sim.staff.pppsun", "sim.auditor", "sim.admin"):
        assert client.get(API, headers=login(client, user)).json()["data"] == []


def test_granted_reader_receives_watermarked_png_without_text() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    doc_id = _doc_id(client, coordinator)

    response = client.get(f"{API}/{doc_id}/pages/1", headers=coordinator)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(PNG_SIGNATURE)
    assert MARKER.encode() not in response.content
    assert "no-store" in response.headers["cache-control"]
    assert response.headers["content-disposition"] == "inline"
    assert response.headers["x-content-type-options"] == "nosniff"

    logs = client.get(
        "/api/v1/audit-logs?action=SECURE_PAGE_VIEW", headers=login(client, "sim.admin")
    ).json()["data"]
    assert any(log["outcome"] == "SUCCESS" and log["entityId"] == doc_id for log in logs)


def test_ungranted_reader_gets_not_found_and_attempt_is_audited() -> None:
    client = make_client()
    doc_id = _doc_id(client, login(client, "sim.coordinator"))
    staff = login(client, "sim.staff.pppsun")

    assert client.get(f"{API}/{doc_id}", headers=staff).status_code == 404
    assert client.get(f"{API}/{doc_id}/pages/1", headers=staff).status_code == 404
    assert client.get(f"{API}/{uuid4()}/pages/1", headers=staff).status_code == 404

    logs = client.get(
        "/api/v1/audit-logs?action=SECURE_PAGE_VIEW", headers=login(client, "sim.admin")
    ).json()["data"]
    assert any(log["outcome"] == "DENIED" and log["entityId"] == doc_id for log in logs)


def test_unauthenticated_requests_are_rejected() -> None:
    client = make_client()
    doc_id = _doc_id(client, login(client, "sim.coordinator"))
    assert client.get(API).status_code == 401
    assert client.get(f"{API}/{doc_id}/pages/1").status_code == 401


def test_page_outside_document_is_not_found() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    doc_id = _doc_id(client, coordinator)
    assert client.get(f"{API}/{doc_id}/pages/3", headers=coordinator).status_code == 404
    assert client.get(f"{API}/{doc_id}/pages/0", headers=coordinator).status_code == 422


def test_no_route_exposes_file_text_or_download() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    doc_id = _doc_id(client, coordinator)
    for suffix in ("download", "file", "text", "raw", "content", "pages/1/text"):
        response = client.get(f"{API}/{doc_id}/{suffix}", headers=coordinator)
        assert response.status_code in {404, 405, 422}, suffix
    paths = client.app.openapi()["paths"]
    secure_routes = sorted(path for path in paths if path.startswith(API))
    assert all(set(paths[path]) == {"get"} for path in secure_routes)
    assert secure_routes == [
        API,
        f"{API}/{{document_id}}",
        f"{API}/{{document_id}}/pages/{{page_number}}",
    ]


def test_bulk_page_requests_are_rate_limited() -> None:
    client = make_client()
    client.app.state.runtime.vault.limiter = PageRateLimiter(limit=2, window_seconds=60)
    coordinator = login(client, "sim.coordinator")
    doc_id = _doc_id(client, coordinator)

    assert client.get(f"{API}/{doc_id}/pages/1", headers=coordinator).status_code == 200
    assert client.get(f"{API}/{doc_id}/pages/2", headers=coordinator).status_code == 200
    blocked = client.get(f"{API}/{doc_id}/pages/1", headers=coordinator)
    assert blocked.status_code == 429
    assert blocked.json()["code"] == "SECURE_VIEW_RATE_LIMITED"
    assert int(blocked.headers["retry-after"]) >= 1


def test_rahasia_content_never_reaches_search_or_savi() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    hits = client.get("/api/v1/search", params={"q": MARKER}, headers=coordinator).json()["data"]
    assert MARKER not in str(hits)
    answer = client.post(
        "/api/v1/hermes/query", json={"question": f"Apa isi dokumen {MARKER}?"}, headers=coordinator
    )
    assert answer.status_code == 200
    assert MARKER not in answer.text.replace(f"Apa isi dokumen {MARKER}?", "")
