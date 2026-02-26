"""
Aether Voice OS — Package Registry.

Scans a directory for .ath packages, loads them,
and provides a lookup interface. Supports hot-reload
via filesystem watching.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Callable, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from core.errors import IdentityError, PackageNotFoundError
from core.identity.package import AthPackage

logger = logging.getLogger(__name__)


class PackageChangeHandler(FileSystemEventHandler):
    """Handles filesystem events for the packages directory."""

    def __init__(self, registry: AetherRegistry) -> None:
        self._registry = registry

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if event.src_path.endswith("manifest.json"):
            # A package manifest changed, trigger reload
            pkg_path = Path(event.src_path).parent
            self._registry._handle_fs_change(pkg_path)

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            # New directory might be a new package
            self._registry._handle_fs_change(Path(event.src_path))


class AetherRegistry:
    """
    Registry of loaded .ath agent packages.

    Scans a directory, validates each package, and provides
    lookup by name. Supports hot-reloading via watchdog.
    """

    def __init__(
        self, 
        packages_dir: str,
        on_change: Optional[Callable[[str, Optional[AthPackage]], Any]] = None
    ) -> None:
        self._dir = Path(packages_dir)
        self._packages: dict[str, AthPackage] = {}
        self._on_change = on_change
        self._observer: Optional[Observer] = None

    def scan(self) -> int:
        """Scan the packages directory and load all valid packages."""
        if not self._dir.exists():
            self._dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created missing packages directory: %s", self._dir)

        loaded = 0
        for entry in self._dir.iterdir():
            if not entry.is_dir():
                continue
            
            pkg = self.load_package(entry)
            if pkg:
                loaded += 1
        
        return loaded

    def load_package(self, path: Path) -> Optional[AthPackage]:
        """Load a single package from path."""
        if not (path / "manifest.json").exists():
            return None

        try:
            package = AthPackage.load(path)
            self._packages[package.manifest.name] = package
            return package
        except IdentityError as exc:
            logger.error("Failed to load package at %s: %s", path.name, exc)
            return None

    def start_watcher(self) -> None:
        """Start the background filesystem observer."""
        if self._observer:
            return

        self._observer = Observer()
        self._observer.schedule(
            PackageChangeHandler(self),
            str(self._dir),
            recursive=True
        )
        self._observer.start()
        logger.info("📡 ADK Hot-Reloading Active: Watching %s", self._dir)

    def stop_watcher(self) -> None:
        """Stop the background filesystem observer."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def _handle_fs_change(self, path: Path) -> None:
        """Internal handler for filesystem changes."""
        logger.info("Detected change in package directory: %s", path.name)
        # We perform a small delay to let file writes finish
        import time
        time.sleep(0.5)

        old_pkg = None
        # Try to find which package this path belongs to
        for name, pkg in self._packages.items():
            if pkg.path == path:
                old_pkg = pkg
                break
        
        new_pkg = self.load_package(path)
        if self._on_change:
            # Notify callback (e.g. engine) to update tool registration
            pkg_name = new_pkg.manifest.name if new_pkg else (old_pkg.manifest.name if old_pkg else path.name)
            self._on_change(pkg_name, new_pkg)

    def get(self, name: str) -> AthPackage:
        """Get a package by name."""
        pkg = self._packages.get(name)
        if not pkg:
            raise PackageNotFoundError(f"Package '{name}' not found")
        return pkg

    def list_packages(self) -> list[str]:
        return list(self._packages.keys())

    def find_expert(self, query: str) -> Optional[AthPackage]:
        """
        Find the best Expert Soul for a given query based on Expertise Matrix.
        
        Simple keyword-based implementation for now. In Phase 3.3, 
        this will use Vector Search.
        """
        query = query.lower()
        candidates: list[tuple[AthPackage, float]] = []

        for name, pkg in self._packages.items():
            best_domain_score = 0.0
            for domain, score in pkg.manifest.expertise.items():
                if domain.lower() in query:
                    best_domain_score = max(best_domain_score, score)
            
            if best_domain_score > 0:
                candidates.append((pkg, best_domain_score))

        if not candidates:
            return None

        # Return the one with the highest expertise score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    @property
    def count(self) -> int:
        return len(self._packages)
