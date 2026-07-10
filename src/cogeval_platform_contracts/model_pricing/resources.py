from __future__ import annotations

from typing import Any

from cogeval_platform_contracts import _resources


_PACKAGE = "cogeval_platform_contracts.model_pricing"


def load_schema(name: str) -> dict[str, Any]:
    return _resources.load_schema(_PACKAGE, name)


def list_fixtures() -> list[str]:
    return _resources.list_fixtures(_PACKAGE)


def load_fixture(name: str) -> dict[str, Any]:
    return _resources.load_fixture(_PACKAGE, name)
