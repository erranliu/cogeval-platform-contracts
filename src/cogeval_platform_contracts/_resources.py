from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_schema(package: str, name: str) -> dict[str, Any]:
    return _read_json_object(_resource_path(package, "schemas", name, ".schema.json"))


def list_fixtures(package: str) -> list[str]:
    fixture_root = files(package).joinpath("fixtures")
    return sorted(path.name.removesuffix(".json") for path in fixture_root.iterdir() if path.name.endswith(".json"))


def load_fixture(package: str, name: str) -> dict[str, Any]:
    return _read_json_object(_resource_path(package, "fixtures", name, ".json"))


def _resource_path(package: str, folder: str, name: str, suffix: str):
    safe_name = _safe_resource_name(name)
    if not safe_name.endswith(suffix):
        safe_name = f"{safe_name}{suffix}"
    path = files(package).joinpath(folder, safe_name)
    if not path.is_file():
        raise FileNotFoundError(f"unknown {package} {folder[:-1]}: {name}")
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
