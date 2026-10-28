"""Every API route keeps the response contract (implementation-master-plan Tahap 1 butir 5).

Without credentials, every non-public route must answer with the standard error body
(`code`, `message`, `details`, `requestId`), echo the request id in `X-Request-ID`, and carry
the security headers. Unknown routes and wrong methods use the same body in Indonesian.
"""

from __future__ import annotations

import re
from uuid import uuid4

import pytest

from sunovate_api.testing import make_client

PUBLIC = {
    ("GET", "/api/v1/health"),
    ("GET", "/api/v1/health/database"),
    ("POST", "/api/v1/auth/dev/login"),
}
SECURITY_HEADERS = {"x-content-type-options": "nosniff", "x-frame-options": "DENY"}
CLIENT = make_client()
ROUTES = sorted(
    (method.upper(), path)
    for path, operations in CLIENT.app.openapi()["paths"].items()
    for method in operations
    if (method.upper(), path) not in PUBLIC
)


def _assert_contract(response, request_id: str) -> None:  # type: ignore[no-untyped-def]
    body = response.json()
    assert set(body) == {"code", "message", "details", "requestId"}
    assert body["requestId"] == request_id
    assert response.headers["x-request-id"] == request_id
    for header, value in SECURITY_HEADERS.items():
        assert response.headers[header] == value
    assert not re.search(r"[A-Z][a-z]+ [A-Z][a-z]+$", body["message"]), body["message"]


@pytest.mark.parametrize(("method", "path"), ROUTES)
def test_protected_routes_reject_anonymous_calls_with_the_standard_body(
    method: str, path: str
) -> None:
    concrete = re.sub(r"\{[^}]+\}", str(uuid4()), path)
    request_id = f"kontrak-{uuid4().hex[:8]}"
    response = CLIENT.request(method, concrete, headers={"X-Request-ID": request_id}, json={})
    assert response.status_code == 401, (method, path, response.status_code)
    assert response.json()["code"] == "UNAUTHENTICATED"
    _assert_contract(response, request_id)


def test_route_inventory_is_not_empty() -> None:
    assert len(ROUTES) >= 50


def test_unknown_route_and_wrong_method_use_the_contract_in_indonesian() -> None:
    missing = CLIENT.get("/api/v1/tidak-ada", headers={"X-Request-ID": "kontrak-404"})
    assert missing.status_code == 404
    assert missing.json()["message"] == "Data atau halaman tidak ditemukan"
    _assert_contract(missing, "kontrak-404")

    wrong = CLIENT.put("/api/v1/health", headers={"X-Request-ID": "kontrak-405"})
    assert wrong.status_code == 405
    assert wrong.json()["message"] == "Metode permintaan tidak diizinkan"
    _assert_contract(wrong, "kontrak-405")


def test_successful_responses_also_echo_the_request_id() -> None:
    response = CLIENT.get("/api/v1/health", headers={"X-Request-ID": "kontrak-200"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "kontrak-200"
