"""Review-only chunk preview API tests."""

from sunovate_api.store.dataset import sid
from sunovate_api.testing import login, make_client

API = "/api/v1/knowledge/chunk-preview"
DRAFT_API = "/api/v1/knowledge/chunk-drafts"


def _payload() -> dict[str, object]:
    return {
        "documentLabel": "SIMULASI - PMK Lelang SUN",
        "knowledgeType": "REGULATION",
        "extractedText": (
            "Pasal 1\nKetentuan pertama untuk simulasi pemeriksaan.\n\n"
            "Pasal 2\nKetentuan kedua untuk simulasi pemeriksaan."
        ),
        "maxWords": 400,
    }


def test_reviewer_can_preview_without_persisting() -> None:
    client = make_client()
    headers = login(client, "sim.coordinator")
    before_response = client.get(
        "/api/v1/knowledge", params={"pageSize": 100}, headers=headers
    )
    before = before_response.json()["meta"]["total"]
    response = client.post(API, json=_payload(), headers=headers)
    after_response = client.get(
        "/api/v1/knowledge", params={"pageSize": 100}, headers=headers
    )
    after = after_response.json()["meta"]["total"]

    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["persisted"] is False
    assert data["chunkCount"] == 2
    assert [item["sectionLabel"] for item in data["chunks"]] == ["Pasal 1", "Pasal 2"]
    assert before == after


def test_preview_requires_reviewer_permission() -> None:
    client = make_client()
    response = client.post(API, json=_payload(), headers=login(client, "sim.staff.pppsun"))
    assert response.status_code == 403


def test_preview_rejects_short_text() -> None:
    client = make_client()
    payload = _payload()
    payload["extractedText"] = "Terlalu singkat"
    response = client.post(API, json=payload, headers=login(client, "sim.coordinator"))
    assert response.status_code == 422


def test_coordinator_saves_reviewed_preview_as_non_retrievable_draft() -> None:
    client = make_client()
    headers = login(client, "sim.coordinator")
    payload = {
        **_payload(),
        "summary": "Ringkasan simulasi hasil pemeriksaan pembagian dokumen.",
        "classificationCode": "INTERNAL",
        "sharingScope": "TEAM",
        "ownerTeamId": str(sid("team:PSUN")),
    }
    response = client.post(DRAFT_API, json=payload, headers=headers)

    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["lifecycleStatus"] == "DRAFT"
    assert [section["sectionLabel"] for section in data["sections"]] == ["Pasal 1", "Pasal 2"]
    assert data["sourceNote"].startswith("SIMULATED_DATA")

    search = client.get("/api/v1/search", params={"q": "Ketentuan pertama"}, headers=headers)
    assert data["id"] not in {item["knowledgeEntryId"] for item in search.json()["data"]}
    audit = client.get("/api/v1/audit-logs", headers=login(client, "sim.admin")).json()["data"]
    saved_log = next(item for item in audit if item["entityId"] == data["id"])
    assert saved_log["detail"]["chunkCount"] == 2
    assert "content" not in saved_log["detail"]


def test_chunk_draft_requires_all_write_permissions_and_simulated_title() -> None:
    client = make_client()
    payload = {
        **_payload(),
        "summary": "Ringkasan simulasi hasil pemeriksaan pembagian dokumen.",
        "classificationCode": "INTERNAL",
        "sharingScope": "TEAM",
        "ownerTeamId": str(sid("team:AKPSUN")),
    }
    reviewer = client.post(DRAFT_API, json=payload, headers=login(client, "sim.reviewer.akpsun"))
    assert reviewer.status_code == 403

    payload["documentLabel"] = "Dokumen tanpa penanda simulasi"
    invalid = client.post(DRAFT_API, json=payload, headers=login(client, "sim.coordinator"))
    assert invalid.status_code == 422
