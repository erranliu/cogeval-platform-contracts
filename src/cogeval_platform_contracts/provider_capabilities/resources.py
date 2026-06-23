from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


_PACKAGE = "cogeval_platform_contracts.provider_capabilities"


def load_schema(name: str) -> dict[str, Any]:
    path = _resource_path("schemas", name, ".schema.json")
    return _read_json_object(path)


def list_fixtures() -> list[str]:
    fixture_root = files(_PACKAGE).joinpath("fixtures")
    return sorted(path.name.removesuffix(".json") for path in fixture_root.iterdir() if path.name.endswith(".json"))


def load_fixture(name: str) -> dict[str, Any]:
    path = _resource_path("fixtures", name, ".json")
    return _read_json_object(path)


def _resource_path(folder: str, name: str, suffix: str):
    safe_name = _safe_resource_name(name)
    if not safe_name.endswith(suffix):
        safe_name = f"{safe_name}{suffix}"
    path = files(_PACKAGE).joinpath(folder, safe_name)
    if not path.is_file():
        raise FileNotFoundError(f"unknown provider capability {folder[:-1]}: {name}")
    return path


def _read_json_object(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"resource must contain a JSON object: {path.name}")
    return payload


def _safe_resource_name(name: str) -> str:
    if not name or "/" in name or "\\" in name or ".." in name:
        raise ValueError(f"unsafe resource name: {name!r}")
    return name

