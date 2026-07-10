# Model Pricing Catalog v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the standalone `cogeval.model_pricing_catalog.v1` Pydantic/JSON Schema contract, packaged fixtures/resources, and producer-consumer integration documentation.

**Architecture:** A new `model_pricing` contract domain owns strict current-only USD-per-million-token rates keyed by exact API-key `provider_id + model_id`. Pydantic performs whole-catalog duplicate validation, JSON Schema validates payload shape, and integration docs define Website publication/cross-catalog rules plus future Workbench loading behavior.

**Tech Stack:** Python 3.11, Pydantic 2, JSON Schema Draft 2020-12, jsonschema, pytest, Markdown integration contracts.

---

Reference design: `docs/superpowers/specs/2026-07-10-model-pricing-catalog-design.md`

### Task 1: Pydantic Pricing Contract

**Files:**
- Create: `src/cogeval_platform_contracts/model_pricing/__init__.py`
- Create: `src/cogeval_platform_contracts/model_pricing/v1.py`
- Create: `tests/test_model_pricing_v1.py`

- [ ] **Step 1: Write failing Pydantic tests**

Tests must cover:

```python
def test_accepts_empty_current_pricing_catalog() -> None:
    catalog = validate_model_pricing_catalog(
        {
            "schema": "cogeval.model_pricing_catalog.v1",
            "updated_at": "2026-07-10T00:00:00Z",
            "currency": "USD",
            "unit_tokens": 1_000_000,
            "prices": [],
        }
    )
    assert catalog.prices == []


def test_rejects_duplicate_provider_model_pair() -> None:
    payload = _valid_payload()
    payload["prices"].append(deepcopy(payload["prices"][0]))
    with pytest.raises(ValidationError, match="duplicate provider/model pricing pairs"):
        validate_model_pricing_catalog(payload)
```

Parameterize valid rate strings (`0`, `3`, `0.3`, `3.75`, 12 integer digits, 12 fractional digits) and invalid values (`00`, `01`, `.5`, `1.`, spaces/tabs/newlines, `1e-3`, negatives, 13 integer/fractional digits, JSON numbers, booleans, blank strings). Test all five rates are required, IDs are nonblank, unknown fields are forbidden, currency/unit/schema are literals, and `updated_at` accepts only a real UTC `YYYY-MM-DDTHH:MM:SSZ` timestamp.

Also delete each top-level field in turn and assert `schema`, `updated_at`, `currency`, `unit_tokens`, and `prices` are all required. Replace wire key `schema` with Python field name `schema_version` and assert validation fails; the closed wire contract accepts aliases only.

- [ ] **Step 2: Run tests and verify RED**

Run: `pytest tests/test_model_pricing_v1.py -q`

Expected: import failure because `cogeval_platform_contracts.model_pricing` does not exist.

- [ ] **Step 3: Implement the strict v1 models**

Define the local base explicitly; do not import or copy the model-capability base with `populate_by_name=True`:

```python
MODEL_PRICING_CATALOG_SCHEMA = "cogeval.model_pricing_catalog.v1"
RATE_PATTERN = r"^(0|[1-9][0-9]{0,11})(\.[0-9]{1,12})?$"
TIMESTAMP_PATTERN = r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"

class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=False)

class PricingRates(StrictContractModel):
    input_uncached: str = Field(pattern=RATE_PATTERN)
    input_cache_read: str = Field(pattern=RATE_PATTERN)
    input_cache_write: str = Field(pattern=RATE_PATTERN)
    output: str = Field(pattern=RATE_PATTERN)
    reasoning_output: str = Field(pattern=RATE_PATTERN)

class ModelPrice(StrictContractModel):
    provider_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    rates: PricingRates

class ModelPricingCatalog(StrictContractModel):
    schema_version: Literal["cogeval.model_pricing_catalog.v1"] = Field(
        alias="schema",
    )
    updated_at: str
    currency: Literal["USD"]
    unit_tokens: Literal[1_000_000]
    prices: list[ModelPrice]
```

