from __future__ import annotations

from typing import Literal

from pydantic import Field

from cogeval_platform_contracts.provider_capabilities.v1 import ProviderCapabilityCatalog, StrictContractModel


ChangeSeverity = Literal["breaking", "additive", "informational"]


class CompatibilityChange(StrictContractModel):
    code: str = Field(min_length=1)
    severity: ChangeSeverity
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)


class CompatibilityReport(StrictContractModel):
    compatible: bool
    breaking_changes: list[CompatibilityChange] = Field(default_factory=list)
    additive_changes: list[CompatibilityChange] = Field(default_factory=list)
    informational_changes: list[CompatibilityChange] = Field(default_factory=list)


def compare_catalogs(
    old: ProviderCapabilityCatalog,
    new: ProviderCapabilityCatalog,
) -> CompatibilityReport:
    breaking: list[CompatibilityChange] = []
    additive: list[CompatibilityChange] = []
    informational: list[CompatibilityChange] = []

    old_providers = {provider.provider_id: provider for provider in old.providers}
    new_providers = {provider.provider_id: provider for provider in new.providers}

    for provider_id in sorted(old_providers.keys() - new_providers.keys()):
        breaking.append(_change("provider_removed", "breaking", f"providers.{provider_id}", "Provider was removed."))
    for provider_id in sorted(new_providers.keys() - old_providers.keys()):
        additive.append(_change("provider_added", "additive", f"providers.{provider_id}", "Provider was added."))

    for provider_id in sorted(old_providers.keys() & new_providers.keys()):
        _compare_provider(
            provider_id=provider_id,
            old_provider=old_providers[provider_id],
            new_provider=new_providers[provider_id],
            breaking=breaking,
            additive=additive,
            informational=informational,
        )

    return CompatibilityReport(
        compatible=not breaking,
        breaking_changes=breaking,
        additive_changes=additive,
        informational_changes=informational,
    )


def _compare_provider(
    *,
    provider_id: str,
    old_provider,
    new_provider,
    breaking: list[CompatibilityChange],
    additive: list[CompatibilityChange],
    informational: list[CompatibilityChange],
) -> None:
    old_models = {model.model_id: model for model in old_provider.models}
    new_models = {model.model_id: model for model in new_provider.models}
    provider_path = f"providers.{provider_id}"

    for model_id in sorted(old_models.keys() - new_models.keys()):
        breaking.append(_change("model_removed", "breaking", f"{provider_path}.models.{model_id}", "Model was removed."))
    for model_id in sorted(new_models.keys() - old_models.keys()):
        additive.append(_change("model_added", "additive", f"{provider_path}.models.{model_id}", "Model was added."))
    for model_id in sorted(old_models.keys() & new_models.keys()):
        _compare_model(
            model_path=f"{provider_path}.models.{model_id}",
            old_model=old_models[model_id],
            new_model=new_models[model_id],
            breaking=breaking,
            additive=additive,
            informational=informational,
        )


def _compare_model(
    *,
    model_path: str,
    old_model,
    new_model,
    breaking: list[CompatibilityChange],
    additive: list[CompatibilityChange],
    informational: list[CompatibilityChange],
) -> None:
    old_capabilities = old_model.capabilities
    new_capabilities = new_model.capabilities

    for capability_name in sorted(old_capabilities.keys() - new_capabilities.keys()):
        breaking.append(
            _change(
                "capability_removed",
                "breaking",
                f"{model_path}.capabilities.{capability_name}",
                "Capability was removed.",
            )
        )
    for capability_name in sorted(new_capabilities.keys() - old_capabilities.keys()):
        additive.append(
            _change(
                "capability_added",
                "additive",
                f"{model_path}.capabilities.{capability_name}",
                "Capability was added.",
            )
        )

    for capability_name in sorted(old_capabilities.keys() & new_capabilities.keys()):
        old_capability = old_capabilities[capability_name]
        new_capability = new_capabilities[capability_name]
        capability_path = f"{model_path}.capabilities.{capability_name}"
        if old_capability.supported and not new_capability.supported:
            breaking.append(
                _change("capability_disabled", "breaking", capability_path, "Capability changed from supported to unsupported.")
            )
        if not old_capability.supported and new_capability.supported:
            additive.append(_change("capability_enabled", "additive", capability_path, "Capability changed to supported."))

        old_values = set(old_capability.values)
        new_values = set(new_capability.values)
        for value in sorted(old_values - new_values):
            breaking.append(
                _change(
                    "capability_value_removed",
                    "breaking",
                    f"{capability_path}.values.{value}",
                    "Capability value was removed.",
                )
            )
        for value in sorted(new_values - old_values):
            additive.append(
                _change(
                    "capability_value_added",
                    "additive",
                    f"{capability_path}.values.{value}",
                    "Capability value was added.",
                )
            )
        if old_capability.default != new_capability.default:
            informational.append(
                _change(
                    "capability_default_changed",
                    "informational",
                    f"{capability_path}.default",
                    "Capability default changed.",
                )
            )


def _change(code: str, severity: ChangeSeverity, path: str, message: str) -> CompatibilityChange:
    return CompatibilityChange(code=code, severity=severity, path=path, message=message)

