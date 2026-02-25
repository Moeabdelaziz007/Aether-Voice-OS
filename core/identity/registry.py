"""
Aether Voice OS — Package Registry.

Scans a directory for .ath packages, loads them,
and provides a lookup interface. Supports hot-reload
via filesystem watching.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from core.errors import IdentityError, PackageNotFoundError
from core.identity.package import AthPackage

logger = logging.getLogger(__name__)


class AetherRegistry:
    """
    Registry of loaded .ath agent packages.

    Scans a directory, validates each package, and provides
    lookup by name. Corrupt packages are logged and skipped
    (fail-open for resilience).
    """

    def __init__(self, packages_dir: str) -> None:
        self._dir = Path(packages_dir)
        self._packages: dict[str, AthPackage] = {}

    def scan(self) -> int:
        """
        Scan the packages directory and load all valid packages.

        Returns the number of successfully loaded packages.
        """
        if not self._dir.exists():
            logger.warning("Packages directory does not exist: %s", self._dir)
            return 0

        loaded = 0
        for entry in self._dir.iterdir():
            if not entry.is_dir():
                continue
            if not (entry / "manifest.json").exists():
                continue

            try:
                package = AthPackage.load(entry)
                self._packages[package.manifest.name] = package
                loaded += 1
            except IdentityError as exc:
                # Log and skip corrupt packages — don't crash the system
                logger.error(
                    "Failed to load package %s: %s", entry.name, exc
                )

        logger.info(
            "Registry scan complete: %d/%d packages loaded",
            loaded,
            loaded + sum(1 for _ in self._dir.iterdir() if _.is_dir()) - loaded,
        )
        return loaded

    def get(self, name: str) -> AthPackage:
        """Get a package by name. Raises PackageNotFoundError if not found."""
        pkg = self._packages.get(name)
        if not pkg:
            raise PackageNotFoundError(
                f"Package '{name}' not found in registry",
                context={"available": list(self._packages.keys())},
            )
        return pkg

    def get_optional(self, name: str) -> Optional[AthPackage]:
        """Get a package by name, returning None if not found."""
        return self._packages.get(name)

    def list_packages(self) -> list[str]:
        """List all loaded package names."""
        return list(self._packages.keys())

    @property
    def count(self) -> int:
        return len(self._packages)