Add validators that reject whitespace-only IDs, require `re.fullmatch(TIMESTAMP_PATTERN, value)` before parsing `updated_at` with `datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")`, and reject duplicate `(provider_id, model_id)` pairs. Export `validate_model_pricing_catalog(payload)`. The full match is mandatory because `strptime` alone accepts unpadded components.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `pytest tests/test_model_pricing_v1.py -q`

Expected: all pricing Pydantic tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cogeval_platform_contracts/model_pricing tests/test_model_pricing_v1.py
git commit -m "feat: define model pricing catalog contract"
```

### Task 2: JSON Schema, Fixtures, And Packaged Resources

**Files:**
- Create: `src/cogeval_platform_contracts/model_pricing/resources.py`
- Create: `src/cogeval_platform_contracts/model_pricing/schemas/model_pricing_catalog.v1.schema.json`
- Create: `src/cogeval_platform_contracts/model_pricing/fixtures/empty.v1.json`
- Create: `src/cogeval_platform_contracts/model_pricing/fixtures/provider_models.v1.json`
- Modify: `src/cogeval_platform_contracts/model_pricing/__init__.py`
- Modify: `pyproject.toml`
- Create: `tests/test_model_pricing_json_schema.py`
- Create: `tests/test_model_pricing_resources.py`

- [ ] **Step 1: Write failing schema/resource tests**

Assert:

- Draft 2020-12 schema validates itself;
- both fixtures pass JSON Schema and Pydantic validation;
- removing each of `schema`, `updated_at`, `currency`, `unit_tokens`, and `prices` fails JSON Schema validation;
- missing rates, JSON numeric rates, invalid decimal boundaries (including a trailing newline), unknown fields, malformed timestamp syntax, and impossible calendar timestamps fail JSON Schema;
- `list_fixtures()` returns both fixture names;
- `load_schema("model_pricing_catalog.v1")` and `load_fixture(...)` return JSON-serializable dictionaries.

- [ ] **Step 2: Run tests and verify RED**

Run: `pytest tests/test_model_pricing_json_schema.py tests/test_model_pricing_resources.py -q`

Expected: failures because schema/resources/fixtures are absent.

- [ ] **Step 3: Implement schema, resources, and fixtures**

Use `$schema: https://json-schema.org/draft/2020-12/schema`, `additionalProperties: false` at every object, exact `const` values for schema/currency/unit, and the same rate regex as Pydantic. The root object has `"required": ["schema", "updated_at", "currency", "unit_tokens", "prices"]`; each price row and rates object likewise list all contract-required fields. Add `"not": {"pattern": "\\s"}` to every rate string so JSON Schema cannot accept a final newline through `$` behavior.

Timestamp validation uses both:

```json
{
  "type": "string",
  "format": "date-time",
  "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
}
```

Instantiate schema validators with `FormatChecker()` so `format: date-time` is asserted. Change the test extra in `pyproject.toml` to include `jsonschema[format]>=4.22` and `build>=1,<2`; this supplies RFC 3339 format validation and the declared package-build command.

Before Step 4, install the changed test extra:

Run: `python -m pip install -e ".[test]"`

Expected: editable package plus JSON Schema format and build dependencies install successfully.

`empty.v1.json` uses a stable seed timestamp. `provider_models.v1.json` includes at least two providers, a nonzero cache-write example, a reasoning/output same-rate example, and an explicit all-zero row.

Add the three resource helpers following other contract domains. Export models/helpers/resources from `model_pricing/__init__.py`. Add these package-data globs:

```toml
"model_pricing/schemas/*.json",
"model_pricing/fixtures/*.json",
```

- [ ] **Step 4: Run all pricing contract tests**

