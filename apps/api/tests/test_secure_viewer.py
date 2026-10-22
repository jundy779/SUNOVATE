"""RAHASIA view-only viewer and envelope encryption (ADR-020). SIMULATED_DATA only."""

from uuid import uuid4

import pytest

from sunovate_api.authz.catalog import ROLE_PERMISSIONS
from sunovate_api.modules.secure_viewer import MANAGE_ALL, MANAGE_TEAM
from sunovate_api.secure.crypto import (
    DecryptionError,
    LocalDevelopmentKeyProvider,
    open_sealed,
    seal,
    shred,
)
from sunovate_api.secure.vault import NoticeRegistry, PageRateLimiter, secure_document_id
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


def _doc_id(client, headers, *, accept: bool = True):  # type: ignore[no-untyped-def]
    rows = client.get(API, headers=headers).json()["data"]
    assert len(rows) == 1
    if accept:
        response = client.post(f"{API}/{rows[0]['id']}/acknowledgements", headers=headers)
        assert response.status_code == 201, response.text
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
    methods = {path: set(paths[path]) for path in paths if path.startswith(API)}
    assert methods == {
        API: {"get"},
        f"{API}/manageable": {"get"},
        f"{API}/{{document_id}}": {"get"},
        f"{API}/{{document_id}}/acknowledgements": {"post"},
        f"{API}/{{document_id}}/readers": {"get", "post"},
        f"{API}/{{document_id}}/readers/{{email}}": {"delete"},
        f"{API}/{{document_id}}/pages/{{page_number}}": {"get"},
    }


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


def test_pages_stay_locked_until_notice_is_accepted() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    doc_id = _doc_id(client, coordinator, accept=False)
    locked = client.get(f"{API}/{doc_id}/pages/1", headers=coordinator)
    assert locked.status_code == 428
    assert locked.json()["code"] == "SECURE_NOTICE_REQUIRED"

    assert client.post(f"{API}/{doc_id}/acknowledgements", headers=coordinator).status_code == 201
    assert client.get(f"{API}/{doc_id}/pages/1", headers=coordinator).status_code == 200
    logs = client.get(
        "/api/v1/audit-logs?action=SECURE_NOTICE_ACCEPTED", headers=login(client, "sim.admin")
    ).json()["data"]
    assert any(log["entityId"] == doc_id for log in logs)


def test_notice_acceptance_expires_and_is_per_reader() -> None:
    clock = [0.0]
    client = make_client()
    client.app.state.runtime.vault.notices = NoticeRegistry(ttl_seconds=60, clock=lambda: clock[0])
    coordinator = login(client, "sim.coordinator")
    lead = login(client, "sim.lead.psun")
    doc_id = _doc_id(client, coordinator)

    assert client.get(f"{API}/{doc_id}/pages/1", headers=coordinator).status_code == 200
    assert client.get(f"{API}/{doc_id}/pages/1", headers=lead).status_code == 428
    clock[0] = 61.0
    assert client.get(f"{API}/{doc_id}/pages/1", headers=coordinator).status_code == 428


def test_ungranted_reader_cannot_accept_notice() -> None:
    client = make_client()
    doc_id = _doc_id(client, login(client, "sim.coordinator"))
    staff = login(client, "sim.staff.pppsun")
    assert client.post(f"{API}/{doc_id}/acknowledgements", headers=staff).status_code == 404


# Access management (DEC-20261021-02: Kasubdit PMP for all teams, Ketua Tim for own team) -

PPSUN_DOC = str(secure_document_id("simulasi-rahasia-pedoman-penilaian"))
PSUN_DOC = str(secure_document_id("simulasi-rahasia-catatan-regulasi"))


def _manageable(client, user):  # type: ignore[no-untyped-def]
    rows = client.get(f"{API}/manageable", headers=login(client, user)).json()["data"]
    return {row["ownerTeamCode"]: row["id"] for row in rows}


def test_only_kasubdit_pmp_and_owning_team_lead_can_manage_access() -> None:
    client = make_client()
    assert _manageable(client, "sim.coordinator") == {"PPSUN": PPSUN_DOC, "PSUN": PSUN_DOC}
    assert _manageable(client, "sim.lead.psun") == {"PSUN": PSUN_DOC}
    for user in ("sim.staff.pppsun", "sim.owner.ppsun", "sim.auditor", "sim.admin"):
        assert _manageable(client, user) == {}, user


