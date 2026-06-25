from __future__ import annotations

from typing import Any

from cogeval_platform_contracts._resources import (
    list_fixtures as _list_fixtures,
    load_fixture as _load_fixture,
    load_schema as _load_schema,
)

_PACKAGE = "cogeval_platform_contracts.cog_cases"


def load_schema(name: str) -> dict[str, Any]:
    return _load_schema(_PACKAGE, name)


def list_fixtures() -> list[str]:
    return _list_fixtures(_PACKAGE)


def load_fixture(name: str) -> dict[str, Any]:
    return _load_fixture(_PACKAGE, name)
