"""Review-only chunk preview API tests."""

from sunovate_api.testing import login, make_client

API = "/api/v1/knowledge/chunk-preview"


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
