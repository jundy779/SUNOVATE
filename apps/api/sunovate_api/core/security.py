"""Development-only signed token (HMAC-SHA256).

This is NOT a production authentication mechanism. The approved identity
mechanism is an OPEN QUESTION (OQ-07).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from .errors import unauthenticated


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


_TOKEN_ID = re.compile(r"[0-9a-f]{32}")


@dataclass(frozen=True)
class TokenClaims:
    user_id: UUID
    token_id: str  # random per token, so one session can be revoked on logout (AUD-05)
    expires_at: datetime


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
            "jti": secrets.token_hex(16),
            "iat": int(issued.timestamp()),
            "exp": int(expires.timestamp()),
        }
        payload = _b64encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
        return f"{payload}.{self._sign(payload)}", expires

    def verify(self, token: str, now: datetime | None = None) -> UUID:
        return self.verify_claims(token, now).user_id

    def verify_claims(self, token: str, now: datetime | None = None) -> TokenClaims:
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
            token_id = str(body["jti"])
        except (ValueError, KeyError, TypeError) as exc:
            # Tokens without an id predate AUD-05 and cannot be revoked, so they are refused.
            raise unauthenticated("Token tidak valid") from exc
        if not _TOKEN_ID.fullmatch(token_id):
            raise unauthenticated("Token tidak valid")
        if (now or datetime.now(UTC)).timestamp() >= expires_at:
            raise unauthenticated("Sesi telah berakhir, silakan masuk kembali")
        return TokenClaims(user_id, token_id, datetime.fromtimestamp(expires_at, UTC))
