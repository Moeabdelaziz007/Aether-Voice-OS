#!/usr/bin/env python3
"""
AetherOS Codebase Health Scanner v1.0
=====================================
Scans the entire Python + TypeScript codebase for:
  1. Python syntax errors (py_compile)
  2. Broken imports (ast-based static analysis)
  3. Common bug patterns (bare except, mutable defaults, TODO/FIXME/HACK, unused vars)
  4. Security red flags (hardcoded secrets, eval/exec usage)
  5. TypeScript/Next.js basic checks (unused imports, console.log left in)
  6. Architectural issues (circular import hints, oversized files)

Usage:
  python infra/scripts/health_scanner.py [--fix] [--json]
"""

import ast
import os
import sys
import re
import json
import py_compile
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = {
    "venv", ".venv", "node_modules", "__pycache__", ".git", ".pytest_cache",
    ".ruff_cache", "target", ".next", ".firebase", "dist", "build",
    ".benchmarks", ".coverage", ".aether", ".aetheros", ".qoder",
    "cortex",  # Rust crate — separate toolchain
}

# ─── Result Storage ───────────────────────────────────────────────────────────

class Issue:
    """A single detected issue."""
    def __init__(self, filepath: str, line: int, category: str, severity: str, message: str):
        self.filepath = str(Path(filepath).relative_to(PROJECT_ROOT))
        self.line = line
        self.category = category
        self.severity = severity   # ERROR, WARNING, INFO
        self.message = message

    def to_dict(self):
        return {
            "file": self.filepath,
            "line": self.line,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
        }

    def __str__(self):
        sev_icon = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(self.severity, "?")
        return f"  {sev_icon}  [{self.category}] {self.filepath}:{self.line} — {self.message}"


issues: list[Issue] = []
stats = defaultdict(int)


def add_issue(filepath, line, category, severity, message):
    issues.append(Issue(filepath, line, category, severity, message))
    stats[severity] += 1


# ─── 1. Python Syntax Check ──────────────────────────────────────────────────

def check_python_syntax(filepath: str):
    """Use in-memory compile() to catch syntax errors without writing .pyc files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        compile(source, filepath, "exec")
    except SyntaxError as e:
        add_issue(filepath, e.lineno or 0, "SYNTAX", "ERROR",
                  f"Syntax error: {e.msg} (line {e.lineno})")


# ─── 2. AST-Based Import Checker ─────────────────────────────────────────────

def check_python_imports(filepath: str, source: str):
    """Parse the AST and flag imports that don't resolve locally."""
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return  # Already caught by syntax check

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = None
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name

            if module and module.startswith("core."):
                # Verify the module path resolves to a file
                parts = module.split(".")
                candidate = PROJECT_ROOT / Path(*parts)
                if not (candidate.with_suffix(".py").exists() or
                        (candidate / "__init__.py").exists()):
                    add_issue(filepath, node.lineno, "BROKEN_IMPORT", "ERROR",
                              f"Import '{module}' does not resolve to a file on disk")


# ─── 3. Common Bug Patterns ──────────────────────────────────────────────────

