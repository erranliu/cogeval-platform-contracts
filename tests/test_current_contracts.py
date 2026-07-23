from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.cog_cases.current import validate_current_cog_case
from cogeval_platform_contracts.cog_cases.resources import load_fixture
from cogeval_platform_contracts.self_run_packages.current import validate_package_import_result_v2
from cogeval_platform_contracts.self_run_packages.resources import load_fixture as load_package_fixture


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
