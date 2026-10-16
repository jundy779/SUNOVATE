"""Review-only chunk preview API tests."""

from sunovate_api.store.dataset import sid
from sunovate_api.testing import login, make_client

API = "/api/v1/knowledge/chunk-preview"
DRAFT_API = "/api/v1/knowledge/chunk-drafts"
EXTRACT_API = "/api/v1/knowledge/extract-preview"


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


def test_draft_search_finds_chunk_content_for_authorized_reviewer_only() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    payload = {
        **_payload(),
        "summary": "Ringkasan simulasi yang tidak memuat istilah pencarian khusus.",
        "classificationCode": "INTERNAL",
        "sharingScope": "TEAM",
        "ownerTeamId": str(sid("team:PSUN")),
    }
    draft = client.post(DRAFT_API, json=payload, headers=coordinator).json()["data"]

    reviewer = client.get(
        "/api/v1/knowledge/drafts/search",
        params={"q": "Ketentuan kedua"},
        headers=login(client, "sim.lead.psun"),
    )
    assert reviewer.status_code == 200, reviewer.text
    hit = next(item for item in reviewer.json()["data"] if item["knowledgeEntryId"] == draft["id"])
    assert hit["accessReason"] == "REVIEWER"
    assert hit["sectionLabel"] == "Pasal 2"

    other_team = client.get(
        "/api/v1/knowledge/drafts/search",
        params={"q": "Ketentuan kedua"},
        headers=login(client, "sim.staff.pppsun"),
    )
    assert other_team.status_code == 403


def test_draft_search_requires_owner_or_reviewer_role() -> None:
    client = make_client()
    response = client.get(
        "/api/v1/knowledge/drafts/search",
        headers=login(client, "sim.readonly.dhtv"),
    )
    assert response.status_code == 403


def test_reviewer_extracts_simulated_text_file_without_persisting_source() -> None:
    client = make_client()
    reviewer = login(client, "sim.coordinator")
    before = client.get("/api/v1/knowledge", params={"pageSize": 100}, headers=reviewer).json()[
        "meta"
    ]["total"]

    response = client.post(
        EXTRACT_API,
        headers=reviewer,
        data={
            "documentLabel": "SIMULASI - Hasil pembacaan berkas",
            "knowledgeType": "REGULATION",
            "maxWords": "400",
        },
        files={
            "sourceFile": (
                "SIMULASI-contoh.txt",
                b"Pasal 1\nKetentuan simulasi untuk pemeriksaan berkas yang aman.\n\n"
                b"Pasal 2\nTahap berikutnya wajib diperiksa manusia sebelum diterbitkan.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["extraction"]["format"] == "TXT"
    assert data["extraction"]["status"] == "EXTRACTED"
    assert data["extraction"]["nextStep"] == "HUMAN_REVIEW"
    assert data["extraction"]["statusHistory"] == ["PENDING", "EXTRACTED"]
    assert data["extraction"]["persisted"] is False
    assert data["chunkCount"] == 2
    assert "Pasal 1" in data["extractedText"]
    after = client.get("/api/v1/knowledge", params={"pageSize": 100}, headers=reviewer).json()[
        "meta"
    ]["total"]
    assert after == before

    audit = client.get("/api/v1/audit-logs", headers=login(client, "sim.admin")).json()["data"]
    event = next(item for item in audit if item["action"] == "EXTRACT_PREVIEW")
    assert event["detail"]["format"] == "txt"
    assert event["detail"]["extractionStatus"] == "EXTRACTED"
    assert "filename" not in event["detail"]
    assert "content" not in event["detail"]


def test_extract_preview_requires_reviewer_and_simulated_labels() -> None:
    client = make_client()
    files = {
        "sourceFile": (
            "SIMULASI-contoh.txt",
            b"Isi simulasi yang cukup panjang.",
            "text/plain",
        )
    }
    data = {
        "documentLabel": "SIMULASI - Contoh",
        "knowledgeType": "OTHER",
        "maxWords": "400",
    }
    denied = client.post(
        EXTRACT_API, headers=login(client, "sim.staff.pppsun"), data=data, files=files
    )
    assert denied.status_code == 403

    invalid = client.post(
        EXTRACT_API,
        headers=login(client, "sim.coordinator"),
        data={**data, "documentLabel": "Dokumen tanpa tanda simulasi"},
        files=files,
    )
    assert invalid.status_code == 422


def test_unsafe_extraction_is_classified_and_audited_without_filename() -> None:
    client = make_client()
    response = client.post(
        EXTRACT_API,
        headers=login(client, "sim.coordinator"),
        data={
            "documentLabel": "SIMULASI - Berkas tidak aman",
            "knowledgeType": "OTHER",
            "maxWords": "400",
        },
        files={
            "sourceFile": (
                "SIMULASI-biner.txt",
                b"teks\x00biner yang tidak aman untuk dibaca",
                "text/plain",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["details"] == {
        "extractionStatus": "QUARANTINED",
        "reasonCode": "BINARY_CONTENT",
        "persisted": False,
    }
    audit = client.get("/api/v1/audit-logs", headers=login(client, "sim.admin")).json()["data"]
    event = next(item for item in audit if item["action"] == "EXTRACT_PREVIEW_REJECTED")
    assert event["detail"]["extractionStatus"] == "QUARANTINED"
    assert event["detail"]["reasonCode"] == "BINARY_CONTENT"
    assert "filename" not in event["detail"]
    assert "content" not in event["detail"]
