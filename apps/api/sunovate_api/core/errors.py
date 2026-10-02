"""Application error type and FastAPI handlers producing the standard error envelope.

Envelope: {"code", "message", "details", "requestId"}. Stack traces are never returned.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .logging import request_id_var

logger = logging.getLogger("sunovate")


class ApiError(Exception):
    def __init__(
        self, status_code: int, code: str, message: str, details: object | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def unauthenticated(message: str = "Autentikasi diperlukan") -> ApiError:
    return ApiError(401, "UNAUTHENTICATED", message)


def permission_denied(message: str = "Anda tidak memiliki izin untuk tindakan ini") -> ApiError:
    return ApiError(403, "PERMISSION_DENIED", message)


def not_found(entity: str = "Data") -> ApiError:
    return ApiError(404, "NOT_FOUND", f"{entity} tidak ditemukan")


def revision_conflict(current: int) -> ApiError:
    return ApiError(
        409,
        "REVISION_CONFLICT",
        "Data telah diperbarui oleh pengguna lain. Muat ulang data sebelum menyimpan perubahan.",
        {"currentRevision": current},
    )


def invalid_state(message: str) -> ApiError:
    return ApiError(409, "INVALID_STATE", message)


def error_body(code: str, message: str, details: object | None = None) -> dict[str, object]:
    return {
        "code": code,
        "message": message,
        "details": jsonable_encoder(details),
        "requestId": request_id_var.get(),
    }


_STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHENTICATED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(error_body(exc.code, exc.message, exc.details), exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation(_request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "location": list(err.get("loc", ())),
                "message": err.get("msg"),
                "type": err.get("type"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(error_body("VALIDATION_ERROR", "Input tidak valid", details), 422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _STATUS_CODES.get(exc.status_code, "HTTP_ERROR")
        message = exc.detail if isinstance(exc.detail, str) else "Permintaan tidak dapat diproses"
        return JSONResponse(error_body(code, message), exc.status_code)

    @app.exception_handler(Exception)
    async def _unhandled(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", extra={"errorType": type(exc).__name__})
        return JSONResponse(error_body("INTERNAL_ERROR", "Terjadi kesalahan internal"), 500)
