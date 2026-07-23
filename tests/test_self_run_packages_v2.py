import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.self_run_packages import load_fixture
from cogeval_platform_contracts.self_run_packages.v2 import validate_package_import_result_v2


def test_v2_fixture_separates_failure_from_decision() -> None:
    result = validate_package_import_result_v2(load_fixture("import_result_mixed.v2"))
    assert result.n_accepted == 1
    assert result.results[1].failure_reason is not None
    assert result.results[1].failure_reason.code == "platform.ingest_rejected"


def test_v2_rejects_failure_and_decision_on_same_result() -> None:
    payload = load_fixture("import_result_mixed.v2")
    payload["results"][1]["decision_codes"] = ["manual_review"]
    with pytest.raises(ValidationError):
        validate_package_import_result_v2(payload)


def test_v2_requires_failure_for_non_review_rejection() -> None:
    payload = load_fixture("import_result_mixed.v2")
    payload["results"][1]["failure_reason"] = None
    with pytest.raises(ValidationError):
        validate_package_import_result_v2(payload)
