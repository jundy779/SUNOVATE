import pytest
from pydantic import ValidationError

from sunovate_api.core.config import Settings
from sunovate_api.testing import login, make_client


def test_health_is_public_and_labelled() -> None:
    client = make_client()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["dataBackend"] == "simulated"
    assert body["meta"]["dataLabel"] == "SIMULATED_DATA"
    assert response.headers["X-Request-ID"]


def test_request_id_is_propagated() -> None:
    client = make_client()
    response = client.get("/api/v1/health", headers={"X-Request-ID": "req-test-123"})
    assert response.headers["X-Request-ID"] == "req-test-123"


def test_dev_login_and_me() -> None:
    client = make_client()
    headers = login(client, "sim.lead.psun")
    me = client.get("/api/v1/auth/me", headers=headers).json()["data"]
    assert me["roles"] == ["team_lead"]
    assert [t["code"] for t in me["teams"]] == ["PSUN"]
    assert me["clearanceCode"] == "RESTRICTED"
    assert "knowledge:publish" not in me["permissions"]


def test_unknown_user_cannot_log_in() -> None:
    client = make_client()
    response = client.post("/api/v1/auth/dev/login", json={"email": "someone@example.go.id"})
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


@pytest.mark.parametrize("header", [None, "Bearer", "Bearer not-a-token", "Basic abc"])
def test_protected_endpoint_requires_valid_token(header: str | None) -> None:
    client = make_client()
    headers = {"Authorization": header} if header else {}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    body = response.json()
    assert set(body) == {"code", "message", "details", "requestId"}


def test_tampered_token_is_rejected() -> None:
    client = make_client()
    token = login(client, "sim.staff.pppsun")["Authorization"]
    tampered = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    assert client.get("/api/v1/auth/me", headers={"Authorization": tampered}).status_code == 401


def test_token_from_other_secret_is_rejected() -> None:
    issuer, verifier = make_client(), make_client(dev_auth_secret="another-secret")
    headers = login(issuer, "sim.staff.pppsun")
    assert verifier.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_dev_auth_disabled_blocks_login_and_access() -> None:
    client = make_client(dev_auth_enabled=False)
    login_response = client.post("/api/v1/auth/dev/login",
                                 json={"email": "sim.admin@sunovate.local"})
    assert login_response.status_code == 404
    assert login_response.json()["code"] == "DEV_AUTH_DISABLED"
    assert client.get("/api/v1/auth/me").status_code == 401


def test_production_refuses_dev_auth_and_simulated_backend() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", dev_auth_enabled=True)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", dev_auth_enabled=False)


def test_validation_error_envelope() -> None:
    client = make_client()
    response = client.post("/api/v1/auth/dev/login", json={"email": "x"})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
