"""Response envelope, pagination, and camelCase serialization helpers."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import fields, is_dataclass
from typing import Annotated, Any

from fastapi import Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

DATA_LABEL = "SIMULATED_DATA"


class ApiModel(BaseModel):
    """Base request model: camelCase aliases, unknown fields rejected."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


class Pagination:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    ) -> None:
        self.page = page
        self.page_size = page_size


def serialize(record: object, *, exclude: Iterable[str] = ()) -> dict[str, Any]:
    """Convert a dataclass record into a JSON-safe dict with camelCase keys."""
    if not is_dataclass(record) or isinstance(record, type):
        raise TypeError("serialize() expects a dataclass instance")
    skip = set(exclude)
    raw = {f.name: getattr(record, f.name) for f in fields(record) if f.name not in skip}
    encoded: dict[str, Any] = jsonable_encoder(raw)
    return {to_camel(key): value for key, value in encoded.items()}


def envelope(data: object, **meta: object) -> dict[str, Any]:
    return {"data": jsonable_encoder(data), "meta": {"dataLabel": DATA_LABEL, **meta}}


def paginated[T](items: Sequence[T], pagination: Pagination) -> tuple[list[T], dict[str, int]]:
    total = len(items)
    start = (pagination.page - 1) * pagination.page_size
    page_items = list(items[start : start + pagination.page_size])
    meta = {
        "page": pagination.page,
        "pageSize": pagination.page_size,
        "total": total,
        "totalPages": math.ceil(total / pagination.page_size) if total else 0,
    }
    return page_items, meta
