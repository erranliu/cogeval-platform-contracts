from __future__ import annotations

import re
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


def test_model_pricing_index_rows_are_complete_and_links_resolve() -> None:
    contract_row = (
        "| Model Pricing Catalog | `cogeval.model_pricing_catalog.v1` | "
        "中台模型价格配置 | Workbench 成本估算 | "
        "[MODEL_PRICING_CATALOG_V1.md](MODEL_PRICING_CATALOG_V1.md) |"
    )
    contract_integration_row = (
        "| Workbench Model Pricing Catalog v1 | "
        "`cogeval.model_pricing_catalog.v1` | 中台 -> Workbench | "
        "[integrations/workbench-model-pricing-v1.md]"
        "(integrations/workbench-model-pricing-v1.md) |"
    )
    integration_row = (
        "| Workbench Model Pricing Catalog v1 | "
        "`cogeval.model_pricing_catalog.v1` | 中台 -> Workbench | "
        "`GET /api/workbench/v1/model-pricing` | model pricing catalog loader | "
        "[workbench-model-pricing-v1.md](workbench-model-pricing-v1.md) |"
    )

    assert contract_row in CONTRACT_INDEX
    assert contract_integration_row in CONTRACT_INDEX
    assert integration_row in INTEGRATION_INDEX

    pricing_links = (
        (ROOT / "docs", CONTRACT_INDEX, "MODEL_PRICING_CATALOG_V1.md"),
        (
            ROOT / "docs",
            CONTRACT_INDEX,
            "integrations/workbench-model-pricing-v1.md",
        ),
        (
            ROOT / "docs" / "integrations",
            INTEGRATION_INDEX,
            "workbench-model-pricing-v1.md",
        ),
    )
    for parent, document, expected_target in pricing_links:
        targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", document)
        assert expected_target in targets
        assert (parent / expected_target).is_file()


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


def test_canonical_document_defines_updated_at_lifecycle() -> None:
    assert "For an active catalog, `updated_at` is its publication time" in CONTRACT
    assert (
        "For the no-active empty seed, `updated_at` is a stable seed-definition "
        "constant and is never generated from request time"
        in CONTRACT
    )


def test_canonical_document_structurally_maps_exactly_five_rates() -> None:
    expected_mappings = [
        ("input_uncached", "input_uncached_tokens"),
        ("input_cache_read", "input_cache_read_tokens"),
        ("input_cache_write", "input_cache_write_tokens"),
        ("output", "output_tokens"),
        ("reasoning_output", "reasoning_output_tokens"),
    ]
    mappings = re.findall(
        r"^\| `([^`]+)` \| `([^`]+_tokens)` \|$",
        CONTRACT,
        flags=re.MULTILINE,
    )

    assert mappings == expected_mappings


def test_canonical_cost_formula_contains_each_dimension_exactly_once() -> None:
    match = re.search(
        r"```text\n(cost_usd =\n.*?)\n```",
        CONTRACT,
        flags=re.DOTALL,
    )
    assert match is not None
    formula_lines = tuple(line.strip() for line in match.group(1).splitlines())
    expected_lines = (
        "cost_usd =",
        "input_uncached_tokens    * input_uncached_rate    / unit_tokens",
        "+ input_cache_read_tokens  * input_cache_read_rate  / unit_tokens",
        "+ input_cache_write_tokens * input_cache_write_rate / unit_tokens",
        "+ output_tokens            * output_rate            / unit_tokens",
        "+ reasoning_output_tokens  * reasoning_output_rate  / unit_tokens",
    )

    assert formula_lines == expected_lines


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


def test_workbench_must_filter_orphan_prices_and_preserve_unconfigured_runs() -> None:
    assert (
        "Workbench must cross-check the accepted API Key Provider Catalog and "
        "ignore orphan pricing rows"
        in INTEGRATION
    )
    assert (
        "Platform not configured: Workbench reports pricing unavailable and "
        "preserves token recording and execution"
        in INTEGRATION
    )


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


def test_both_catalog_publishes_use_one_cross_catalog_serialization_boundary() -> None:
    shared_lock_facts = (
        "same cross-catalog publication lock",
        "before reading the committed active counterpart, validating, and committing",
        "active-version change",
        "Equivalent serializable database isolation is acceptable only when it guarantees conflict detection and retry",
        "fresh committed counterpart read",
        "No interleaving may activate an orphan provider/model pair",
    )

    for document in (INTEGRATION, PROVIDER_INTEGRATION):
        for fact in shared_lock_facts:
            assert fact in document


def test_required_producer_checklist_covers_contract_and_publication_invariants() -> None:
    producer_assertions = (
        "draft validation uses the shared contract",
        "pricing publication validates references against the active API Key Provider Catalog and rejects unknown provider/model references",
        "provider publication reverse-validates active pricing and blocks referenced removal",
        "synchronized conflicting publication attempts cannot activate an orphan pair",
        "stale validation cannot commit inconsistent active catalogs",
        "the public endpoint returns exactly one active version as the direct v1 catalog",
        "public endpoint authentication follows the existing catalog policy",
        "no active catalog returns the stable valid empty seed",
    )

    for assertion in producer_assertions:
        assert assertion in INTEGRATION
    assert "Candidate draft validation is mandatory before publication" in INTEGRATION
    assert "synchronized conflicting publication attempts" in PROVIDER_INTEGRATION


def test_required_consumer_checklist_covers_exact_cost_availability_rules() -> None:
    consumer_assertions = (
        "the whole payload is loaded and validated before any row is used",
        "exact API-key `provider_id + model_id` matching works",
        "decimal rate strings are preserved",
        "missing, built-in, and orphan pricing are unavailable",
        "invalid catalog disables cost only while token recording and execution remain available",
        "cache and reasoning rates map to their exact canonical token fields",
        "reasoning output is charged exactly once",
    )

    for assertion in consumer_assertions:
        assert assertion in INTEGRATION
