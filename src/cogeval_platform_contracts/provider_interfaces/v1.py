from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


PROVIDER_INTERFACE_CATALOG_SCHEMA = "cogeval.provider_interface_catalog.v1"
WORKBENCH_PROVIDER_CATALOG_SCHEMA = "cogeval.api_key_provider_catalog.v1"

PROVIDER_INTERFACE_ALIASES: dict[str, str] = {
    "codex_model_provider": "openai_responses",
    "anthropic_gateway": "anthropic_compatible_messages",
}

VALID_PROVIDER_INTERFACES = {
    "openai_compatible_chat",
    "openai_responses",
    "anthropic_compatible_messages",
}


class ProviderInterfaceCatalogError(ValueError):
    def __init__(self, code: str, message: str, *, detail: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


def canonical_provider_interface_id(interface: str) -> str:
    return PROVIDER_INTERFACE_ALIASES.get(interface, interface)


def provider_interface_ids_equal(left: str, right: str) -> bool:
    return canonical_provider_interface_id(left) == canonical_provider_interface_id(right)


def is_valid_provider_interface(interface: str) -> bool:
    return canonical_provider_interface_id(interface) in VALID_PROVIDER_INTERFACES


class ProviderInterface(StrictContractModel):
    interface: str = Field(min_length=1)
    default_base_url: str | None = None
    default_model_prefix: str | None = None
    recommended: bool = False

    @model_validator(mode="after")
    def validate_interface(self) -> "ProviderInterface":
        if self.interface not in VALID_PROVIDER_INTERFACES:
            raise ValueError(f"unknown provider interface: {self.interface}")
        _validate_optional_http_url("supported_interfaces.default_base_url", self.default_base_url)
        return self


class ProviderModel(StrictContractModel):
    display_name: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    recommended: bool = False
    capabilities: dict[str, Any] = Field(default_factory=dict)

    @field_validator("capabilities", mode="before")
    @classmethod
    def normalize_capabilities(cls, value: object) -> object:
        if isinstance(value, dict):
            return value
        if not isinstance(value, list):
            return value

        capabilities: dict[str, bool] = {}
        for item in value:
            if not isinstance(item, str):
                raise ValueError("capabilities list items must be non-empty strings")
            capability = item.strip()
            if not capability:
                raise ValueError("capabilities list items must be non-empty strings")
            capabilities[capability] = True
        return capabilities


class ApiKeyProvider(StrictContractModel):
    provider_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    status: Literal["supported", "preview", "deprecated"]
    summary: str | None = None
    website_url: str | None = None
    console_url: str | None = None
    docs_url: str | None = None
    default_base_url: str = Field(min_length=1)
    recommended: bool = False
    supported_interfaces: list[ProviderInterface] = Field(min_length=1)
    models: list[ProviderModel] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_models(self) -> "ApiKeyProvider":
        _validate_required_http_url("default_base_url", self.default_base_url)
        _validate_optional_http_url("website_url", self.website_url)
        _validate_optional_http_url("console_url", self.console_url)
        _validate_optional_http_url("docs_url", self.docs_url)
        if self.status != "deprecated" and not self.models:
            raise ValueError(f"provider {self.provider_id} must include at least one model")
        return self


class ProviderInterfaceCatalog(StrictContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=False,
        validate_by_alias=True,
        validate_by_name=False,
    )

    schema_version: Literal["cogeval.provider_interface_catalog.v1"] = Field(
        alias="schema",
    )
    updated_at: str = Field(min_length=1)
    providers: list[ApiKeyProvider] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def schema(self) -> str:
        return self.schema_version

    @model_validator(mode="after")
    def validate_provider_ids(self) -> "ProviderInterfaceCatalog":
        provider_ids = [provider.provider_id for provider in self.providers]
        duplicates = sorted({provider_id for provider_id in provider_ids if provider_ids.count(provider_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate provider_id values: {', '.join(duplicates)}")
        return self


def validate_provider_interface_catalog(payload: object) -> ProviderInterfaceCatalog:
    try:
        return ProviderInterfaceCatalog.model_validate(payload)
    except ValidationError as exc:
        raise ProviderInterfaceCatalogError(
            "catalog_invalid_payload",
            f"Provider interface catalog payload is invalid: {exc}",
            detail=str(exc),
        ) from exc


def _validate_required_http_url(field_name: str, value: str) -> None:
    _validate_optional_http_url(field_name, value)


def _validate_optional_http_url(field_name: str, value: str | None) -> None:
    if value is None:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{field_name} must be an absolute http(s) URL")
