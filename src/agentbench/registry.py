"""Provider registration and lookup."""
# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .models import ProviderConfig
from .providers import Provider


class ProviderRegistryError(LookupError):
    """Raised when a provider cannot be selected."""


@dataclass(frozen=True)
class RegisteredProvider:
    config: ProviderConfig
    provider: Provider


class ProviderRegistry:
    """Keeps the active provider set small and explicit."""

    def __init__(self, providers: Iterable[RegisteredProvider] = ()) -> None:
        self._providers: dict[str, RegisteredProvider] = {}
        for registered in providers:
            self.add(registered)

    def add(self, registered: RegisteredProvider) -> None:
        name = registered.config.name.strip()
        if not name:
            raise ValueError("provider name cannot be empty")
        if name in self._providers:
            raise ProviderRegistryError(f"provider already registered: {name}")
        self._providers[name] = registered

    def replace(self, registered: RegisteredProvider) -> None:
        name = registered.config.name.strip()
        if not name:
            raise ValueError("provider name cannot be empty")
        self._providers[name] = registered

    def get(self, name: str) -> RegisteredProvider:
        try:
            registered = self._providers[name]
        except KeyError as exc:
            raise ProviderRegistryError(f"unknown provider: {name}") from exc
        if not registered.config.enabled:
            raise ProviderRegistryError(f"provider is disabled: {name}")
        return registered

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def enabled(self) -> list[RegisteredProvider]:
        return [item for item in self._providers.values() if item.config.enabled]
