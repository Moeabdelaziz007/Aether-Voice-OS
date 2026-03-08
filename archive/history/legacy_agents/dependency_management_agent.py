"""
📦 DependencyManagementAgent
Manages project dependencies, checks for outdated packages
and security vulnerabilities. Suggests updates for Aether Voice OS.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Information about a single dependency."""

    name: str
    current_version: str
    latest_version: Optional[str] = None
    is_outdated: bool = False
    update_type: Optional[str] = None  # major, minor, patch
    security_advisory: Optional[str] = None
    is_dev_dependency: bool = False
    source: str = "pip"  # pip, npm, cargo


@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability in a dependency."""

    package: str
    vulnerability_id: str
    severity: str  # critical, high, medium, low
    description: str
    fixed_in: Optional[str] = None
    cve_id: Optional[str] = None


@dataclass
class DependencyReport:
    """Complete dependency management report."""

    dependencies: List[DependencyInfo] = field(default_factory=list)
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    outdated_count: int = 0
    security_issues: int = 0
    update_suggestions: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    timestamp: str = ""


class DependencyManagementAgent:
    """Manages and audits project dependencies."""

    def __init__(self):
        self.name = "DependencyManagementAgent"
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.report = DependencyReport()

        # Configuration files to check
        self.python_deps_files = ["requirements.txt", "pyproject.toml"]
        self.node_deps_files = ["package.json", "package-lock.json"]
        self.rust_deps_files = ["Cargo.toml", "Cargo.lock"]

    async def run(self) -> Dict[str, Any]:
        """Execute dependency management tasks."""
        self.logger.info("📦 Starting dependency management...")
        results = {
            "dependencies_checked": 0,
            "outdated_packages": 0,
            "security_vulnerabilities": 0,
            "updates_available": [],
            "critical_updates": [],
            "errors": [],
        }

        try:
            # Check Python dependencies
            python_deps = await self._check_python_dependencies()
            results["dependencies_checked"] += len(python_deps)

            # Check Node.js dependencies (if applicable)
            node_deps = await self._check_node_dependencies()
            results["dependencies_checked"] += len(node_deps)

            # Check Rust dependencies (if applicable)
            rust_deps = await self._check_rust_dependencies()
            results["dependencies_checked"] += len(rust_deps)

            # Run security audit
            await self._run_security_audit()

            # Detect dependency conflicts
            self._detect_conflicts()

            # Generate update suggestions
            self._generate_update_suggestions()

            # Compile results
            results["outdated_packages"] = self.report.outdated_count
            results["security_vulnerabilities"] = len(self.report.vulnerabilities)
            results["updates_available"] = [
                f"{d.name}: {d.current_version} → {d.latest_version}"
                for d in self.report.dependencies
                if d.is_outdated and d.update_type in ["minor", "patch"]
            ][:10]
            results["critical_updates"] = [
                f"{d.name}: {d.current_version} → {d.latest_version}"
                for d in self.report.dependencies
                if d.is_outdated and d.update_type == "major"
            ][:5]
            results["suggestions"] = self.report.update_suggestions[:5]
            results["status"] = "success"

            self.logger.info(
                f"✅ Dependency check completed: "
                f"{results['outdated_packages']} outdated, "
                f"{results['security_vulnerabilities']} vulnerabilities"
            )

        except Exception as e:
            self.logger.error(f"💥 DependencyManagementAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"

        self.report.timestamp = datetime.now().isoformat()
        return results

    async def _check_python_dependencies(self) -> List[DependencyInfo]:
        """Check Python dependencies for updates."""
        dependencies = []

        try:
            # Parse requirements.txt
            req_path = Path("requirements.txt")
            if req_path.exists():
                deps = self._parse_requirements_txt(req_path)
                dependencies.extend(deps)

            # Parse pyproject.toml
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                deps = self._parse_pyproject_toml(pyproject_path)
                dependencies.extend(deps)

            # Check for outdated packages using pip
            outdated = await self._get_pip_outdated()

            # Update dependency info with latest versions
            for dep in dependencies:
                if dep.name in outdated:
                    dep.latest_version = outdated[dep.name]["latest"]
                    dep.is_outdated = True
                    dep.update_type = self._determine_update_type(
                        dep.current_version, dep.latest_version
                    )
                    self.report.outdated_count += 1

            self.report.dependencies.extend(dependencies)

        except Exception as e:
            self.logger.warning(f"Failed to check Python dependencies: {str(e)}")

        return dependencies

    def _parse_requirements_txt(self, path: Path) -> List[DependencyInfo]:
        """Parse requirements.txt file."""
        dependencies = []
        content = path.read_text(encoding="utf-8")

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse package==version or package>=version
            match = re.match(r"^([a-zA-Z0-9_-]+)[=<>!~]+([0-9.]+)", line)
            if match:
                dependencies.append(
                    DependencyInfo(
                        name=match.group(1).lower(),
                        current_version=match.group(2),
                        source="pip",
                    )
                )
            elif re.match(r"^[a-zA-Z0-9_-]+$", line):
                dependencies.append(
                    DependencyInfo(
                        name=line.lower(), current_version="latest", source="pip"
                    )
                )

        return dependencies

    def _parse_pyproject_toml(self, path: Path) -> List[DependencyInfo]:
        """Parse pyproject.toml for dependencies."""
        dependencies = []

        try:
            content = path.read_text(encoding="utf-8")

            # Simple regex parsing for dependencies section
            in_deps = False
            for line in content.split("\n"):
                if (
                    "[project.dependencies]" in line
                    or "[tool.poetry.dependencies]" in line
                ):
                    in_deps = True
                    continue
                elif line.startswith("[") and in_deps:
                    in_deps = False
                    continue

                if in_deps and "=" in line:
                    # Parse "package = version" or "package = {version = ...}"
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        name = parts[0].strip().strip('"')
                        version_str = parts[1].strip().strip('"').strip("{").strip("}")

                        # Extract version number
                        version_match = re.search(r"[0-9]+\.[0-9]+", version_str)
                        version = version_match.group(0) if version_match else "unknown"

                        if name and name != "python":
                            dependencies.append(
                                DependencyInfo(
                                    name=name.lower(),
                                    current_version=version,
                                    source="pip",
                                )
                            )

        except Exception as e:
            self.logger.warning(f"Failed to parse pyproject.toml: {str(e)}")

        return dependencies

    async def _get_pip_outdated(self) -> Dict[str, Dict]:
        """Get outdated pip packages."""
        outdated = {}

        try:
            cmd = ["pip", "list", "--outdated", "--format=json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0 and stdout:
                packages = json.loads(stdout.decode())
                for pkg in packages:
                    outdated[pkg["name"].lower()] = {
                        "current": pkg["version"],
                        "latest": pkg["latest_version"],
                    }

        except FileNotFoundError:
            self.logger.info("pip not available")
        except Exception as e:
            self.logger.warning(f"Failed to check pip outdated: {str(e)}")

        return outdated

    async def _check_node_dependencies(self) -> List[DependencyInfo]:
        """Check Node.js dependencies for updates."""
        dependencies = []

        # Check multiple package.json locations
        package_paths = [Path("package.json"), Path("apps/portal/package.json")]

        for package_path in package_paths:
            if not package_path.exists():
                continue

            try:
                content = json.loads(package_path.read_text(encoding="utf-8"))

                # Parse dependencies
                for dep_type in ["dependencies", "devDependencies"]:
                    if dep_type in content:
                        for name, version in content[dep_type].items():
                            # Clean version string
                            clean_version = re.sub(r"^[\^~>=<]", "", str(version))
                            dependencies.append(
                                DependencyInfo(
                                    name=name,
                                    current_version=clean_version,
                                    is_dev_dependency=(dep_type == "devDependencies"),
                                    source="npm",
                                )
                            )

                # Check for outdated using npm (if available)
                outdated = await self._get_npm_outdated(package_path.parent)

                for dep in dependencies:
                    if dep.name in outdated:
                        dep.latest_version = outdated[dep.name]
                        dep.is_outdated = True
                        dep.update_type = self._determine_update_type(
                            dep.current_version, dep.latest_version
                        )
                        self.report.outdated_count += 1

            except Exception as e:
                self.logger.warning(f"Failed to parse {package_path}: {str(e)}")

        self.report.dependencies.extend(dependencies)
        return dependencies

    async def _get_npm_outdated(self, cwd: Path) -> Dict[str, str]:
        """Get outdated npm packages."""
        outdated = {}

        try:
            cmd = ["npm", "outdated", "--json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if stdout:
                packages = json.loads(stdout.decode())
                for name, info in packages.items():
                    if "latest" in info:
                        outdated[name] = info["latest"]

        except FileNotFoundError:
            self.logger.info("npm not available")
        except Exception as e:
            self.logger.warning(f"npm outdated check failed: {str(e)}")

        return outdated

    async def _check_rust_dependencies(self) -> List[DependencyInfo]:
        """Check Rust dependencies for updates."""
        dependencies = []

        # Check Cargo.toml files
        cargo_paths = [
            Path("cortex/Cargo.toml"),
            Path("apps/portal/src-tauri/Cargo.toml"),
        ]

        for cargo_path in cargo_paths:
            if not cargo_path.exists():
                continue

            try:
                content = cargo_path.read_text(encoding="utf-8")

                in_deps = False
                for line in content.split("\n"):
                    if "[dependencies]" in line or "[dev-dependencies]" in line:
                        in_deps = True
                        continue
                    elif line.startswith("[") and in_deps:
                        in_deps = False
                        continue

                    if in_deps and "=" in line:
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            version_str = parts[1].strip().strip('"')

                            # Extract version
                            version_match = re.search(r"[0-9]+\.[0-9]+", version_str)
                            version = (
                                version_match.group(0) if version_match else "unknown"
                            )

                            if name and not name.startswith("#"):
                                dependencies.append(
                                    DependencyInfo(
                                        name=name,
                                        current_version=version,
                                        source="cargo",
                                    )
                                )

            except Exception as e:
                self.logger.warning(f"Failed to parse {cargo_path}: {str(e)}")

        # Check for outdated using cargo (if available)
        try:
            cmd = ["cargo", "outdated", "--format=json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd="cortex",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0 and stdout:
                outdated_data = json.loads(stdout.decode())
                outdated_map = {
                    pkg["name"]: pkg["latest"]
                    for pkg in outdated_data.get("dependencies", [])
                }

                for dep in dependencies:
                    if dep.name in outdated_map:
                        dep.latest_version = outdated_map[dep.name]
                        dep.is_outdated = True
                        dep.update_type = self._determine_update_type(
                            dep.current_version, dep.latest_version
                        )
                        self.report.outdated_count += 1

        except FileNotFoundError:
            self.logger.info("cargo not available")
        except Exception as e:
            self.logger.warning(f"cargo outdated check failed: {str(e)}")

        self.report.dependencies.extend(dependencies)
        return dependencies

    async def _run_security_audit(self) -> None:
        """Run security audit on dependencies."""
        # Python security audit using pip-audit or safety
        await self._audit_python_security()

        # Node.js security audit using npm audit
        await self._audit_node_security()

        # Rust security audit using cargo audit
        await self._audit_rust_security()

    async def _audit_python_security(self) -> None:
        """Audit Python dependencies for security vulnerabilities."""
        try:
            # Try pip-audit first
            cmd = ["pip-audit", "--format=json", "--desc=on"]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0 and stdout:
                vulns = json.loads(stdout.decode())
                for vuln in vulns:
                    self.report.vulnerabilities.append(
                        SecurityVulnerability(
                            package=vuln.get("name", "unknown"),
                            vulnerability_id=vuln.get("id", "unknown"),
                            severity=vuln.get("severity", "unknown"),
                            description=vuln.get("description", ""),
                            fixed_in=vuln.get("fix_versions", [None])[0],
                            cve_id=vuln.get("cve", None),
                        )
                    )

        except FileNotFoundError:
            # Try safety as fallback
            try:
                cmd = ["safety", "check", "--json"]
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                if stdout:
                    result = json.loads(stdout.decode())
                    for vuln in result.get("vulnerabilities", []):
                        self.report.vulnerabilities.append(
                            SecurityVulnerability(
                                package=vuln.get("package_name", "unknown"),
                                vulnerability_id=vuln.get(
                                    "vulnerability_id", "unknown"
                                ),
                                severity=vuln.get("severity", "unknown"),
                                description=vuln.get("advisory", ""),
                                cve_id=vuln.get("cve", None),
                            )
                        )

            except FileNotFoundError:
                self.logger.info(
                    "No Python security audit tool available (pip-audit or safety)"
                )
            except Exception as e:
                self.logger.warning(f"Safety check failed: {str(e)}")
        except Exception as e:
            self.logger.warning(f"pip-audit failed: {str(e)}")

    async def _audit_node_security(self) -> None:
        """Audit Node.js dependencies for security vulnerabilities."""
        package_dirs = [Path("."), Path("apps/portal")]

        for pkg_dir in package_dirs:
            if not (pkg_dir / "package.json").exists():
                continue

            try:
                cmd = ["npm", "audit", "--json"]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=str(pkg_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()

                if stdout:
                    audit_result = json.loads(stdout.decode())
                    advisories = audit_result.get("advisories", {})

                    for adv_id, adv in advisories.items():
                        self.report.vulnerabilities.append(
                            SecurityVulnerability(
                                package=adv.get("module_name", "unknown"),
                                vulnerability_id=str(adv_id),
                                severity=adv.get("severity", "unknown"),
                                description=adv.get("title", ""),
                                fixed_in=adv.get("patched_versions", None),
                                cve_id=adv.get("cves", [None])[0]
                                if adv.get("cves")
                                else None,
                            )
                        )

            except FileNotFoundError:
                self.logger.info("npm not available for security audit")
            except Exception as e:
                self.logger.warning(f"npm audit failed in {pkg_dir}: {str(e)}")

    async def _audit_rust_security(self) -> None:
        """Audit Rust dependencies for security vulnerabilities."""
        if not Path("cortex/Cargo.toml").exists():
            return

        try:
            cmd = ["cargo", "audit", "--json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd="cortex",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if stdout:
                audit_result = json.loads(stdout.decode())
                for vuln in audit_result.get("vulnerabilities", {}).get("list", []):
                    self.report.vulnerabilities.append(
                        SecurityVulnerability(
                            package=vuln.get("package", {}).get("name", "unknown"),
                            vulnerability_id=vuln.get("advisory", {}).get(
                                "id", "unknown"
                            ),
                            severity=vuln.get("advisory", {}).get(
                                "severity", "unknown"
                            ),
                            description=vuln.get("advisory", {}).get("title", ""),
                            cve_id=vuln.get("advisory", {}).get("cvss", None),
                        )
                    )

        except FileNotFoundError:
            self.logger.info("cargo-audit not available")
        except Exception as e:
            self.logger.warning(f"cargo audit failed: {str(e)}")

    def _determine_update_type(self, current: str, latest: str) -> str:
        """Determine if update is major, minor, or patch."""
        try:
            current_parts = [int(x) for x in re.findall(r"\d+", current)[:3]]
            latest_parts = [int(x) for x in re.findall(r"\d+", latest)[:3]]

            # Pad to 3 parts
            while len(current_parts) < 3:
                current_parts.append(0)
            while len(latest_parts) < 3:
                latest_parts.append(0)

            if latest_parts[0] > current_parts[0]:
                return "major"
            elif latest_parts[1] > current_parts[1]:
                return "minor"
            elif latest_parts[2] > current_parts[2]:
                return "patch"

        except (ValueError, IndexError):
            pass

        return "unknown"

    def _detect_conflicts(self) -> None:
        """Detect potential dependency conflicts."""
        # Group dependencies by name
        dep_versions = {}
        for dep in self.report.dependencies:
            if dep.name not in dep_versions:
                dep_versions[dep.name] = []
            dep_versions[dep.name].append((dep.current_version, dep.source))

        # Find conflicts (same package, different versions)
        for name, versions in dep_versions.items():
            unique_versions = set(v[0] for v in versions)
            if len(unique_versions) > 1:
                sources = [v[1] for v in versions]
                self.report.conflicts.append(
                    f"{name}: conflicting versions {unique_versions} in {set(sources)}"
                )

    def _generate_update_suggestions(self) -> None:
        """Generate prioritized update suggestions."""
        suggestions = []

        # Critical: Security vulnerabilities
        critical_vulns = [
            v for v in self.report.vulnerabilities if v.severity == "critical"
        ]
        if critical_vulns:
            suggestions.append(
                f"🚨 CRITICAL: {len(critical_vulns)} critical security vulnerabilities found! "
                f"Update immediately: {', '.join(v.package for v in critical_vulns[:3])}"
            )

        # High priority: Major version updates with security fixes
        major_updates = [
            d
            for d in self.report.dependencies
            if d.is_outdated and d.update_type == "major"
        ]
        if major_updates:
            suggestions.append(
                f"⬆️ {len(major_updates)} major version updates available. "
                f"Review breaking changes: {', '.join(d.name for d in major_updates[:5])}"
            )

        # Medium priority: Minor/patch updates
        safe_updates = [
            d
            for d in self.report.dependencies
            if d.is_outdated and d.update_type in ["minor", "patch"]
        ]
        if safe_updates:
            suggestions.append(
                f"📦 {len(safe_updates)} safe updates available (minor/patch). "
                f"Run: pip install --upgrade {' '.join(d.name for d in safe_updates[:10])}"
            )

        # Conflicts
        if self.report.conflicts:
            suggestions.append(
                f"⚠️ {len(self.report.conflicts)} dependency conflicts detected. "
                f"Review: {self.report.conflicts[0]}"
            )

        # General recommendations for Aether Voice OS
        suggestions.extend(
            [
                "🎵 For audio processing, ensure numpy and scipy are up-to-date for performance.",
                "🔒 Run security audits regularly: pip-audit && npm audit && cargo audit",
                "📌 Consider pinning critical dependencies for reproducible builds.",
                "🧹 Remove unused dependencies to reduce attack surface.",
            ]
        )

        self.report.update_suggestions = suggestions

    async def update_dependencies(
        self,
        packages: Optional[List[str]] = None,
        update_type: str = "safe",  # safe, all, specific
    ) -> Dict[str, Any]:
        """Update dependencies (safe updates only by default)."""
        results = {"updated": [], "failed": [], "skipped": []}

        deps_to_update = []

        if update_type == "safe":
            deps_to_update = [
                d
                for d in self.report.dependencies
                if d.is_outdated and d.update_type in ["minor", "patch"]
            ]
        elif update_type == "all":
            deps_to_update = [d for d in self.report.dependencies if d.is_outdated]
        elif packages:
            deps_to_update = [
                d
                for d in self.report.dependencies
                if d.name in packages and d.is_outdated
            ]

        for dep in deps_to_update:
            try:
                if dep.source == "pip":
                    cmd = ["pip", "install", "--upgrade", dep.name]
                elif dep.source == "npm":
                    cmd = ["npm", "install", f"{dep.name}@latest"]
                elif dep.source == "cargo":
                    cmd = ["cargo", "update", "-p", dep.name]
                else:
                    results["skipped"].append(dep.name)
                    continue

                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()

                if proc.returncode == 0:
                    results["updated"].append(f"{dep.name} → {dep.latest_version}")
                else:
                    results["failed"].append(dep.name)

            except Exception as e:
                results["failed"].append(f"{dep.name}: {str(e)}")

        return results

    def get_report(self) -> DependencyReport:
        """Get the complete dependency report."""
        return self.report

    def export_report_json(self) -> Dict[str, Any]:
        """Export report as JSON-serializable dictionary."""
        return {
            "timestamp": self.report.timestamp,
            "dependencies": [
                {
                    "name": d.name,
                    "current": d.current_version,
                    "latest": d.latest_version,
                    "outdated": d.is_outdated,
                    "update_type": d.update_type,
                    "source": d.source,
                }
                for d in self.report.dependencies
            ],
            "vulnerabilities": [
                {
                    "package": v.package,
                    "id": v.vulnerability_id,
                    "severity": v.severity,
                    "description": v.description,
                    "fixed_in": v.fixed_in,
                    "cve": v.cve_id,
                }
                for v in self.report.vulnerabilities
            ],
            "conflicts": self.report.conflicts,
            "suggestions": self.report.update_suggestions,
            "summary": {
                "total": len(self.report.dependencies),
                "outdated": self.report.outdated_count,
                "vulnerabilities": len(self.report.vulnerabilities),
            },
        }
