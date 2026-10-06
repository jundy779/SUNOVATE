"""Provider status and data quality issues."""

from __future__ import annotations

from dataclasses import asdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic.alias_generators import to_camel

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.responses import Pagination, envelope, paginated
from ..store.records import DataQualityIssue
from ._common import governed_view

router = APIRouter(tags=["providers and data quality"])


@router.get("/providers")
def list_providers(
    ctx: Ctx, _p: Annotated[Principal, Depends(require("provider:read", resource="provider"))]
) -> dict[str, Any]:
    rows = [{to_camel(k): v for k, v in asdict(s).items()} for s in ctx.providers.statuses()]
    return envelope(rows, total=len(rows), productionIntegrations="DISABLED")


@router.get("/data-quality-issues")
def list_data_quality(
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("data_quality:read", resource="data_quality_issue"))
    ],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    items = ctx.authz.list_readable(principal, DataQualityIssue)
    page, meta = paginated(items, pagination)
    return envelope([governed_view(ctx, i) for i in page], **meta)
