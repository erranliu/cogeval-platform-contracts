from __future__ import annotations

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.cog_cases.current import validate_current_cog_case
from cogeval_platform_contracts.cog_cases.resources import load_fixture
from cogeval_platform_contracts.self_run_packages.current import validate_package_import_result_v2
from cogeval_platform_contracts.self_run_packages.resources import load_fixture as load_package_fixture


def test_current_contract_modules_do_not_import_retired_version_modules() -> None:
    root = Path(__file__).resolve().parents[1] / "src" / "cogeval_platform_contracts"
    for relative in ("cog_cases/current.py", "self_run_packages/current.py"):
        tree = ast.parse((root / relative).read_text(encoding="utf-8"))
        modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(module.endswith(".v1") or module.endswith(".v2") for module in modules)


def test_current_group_contract_owns_member_count_invariant() -> None:
    payload = load_fixture("group_public.v1")
    payload["members"] = [load_fixture("case_public.v3")]
    payload["member_count"] = 0
    with pytest.raises(ValidationError, match="member_count"):
        from cogeval_platform_contracts.cog_cases.current import validate_current_cog_case_group

        validate_current_cog_case_group(payload)


def test_current_case_is_v3_and_rejects_retired_schema() -> None:
    current = validate_current_cog_case(load_fixture("case_public.v3"))
    assert current.cog_case_display_id == "SWEPro#1"

    with pytest.raises(ValidationError):
        validate_current_cog_case(load_fixture("case_public.v1"))


def test_current_case_accepts_hydrated_public_fields() -> None:
    payload = load_fixture("case_public.v3")
    payload["validation"] = {"backend": "pytest", "command": "pytest -q"}
    payload["workspace"] = {"docker_image": "case:latest"}
    current = validate_current_cog_case(payload)
    assert current.validation == payload["validation"]


def test_current_import_result_is_v2_only() -> None:
    result = validate_package_import_result_v2(load_package_fixture("import_result_mixed.v2"))
    assert result.schema == "cogeval.package_import_result.v2"
    with pytest.raises(ValidationError):
        validate_package_import_result_v2(load_package_fixture("import_result_mixed.v1"))
