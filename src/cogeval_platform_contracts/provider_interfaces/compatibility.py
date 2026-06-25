from __future__ import annotations

from typing import Literal

from pydantic import Field

from cogeval_platform_contracts.provider_interfaces.v1 import ProviderInterfaceCatalog, StrictContractModel


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
    old: ProviderInterfaceCatalog,
    new: ProviderInterfaceCatalog,
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
    provider_path = f"providers.{provider_id}"
    for field_name in ("default_base_url", "default_env_key", "model_provider"):
        if getattr(old_provider, field_name) != getattr(new_provider, field_name):
            informational.append(
                _change(
                    f"provider_{field_name}_changed",
                    "informational",
                    f"{provider_path}.{field_name}",
                    f"Provider {field_name} changed.",
                )
            )
    _compare_interfaces(
        provider_path=provider_path,
        old_interfaces={item.interface: item for item in old_provider.supported_interfaces},
        new_interfaces={item.interface: item for item in new_provider.supported_interfaces},
        breaking=breaking,
        additive=additive,
        informational=informational,
    )
    _compare_models(
        provider_path=provider_path,
        old_models={model.model_option_id: model for model in old_provider.models},
        new_models={model.model_option_id: model for model in new_provider.models},
        breaking=breaking,
        additive=additive,
        informational=informational,
    )


def _compare_interfaces(
    *,
    provider_path: str,
    old_interfaces,
    new_interfaces,
    breaking: list[CompatibilityChange],
    additive: list[CompatibilityChange],
    informational: list[CompatibilityChange],
) -> None:
    for interface in sorted(old_interfaces.keys() - new_interfaces.keys()):
        breaking.append(
            _change("interface_removed", "breaking", f"{provider_path}.interfaces.{interface}", "Interface was removed.")
        )
    for interface in sorted(new_interfaces.keys() - old_interfaces.keys()):
        additive.append(
            _change("interface_added", "additive", f"{provider_path}.interfaces.{interface}", "Interface was added.")
        )
    for interface in sorted(old_interfaces.keys() & new_interfaces.keys()):
        old = old_interfaces[interface]
        new = new_interfaces[interface]
        interface_path = f"{provider_path}.interfaces.{interface}"
        for field_name in ("default_base_url", "default_model_prefix"):
            if getattr(old, field_name) != getattr(new, field_name):
                informational.append(
                    _change(
                        f"interface_{field_name}_changed",
                        "informational",
                        f"{interface_path}.{field_name}",
                        f"Interface {field_name} changed.",
                    )
                )


def _compare_models(
    *,
    provider_path: str,
    old_models,
    new_models,
    breaking: list[CompatibilityChange],
    additive: list[CompatibilityChange],
    informational: list[CompatibilityChange],
) -> None:
    for model_id in sorted(old_models.keys() - new_models.keys()):
        breaking.append(_change("model_removed", "breaking", f"{provider_path}.models.{model_id}", "Model was removed."))
    for model_id in sorted(new_models.keys() - old_models.keys()):
        additive.append(_change("model_added", "additive", f"{provider_path}.models.{model_id}", "Model was added."))
    for model_id in sorted(old_models.keys() & new_models.keys()):
        old_supported = set(old_models[model_id].supported_interfaces)
        new_supported = set(new_models[model_id].supported_interfaces)
        model_path = f"{provider_path}.models.{model_id}"
        for interface in sorted(old_supported - new_supported):
            breaking.append(
                _change(
                    "model_interface_removed",
                    "breaking",
                    f"{model_path}.supported_interfaces.{interface}",
                    "Model support for interface was removed.",
                )
            )
        for interface in sorted(new_supported - old_supported):
            additive.append(
                _change(
                    "model_interface_added",
                    "additive",
                    f"{model_path}.supported_interfaces.{interface}",
                    "Model support for interface was added.",
                )
            )


def _change(code: str, severity: ChangeSeverity, path: str, message: str) -> CompatibilityChange:
    return CompatibilityChange(code=code, severity=severity, path=path, message=message)

