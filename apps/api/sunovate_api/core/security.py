"""Development-only signed token (HMAC-SHA256).

This is NOT a production authentication mechanism. The approved identity
mechanism is an OPEN QUESTION (OQ-07).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from .errors import unauthenticated


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class DevTokenSigner:
    def __init__(self, secret: str, ttl_minutes: int) -> None:
        # Empty secret: generate an ephemeral one, so tokens die when the process restarts.
        self._key = (secret or secrets.token_urlsafe(32)).encode("utf-8")
        self._ttl = timedelta(minutes=ttl_minutes)

    def _sign(self, payload: str) -> str:
        return _b64encode(hmac.new(self._key, payload.encode("ascii"), hashlib.sha256).digest())

    def issue(self, user_id: UUID, now: datetime | None = None) -> tuple[str, datetime]:
        issued = now or datetime.now(UTC)
        expires = issued + self._ttl
        body = {
            "sub": str(user_id),
            "iat": int(issued.timestamp()),
            "exp": int(expires.timestamp()),
        }
        payload = _b64encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
        return f"{payload}.{self._sign(payload)}", expires

    def verify(self, token: str, now: datetime | None = None) -> UUID:
        try:
            payload, signature = token.split(".", 1)
            # Non-ASCII input cannot be a token we issued; ascii-encoding it would raise a 500.
            payload.encode("ascii")
            signature.encode("ascii")
        except (ValueError, UnicodeError) as exc:
            raise unauthenticated("Token tidak valid") from exc
        if not hmac.compare_digest(signature, self._sign(payload)):
            raise unauthenticated("Token tidak valid")
        try:
            body = json.loads(_b64decode(payload))
            user_id = UUID(str(body["sub"]))
            expires_at = int(body["exp"])
        except (ValueError, KeyError, TypeError) as exc:
            raise unauthenticated("Token tidak valid") from exc
        if (now or datetime.now(UTC)).timestamp() >= expires_at:
            raise unauthenticated("Sesi telah berakhir, silakan masuk kembali")
        return user_id