Run: `pytest tests/test_model_pricing_v1.py tests/test_model_pricing_json_schema.py tests/test_model_pricing_resources.py -q`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/cogeval_platform_contracts/model_pricing tests/test_model_pricing_json_schema.py tests/test_model_pricing_resources.py
git commit -m "feat: package model pricing schema and fixtures"
```

### Task 3: Contract And Integration Documentation

**Files:**
- Create: `docs/MODEL_PRICING_CATALOG_V1.md`
- Create: `docs/integrations/workbench-model-pricing-v1.md`
- Modify: `docs/契约.md`
- Modify: `docs/integrations/README.md`
- Modify: `docs/integrations/workbench-api-key-provider-catalog-v1.md`

- [ ] **Step 1: Add a failing documentation contract test**

Create `tests/test_model_pricing_documentation.py` that reads the five documentation/index files and asserts the following stable facts are present:

- schema ID and public path;
- exact provider/model identity;
- USD per 1,000,000 tokens;
- five dimensions;
- missing is unavailable and explicit zero is free;
- built-in accounts are excluded;
- empty seed behavior;
- pricing-first removal/provider-first addition ordering;
- reverse provider-catalog publication validation;
- required producer and future consumer tests.

- [ ] **Step 2: Run the documentation test and verify RED**

Run: `pytest tests/test_model_pricing_documentation.py -q`

Expected: FAIL because pricing documents and index entries do not exist.

- [ ] **Step 3: Write the contract and integration documents**

`MODEL_PRICING_CATALOG_V1.md` owns schema semantics, decimal grammar, examples, compatibility, and calculation mapping. `workbench-model-pricing-v1.md` owns producer API/auth, loader config, direct response shape, empty seed, failure behavior, data flow, and producer/consumer test checklists.

Update both indexes. Update `workbench-api-key-provider-catalog-v1.md` to state that Provider Catalog publication must reject removal of a provider/model pair referenced by active pricing. Keep Website internal admin DTOs out of the public contract.

- [ ] **Step 4: Run documentation and full pricing tests**

Run: `pytest tests/test_model_pricing_documentation.py tests/test_model_pricing_v1.py tests/test_model_pricing_json_schema.py tests/test_model_pricing_resources.py -q`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/MODEL_PRICING_CATALOG_V1.md docs/integrations/workbench-model-pricing-v1.md docs/契约.md docs/integrations/README.md docs/integrations/workbench-api-key-provider-catalog-v1.md tests/test_model_pricing_documentation.py
git commit -m "docs: register Workbench model pricing integration"
```

### Task 4: Full Contract Verification

**Files:**
- Modify only files required to correct failures caused by this contract.

- [ ] **Step 1: Run the complete repository test suite**

Run: `pytest -q`

Expected: all tests PASS with zero failures.

- [ ] **Step 2: Verify packaged artifacts**

Install the declared test/build extras into the active development environment:

Run: `python -m pip install -e ".[test]"`

Expected: editable package plus `jsonschema[format]`, pytest, and build dependencies install successfully.

Run: `python -m build`

Expected: wheel and sdist build successfully and include `model_pricing` schema/fixtures.

Inspect both archives rather than importing the editable source tree:

Run: `python -c "from pathlib import Path; import tarfile, zipfile; artifacts=list(Path('dist').glob('*')); wheel=next(p for p in artifacts if p.suffix=='.whl'); sdist=next(p for p in artifacts if p.name.endswith('.tar.gz')); expected=('model_pricing/schemas/model_pricing_catalog.v1.schema.json','model_pricing/fixtures/empty.v1.json','model_pricing/fixtures/provider_models.v1.json'); wn=zipfile.ZipFile(wheel).namelist(); tn=tarfile.open(sdist).getnames(); assert all(any(n.endswith(e) for n in wn) for e in expected); assert all(any(n.endswith(e) for n in tn) for e in expected); print('pricing resources packaged')"`

Expected output: `pricing resources packaged`.

- [ ] **Step 3: Verify diff scope and whitespace**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors and only planned contract/plan files remain.

- [ ] **Step 4: Commit verification-only corrections if needed**

Do not create an empty commit. If verification required a correction, stage only that correction and commit:

```bash
git commit -m "test: close model pricing contract verification"
```

- [ ] **Step 5: Record the implementation commit range for the Website handoff**

Run: `git log --oneline --decorate -6`

Expected: design, plan, contract, resources, and integration-document commits are visible for the handoff prompt.
