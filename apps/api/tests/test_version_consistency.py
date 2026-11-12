"""Every place that states the SUNOVATE version must agree.

The API once kept reporting 0.2.0 after the packages moved to 0.3.0.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from sunovate_api import __version__
from sunovate_api.testing import make_client

ROOT = Path(__file__).resolve().parents[3]


def test_versions_match_across_packages_and_the_health_endpoint() -> None:
    package_versions = {
        path: json.loads((ROOT / path).read_text(encoding="utf-8"))["version"]
        for path in ("package.json", "apps/web/package.json", "packages/contracts/package.json")
    }
    pyproject = tomllib.loads((ROOT / "apps/api/pyproject.toml").read_text(encoding="utf-8"))
    lock = (ROOT / "apps/api/uv.lock").read_text(encoding="utf-8")
    locked = re.search(r'name = "sunovate-api"\nversion = "([^"]+)"', lock)
    assert locked, "uv.lock lists sunovate-api"
    health = make_client().get("/api/v1/health").json()["data"]["version"]
    stated = {*package_versions.values(), pyproject["project"]["version"], locked.group(1), health}
    assert stated == {__version__}, {**package_versions, "health": health}
