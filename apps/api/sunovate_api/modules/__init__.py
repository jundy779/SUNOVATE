"""API modules of the modular monolith. Each module owns one router."""

from fastapi import APIRouter

from . import (
    approvals,
    audit,
    auth,
    dashboard,
    documents,
    health,
    hermes,
    identity,
    knowledge,
    pending,
    search,
    secure_viewer,
    system,
    work,
)


def build_api_router() -> APIRouter:
    router = APIRouter()
    for module in (
        health,
        auth,
        identity,
        knowledge,
        documents,
        search,
        dashboard,
        work,
        pending,
        audit,
        approvals,
        hermes,
        secure_viewer,
        system,
    ):
        router.include_router(module.router)
    return router