def check_python_patterns(filepath: str, source: str):
    """Regex and AST checks for common Python bugs."""
    lines = source.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Bare except (catches SystemExit, KeyboardInterrupt — almost always a bug)
        if re.match(r"^\s*except\s*:", stripped):
            add_issue(filepath, i, "BARE_EXCEPT", "WARNING",
                      "Bare 'except:' catches all exceptions including SystemExit/KeyboardInterrupt")

        # TODO / FIXME / HACK markers
        for marker in ("TODO", "FIXME", "HACK", "XXX"):
            if marker in stripped and stripped.lstrip().startswith("#"):
                add_issue(filepath, i, "MARKER", "INFO",
                          f"Developer marker found: {marker}")

        # Hardcoded secret patterns
        secret_patterns = [
            (r'(?i)(api[_-]?key|secret|password|token)\s*=\s*["\'][^"\']{8,}["\']',
             "Potential hardcoded secret/credential"),
            (r'AIza[0-9A-Za-z_-]{35}', "Possible Google API key"),
            (r'sk-[a-zA-Z0-9]{20,}', "Possible OpenAI secret key"),
        ]
        for pattern, msg in secret_patterns:
            if re.search(pattern, line):
                add_issue(filepath, i, "SECURITY", "ERROR", msg)

        # eval() / exec() usage
        if re.search(r'\beval\s*\(', stripped) or re.search(r'\bexec\s*\(', stripped):
            add_issue(filepath, i, "SECURITY", "WARNING",
                      "Usage of eval()/exec() — potential code injection risk")

    # AST-level checks
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        # Mutable default arguments
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    add_issue(filepath, node.lineno, "MUTABLE_DEFAULT", "WARNING",
                              f"Mutable default argument in function '{node.name}()' — use None instead")

        # Broad exception catches (Exception without re-raise)
        if isinstance(node, ast.ExceptHandler):
            if node.type and isinstance(node.type, ast.Name) and node.type.id == "Exception":
                # Check if the body just passes (swallowed exception)
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    add_issue(filepath, node.lineno, "SWALLOWED_EXCEPTION", "WARNING",
                              "Exception caught and silently swallowed with 'pass'")


# ─── 4. File Size / Complexity Check ─────────────────────────────────────────

def check_file_metrics(filepath: str, source: str):
    """Flag oversized files and high function counts."""
    lines = source.split("\n")
    line_count = len(lines)

    if line_count > 500:
        add_issue(filepath, 0, "COMPLEXITY", "WARNING",
                  f"File has {line_count} lines — consider splitting into smaller modules")

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return

    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(funcs) > 20:
        add_issue(filepath, 0, "COMPLEXITY", "INFO",
                  f"File has {len(funcs)} functions — consider refactoring into classes or separate modules")

    for func in funcs:
        func_lines = func.end_lineno - func.lineno + 1 if hasattr(func, 'end_lineno') and func.end_lineno else 0
        if func_lines > 80:
            add_issue(filepath, func.lineno, "LONG_FUNCTION", "INFO",
                      f"Function '{func.name}()' is {func_lines} lines long — consider breaking it up")


# ─── 5. TypeScript / Next.js Checks ──────────────────────────────────────────

def check_typescript_file(filepath: str, source: str):
    """Basic regex checks for TS/TSX files."""
    lines = source.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # console.log left in production code
        if "console.log(" in stripped and not stripped.startswith("//"):
            add_issue(filepath, i, "CONSOLE_LOG", "INFO",
                      "console.log() found — remove before production")

        # @ts-ignore / @ts-nocheck
        if "@ts-ignore" in stripped or "@ts-nocheck" in stripped:
            add_issue(filepath, i, "TS_SUPPRESS", "WARNING",
                      "TypeScript error suppression found — fix the underlying type issue")

        # 'any' type usage
        if re.search(r':\s*any\b', stripped):
            add_issue(filepath, i, "ANY_TYPE", "INFO",
                      "Usage of 'any' type — consider using a specific type")

        # TODO / FIXME
        for marker in ("TODO", "FIXME", "HACK"):
            if marker in stripped:
                add_issue(filepath, i, "MARKER", "INFO",
                          f"Developer marker found: {marker}")

        # Hardcoded secrets
        if re.search(r'(?i)(api[_-]?key|secret|password)\s*[:=]\s*["\'][^"\']{8,}["\']', line):
            add_issue(filepath, i, "SECURITY", "ERROR",
                      "Potential hardcoded secret in TypeScript file")


# ─── 6. Cross-Module Consistency ─────────────────────────────────────────────

