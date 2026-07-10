from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    path = ROOT / relative_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


CONTRACT = _read("docs/MODEL_PRICING_CATALOG_V1.md")
INTEGRATION = _read("docs/integrations/workbench-model-pricing-v1.md")
CONTRACT_INDEX = _read("docs/契约.md")
INTEGRATION_INDEX = _read("docs/integrations/README.md")
PROVIDER_INTEGRATION = _read(
    "docs/integrations/workbench-api-key-provider-catalog-v1.md"
)


def test_model_pricing_contract_is_registered_in_both_indexes() -> None:
    assert "cogeval.model_pricing_catalog.v1" in CONTRACT_INDEX
    assert "MODEL_PRICING_CATALOG_V1.md" in CONTRACT_INDEX
    assert "workbench-model-pricing-v1.md" in CONTRACT_INDEX

    assert "cogeval.model_pricing_catalog.v1" in INTEGRATION_INDEX
    assert "GET /api/workbench/v1/model-pricing" in INTEGRATION_INDEX
    assert "workbench-model-pricing-v1.md" in INTEGRATION_INDEX


def test_canonical_document_defines_closed_v1_wire_semantics() -> None:
    required_facts = (
        "cogeval.model_pricing_catalog.v1",
        "provider_id + model_id",
        "USD per exactly 1,000,000 tokens",
        "input_uncached",
        "input_cache_read",
        "input_cache_write",
        "`output`",
        "reasoning_output",
        r"^(0|[1-9][0-9]{0,11})(\.[0-9]{1,12})?$",
        "YYYY-MM-DDTHH:MM:SSZ",
        "Pydantic whole-catalog validation is normative for pair uniqueness",
        "A missing row means pricing is unavailable",
        'an explicit rate of `"0"` means that dimension is free',
        "ordinary output and reasoning output are disjoint",
        "charged exactly once",
        "closed v1 schema",
        "current-only",
    )

    for fact in required_facts:
        assert fact in CONTRACT


def test_workbench_integration_defines_public_loader_and_failure_boundaries() -> None:
    required_facts = (
        "GET /api/workbench/v1/model-pricing",
        "without an outer envelope",
        "existing optional Workbench catalog Bearer-token policy",
        "platform.model_pricing_catalog_path",
        "API-key provider sources only",
        "Built-in account sources are excluded",
        "stable valid empty seed",
        "invalid catalog disables cost estimation only",
        "token recording and execution remain available",
        "provider-first, then pricing",
        "pricing-first, then provider",
        "committed active counterpart",
        "reasoning and ordinary output are disjoint",
        "charged exactly once",
        "Producer tests",
        "Future Workbench consumer tests",
    )

    for fact in required_facts:
        assert fact in INTEGRATION


def test_catalog_publish_rules_are_bidirectional_and_concurrency_safe() -> None:
    pricing_publish_facts = (
        "pricing publication validates every row against the active API Key Provider Catalog",
        "counterpart validation must be repeated inside the publish transaction",
    )
    provider_publish_facts = (
        "active Model Pricing Catalog",
        "blocks removal of a provider/model pair while active pricing references it",
        "publish pricing removal first",
        "committed active pricing catalog",
        "concurrent or stale validation",
    )

    for fact in pricing_publish_facts:
        assert fact in INTEGRATION
    for fact in provider_publish_facts:
        assert fact in PROVIDER_INTEGRATION


def test_documents_list_required_producer_and_consumer_coverage() -> None:
    producer_facts = (
        "public endpoint returns the direct v1 catalog",
        "no active catalog returns the stable valid empty seed",
        "publish rejects unknown provider/model references",
        "provider catalog publish blocks referenced removal",
        "stale validation cannot commit inconsistent active catalogs",
    )
    consumer_facts = (
        "decimal strings are preserved",
        "missing, built-in, and orphan pricing are unavailable",
        "invalid catalog disables cost only",
        "cache and reasoning dimensions map to canonical token fields",
        "reasoning output is charged exactly once",
    )

    for fact in producer_facts + consumer_facts:
        assert fact in INTEGRATION