def test_authority_comes_from_the_permission_catalog() -> None:
    def holders(permission: str) -> set[str]:
        return {role for role, perms in ROLE_PERMISSIONS.items() if permission in perms}

    assert holders(MANAGE_TEAM) == {"team_lead"}
    assert holders(MANAGE_ALL) == {"knowledge_coordinator"}


def test_team_lead_cannot_manage_another_teams_document() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    assert client.get(f"{API}/{PPSUN_DOC}/readers", headers=lead).status_code == 404
    denied = client.post(
        f"{API}/{PPSUN_DOC}/readers", json={"email": "sim.auditor@sunovate.local"}, headers=lead
    )
    assert denied.status_code == 404
    logs = client.get(
        "/api/v1/audit-logs?action=SECURE_ACCESS_GRANTED", headers=login(client, "sim.admin")
    ).json()["data"]
    assert any(log["outcome"] == "DENIED" and log["entityId"] == PPSUN_DOC for log in logs)


def test_team_lead_grants_reader_from_another_team() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    auditor = login(client, "sim.auditor")
    assert client.get(API, headers=auditor).json()["data"] == []

    granted = client.post(
        f"{API}/{PSUN_DOC}/readers", json={"email": "SIM.Auditor@sunovate.local"}, headers=lead
    )
    assert granted.status_code == 201
    readers = client.get(f"{API}/{PSUN_DOC}/readers", headers=lead).json()["data"]
    assert {"email": "sim.auditor@sunovate.local"} in readers
    assert [row["id"] for row in client.get(API, headers=auditor).json()["data"]] == [PSUN_DOC]

    logs = client.get(
        "/api/v1/audit-logs?action=SECURE_ACCESS_GRANTED", headers=login(client, "sim.admin")
    ).json()["data"]
    assert any(log["outcome"] == "SUCCESS" and log["entityId"] == PSUN_DOC for log in logs)


def test_grant_rejects_unknown_users_and_low_clearance() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    unknown = client.post(
        f"{API}/{PSUN_DOC}/readers", json={"email": "orang.luar@contoh.local"}, headers=lead
    )
    assert unknown.status_code == 422
    assert unknown.json()["code"] == "READER_NOT_FOUND"
    low = client.post(
        f"{API}/{PSUN_DOC}/readers",
        json={"email": "sim.staff.pppsun@sunovate.local"},
        headers=lead,
    )
    assert low.status_code == 422
    assert low.json()["code"] == "READER_CLEARANCE_TOO_LOW"


def test_revoking_access_closes_the_viewer_immediately() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    coordinator = login(client, "sim.coordinator")
    grant = {"email": "sim.coordinator@sunovate.local"}
    assert client.post(f"{API}/{PSUN_DOC}/readers", json=grant, headers=lead).status_code == 201
    assert client.post(f"{API}/{PSUN_DOC}/acknowledgements", headers=coordinator).status_code == 201
    assert client.get(f"{API}/{PSUN_DOC}/pages/1", headers=coordinator).status_code == 200

    reader_url = f"{API}/{PSUN_DOC}/readers/sim.coordinator@sunovate.local"
    assert client.delete(reader_url, headers=lead).status_code == 200
    assert client.get(f"{API}/{PSUN_DOC}/pages/1", headers=coordinator).status_code == 404
    assert client.delete(reader_url, headers=lead).status_code == 404

    assert client.post(f"{API}/{PSUN_DOC}/readers", json=grant, headers=lead).status_code == 201
    assert client.get(f"{API}/{PSUN_DOC}/pages/1", headers=coordinator).status_code == 428


def test_kasubdit_pmp_manages_any_teams_document() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    grant = {"email": "sim.auditor@sunovate.local"}
    granted = client.post(f"{API}/{PSUN_DOC}/readers", json=grant, headers=coordinator)
    assert granted.status_code == 201
    readers = client.get(f"{API}/{PSUN_DOC}/readers", headers=login(client, "sim.lead.psun"))
    assert {"email": "sim.auditor@sunovate.local"} in readers.json()["data"]
    reader_url = f"{API}/{PPSUN_DOC}/readers/sim.lead.psun@sunovate.local"
    assert client.delete(reader_url, headers=coordinator).status_code == 200