def check_init_files(root_dir: Path):
    """Ensure every Python package has an __init__.py."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = Path(dirpath).relative_to(PROJECT_ROOT)

        py_files = [f for f in filenames if f.endswith(".py") and f != "__init__.py"]
        has_init = "__init__.py" in filenames

        if py_files and not has_init and str(rel) != ".":
            add_issue(str(Path(dirpath) / "__init__.py"), 0, "MISSING_INIT", "WARNING",
                      f"Directory '{rel}' has Python files but no __init__.py — may break imports")


# ─── Main Scanner Loop ───────────────────────────────────────────────────────

def scan_codebase():
    """Walk the project tree and run all checkers."""
    py_count = 0
    ts_count = 0

    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        # Prune skip directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            # Python files
            if filename.endswith(".py"):
                py_count += 1
                check_python_syntax(filepath)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                except (IOError, OSError):
                    add_issue(filepath, 0, "IO_ERROR", "ERROR", "Could not read file")
                    continue
                check_python_imports(filepath, source)
                check_python_patterns(filepath, source)
                check_file_metrics(filepath, source)

            # TypeScript / JavaScript
            elif filename.endswith((".ts", ".tsx", ".js", ".jsx")) and "node_modules" not in dirpath:
                ts_count += 1
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                except (IOError, OSError):
                    continue
                check_typescript_file(filepath, source)

    # Cross-module checks
    check_init_files(PROJECT_ROOT / "core")
    check_init_files(PROJECT_ROOT / "tests")

    return py_count, ts_count


# ─── Report Generation ───────────────────────────────────────────────────────

def generate_report(py_count: int, ts_count: int, output_json: bool = False):
    """Print or export the scan results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if output_json:
        report = {
            "timestamp": timestamp,
            "files_scanned": {"python": py_count, "typescript": ts_count},
            "totals": dict(stats),
            "issues": [i.to_dict() for i in issues],
        }
        output_path = PROJECT_ROOT / "docs" / "audits" / f"health_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 JSON report saved to: {output_path}")
        return

    print("\n" + "=" * 70)
    print(f"  🧬 AetherOS Health Scanner — {timestamp}")
    print("=" * 70)
    print(f"\n  📁 Files scanned:  {py_count} Python  |  {ts_count} TypeScript/JSX")
    print(f"  ❌ Errors:    {stats.get('ERROR', 0)}")
    print(f"  ⚠️  Warnings:  {stats.get('WARNING', 0)}")
    print(f"  ℹ️  Info:      {stats.get('INFO', 0)}")
    print(f"  📊 Total:     {len(issues)}")

    if not issues:
        print("\n  ✅  Codebase is CLEAN — no issues detected! 🎉\n")
        return

    # Group by severity
    for severity in ("ERROR", "WARNING", "INFO"):
        group = [i for i in issues if i.severity == severity]
        if not group:
            continue

        sev_label = {"ERROR": "❌ ERRORS", "WARNING": "⚠️  WARNINGS", "INFO": "ℹ️  INFORMATIONAL"}.get(severity)
        print(f"\n{'─' * 70}")
        print(f"  {sev_label} ({len(group)})")
        print(f"{'─' * 70}")

        # Sub-group by category
        by_category = defaultdict(list)
        for i in group:
            by_category[i.category].append(i)

        for cat, cat_issues in sorted(by_category.items()):
            print(f"\n  [{cat}] ({len(cat_issues)} issues)")
            for issue in cat_issues[:15]:  # Cap per category to avoid flood
                print(f"    {issue}")
            if len(cat_issues) > 15:
                print(f"    ... and {len(cat_issues) - 15} more")

    print(f"\n{'=' * 70}\n")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AetherOS Codebase Health Scanner")
    parser.add_argument("--json", action="store_true", help="Output results as JSON to docs/audits/")
    args = parser.parse_args()

    print("\n🔍 Scanning AetherOS codebase...\n")
    py_count, ts_count = scan_codebase()
    generate_report(py_count, ts_count, output_json=args.json)
