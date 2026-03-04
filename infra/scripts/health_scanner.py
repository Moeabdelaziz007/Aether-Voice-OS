#!/usr/bin/env python3
"""
AetherOS Codebase Health Scanner & Self-Improvement Engine v2.0
===============================================================
Scans the entire Python + TypeScript codebase for:
  1. Python syntax errors
  2. Broken imports
  3. Common bug patterns
  4. Security red flags
  5. TypeScript/Next.js basic checks
  6. Architectural issues

*NEW* Features:
- Attached actionable solutions for every detected issue.
- Meta-Level Architecture Suggestions (Self-Improvement loop).
- Auto-fix generation (`suggested_fixes.sh`).

Usage:
  python infra/scripts/health_scanner.py [--json] [--auto-fix]
"""

import argparse
import ast
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = {
    "venv", ".venv", "node_modules", "__pycache__", ".git", ".pytest_cache",
    ".ruff_cache", "target", ".next", ".firebase", "dist", "build",
    ".benchmarks", ".coverage", ".aether", ".aetheros", ".qoder",
    "cortex",  # Rust crate  — separate toolchain
}

FIX_SCRIPT_PATH = PROJECT_ROOT / "docs" / "audits" / "suggested_fixes.sh"

# ─── Result Storage ───────────────────────────────────────────────────────────

class Issue:
    """A single detected issue with an actionable solution."""
    def __init__(self, filepath: str, line: int, category: str, severity: str, message: str, solution: str):
        self.filepath = str(Path(filepath).relative_to(PROJECT_ROOT)) if Path(filepath).is_absolute() else filepath
        self.line = line
        self.category = category
        self.severity = severity   # ERROR, WARNING, INFO
        self.message = message
        self.solution = solution

    def to_dict(self):
        return {
            "file": self.filepath,
            "line": self.line,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "solution": self.solution,
        }

    def __str__(self):
        sev_icon = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(self.severity, "?")
        return f"  {sev_icon}  [{self.category}] {self.filepath}:{self.line}\n      └─ 🛑 Issue: {self.message}\n      └─ 💡 Fix: {self.solution}"


issues: list[Issue] = []
stats = defaultdict(int)
auto_fix_commands = []


def add_issue(filepath, line, category, severity, message, solution=""):
    issues.append(Issue(filepath, line, category, severity, message, solution))
    stats[severity] += 1


# ─── 1. Python Syntax Check ──────────────────────────────────────────────────

def check_python_syntax(filepath: str):
    """"Use in-memory compile() to catch syntax errors without writing .pyc files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        compile(source, filepath, "exec")
    except SyntaxError as e:
        add_issue(filepath, e.lineno or 0, "SYNTAX", "ERROR",
                  f"Syntax error: {e.msg}", 
                  "Fix the syntax typo at the specified line before re-running.")


# ─── 2. AST-Based Import Checker ─────────────────────────────────────────────

def check_python_imports(filepath: str, source: str):
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = None
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name

            if module and module.startswith("core."):
                parts = module.split(".")
                candidate = PROJECT_ROOT / Path(*parts)
                if not (candidate.with_suffix(".py").exists() or
                        (candidate / "__init__.py").exists()):
                    add_issue(filepath, node.lineno, "BROKEN_IMPORT", "ERROR",
                              f"Import '{module}' does not resolve to a file on disk",
                              f"Check if '{module}' was renamed or deleted. Update the import path.")


# ─── 3. Common Bug Patterns ──────────────────────────────────────────────────

def check_python_patterns(filepath: str, source: str):
    lines = source.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if re.match(r"^\s*except\s*:", stripped):
            add_issue(filepath, i, "BARE_EXCEPT", "WARNING",
                      "Bare 'except:' catches all exceptions including SystemExit",
                      "Change to 'except Exception as e:' to only catch standard exceptions.")

        for marker in ("TODO", "FIXME", "HACK", "XXX"):
            if marker in stripped and stripped.lstrip().startswith("#"):
                add_issue(filepath, i, "MARKER", "INFO",
                          f"Developer marker found: {marker}",
                          "Review and resolve the inline technical debt/todo item.")

        secret_patterns = [
            (r'(?i)(api[_-]?key|secret|password|token)\s*=\s*["\'][^"\']{8,}["\']', "Potential hardcoded secret"),
            (r'AIza[0-9A-Za-z_-]{35}', "Possible Google API key"),
            (r'sk-[a-zA-Z0-9]{20,}', "Possible OpenAI secret key"),
        ]
        for pattern, msg in secret_patterns:
            if re.search(pattern, line):
                add_issue(filepath, i, "SECURITY", "ERROR", msg,
                          "Move secrets to environment variables (.env) and load via os.getenv().")

        if re.search(r'\beval\s*\(', stripped) or re.search(r'\bexec\s*\(', stripped):
            add_issue(filepath, i, "SECURITY", "WARNING",
                      "Usage of eval()/exec()",
                      "Avoid eval(). If parsing JSON, use json.loads(). If parsing literals, use ast.literal_eval().")

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    add_issue(filepath, node.lineno, "MUTABLE_DEFAULT", "WARNING",
                              f"Mutable default argument in '{node.name}()'",
                              "Change to 'arg=None', and set 'arg = arg or []' inside the function body.")

        if isinstance(node, ast.ExceptHandler):
            if node.type and isinstance(node.type, ast.Name) and node.type.id == "Exception":
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    add_issue(filepath, node.lineno, "SWALLOWED_EXCEPTION", "WARNING",
                              "Exception caught and silently swallowed with 'pass'",
                              "Log the exception via logging.warning() or logger.error() instead of quietly passing.")


# ─── 4. File Size / Complexity Check ─────────────────────────────────────────

def check_file_metrics(filepath: str, source: str):
    lines = source.split("\n")
    line_count = len(lines)

    if line_count > 500:
        add_issue(filepath, 0, "COMPLEXITY", "WARNING",
                  f"File has {line_count} lines",
                  "Split this file into smaller sub-modules (e.g., separate Models from Handlers/Business Logic).")

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return

    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(funcs) > 20:
        add_issue(filepath, 0, "COMPLEXITY", "INFO",
                  f"File has {len(funcs)} functions",
                  "Consider refactoring related functions into a Class to encapsulate state and logic.")

    for func in funcs:
        func_lines = func.end_lineno - func.lineno + 1 if hasattr(func, 'end_lineno') and func.end_lineno else 0
        if func_lines > 80:
            add_issue(filepath, func.lineno, "LONG_FUNCTION", "INFO",
                      f"Function '{func.name}()' is {func_lines} lines long",
                      "Extract pure, stateless parts of this function into smaller helper generic functions.")


# ─── 5. TypeScript / Next.js Checks ──────────────────────────────────────────

def check_typescript_file(filepath: str, source: str):
    lines = source.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if "console.log(" in stripped and not stripped.startswith("//"):
            add_issue(filepath, i, "CONSOLE_LOG", "INFO",
                      "console.log() found",
                      "Remove simple console.log statements or replace with structured logging (e.g., pino).")

        if "@ts-ignore" in stripped or "@ts-nocheck" in stripped:
            add_issue(filepath, i, "TS_SUPPRESS", "WARNING",
                      "TypeScript error suppression",
                      "Define a proper interface for the object instead of skipping type checking.")

        if re.search(r':\s*any\b', stripped):
            add_issue(filepath, i, "ANY_TYPE", "INFO",
                      "Usage of 'any' type",
                      "Replace 'any' with 'unknown' (and narrow) or a detailed Interface type.")


# ─── 6. Cross-Module Consistency (WITH AUTO-FIX) ─────────────────────────────

def check_init_files(root_dir: Path):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = Path(dirpath).relative_to(PROJECT_ROOT)

        py_files = [f for f in filenames if f.endswith(".py") and f != "__init__.py"]
        has_init = "__init__.py" in filenames

        if py_files and not has_init and str(rel) != ".":
            init_path = Path(dirpath) / "__init__.py"
            add_issue(str(init_path), 0, "MISSING_INIT", "WARNING",
                      f"Directory '{rel}' has Python files but no __init__.py",
                      f"Create empty file: touch {init_path.relative_to(PROJECT_ROOT)}")
            auto_fix_commands.append(f"touch '{init_path.resolve()}'")


# ─── Macro-Level Codebase Architecture Intel ─────────────────────────────────

def generate_macro_improvements():
    """Analyze all issues and suggest macro-level architectural improvements."""
    improvements = []
    
    # 1. Missing Init files
    missing_inits = len([i for i in issues if i.category == "MISSING_INIT"])
    if missing_inits > 0:
        improvements.append(f"📦 [Module Resolution] Missing {missing_inits} '__init__.py' files. This can break absolute imports across the codebase.")

    # 2. Complexity Density
    complex_files = [i.filepath for i in issues if i.category == "COMPLEXITY"]
    if len(complex_files) > 5:
        improvements.append("🧩 [Architecture] High number of 'God Objects' and oversized files detected. We need to adopt a cleaner Domain-Driven Design (DDD). We should start splitting components by Domain (e.g., `core/audio` -> split into `capture`, `pipeline`, `output`).")

    # 3. Suppressed Types & Console.Logs
    ts_debt = len([i for i in issues if i.category in ["ANY_TYPE", "TS_SUPPRESS"]])
    if ts_debt > 0:
        improvements.append(f"🟦 [Type Safety] {ts_debt} TypeScript shortcuts ('any' or '@ts-ignore') detected. We should strictly enforce tsconfig.json `'strict': true` to prevent future runtime UI bugs.")

    # 4. Long Functions
    long_funcs = len([i for i in issues if i.category == "LONG_FUNCTION"])
    if long_funcs > 10:
        improvements.append(f"📜 [Maintainability] {long_funcs} functions exceed 80 lines. Testability is severely impaired here. Recommendation: Apply the 'Extract Function' refactoring pattern heavily on the core handlers.")
    
    return improvements

# ─── Main Scanner Loop ───────────────────────────────────────────────────────

def scan_codebase():
    py_count = 0
    ts_count = 0

    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if filename.endswith(".py"):
                py_count += 1
                check_python_syntax(filepath)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                except (IOError, OSError):
                    add_issue(filepath, 0, "IO_ERROR", "ERROR", "Could not read file", "Check file permissions.")
                    continue
                check_python_imports(filepath, source)
                check_python_patterns(filepath, source)
                check_file_metrics(filepath, source)

            elif filename.endswith((".ts", ".tsx", ".js", ".jsx")):
                ts_count += 1
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                except (IOError, OSError):
                    continue
                check_typescript_file(filepath, source)

    check_init_files(PROJECT_ROOT / "core")
    check_init_files(PROJECT_ROOT / "tests")

    return py_count, ts_count


# ─── Report Generation ───────────────────────────────────────────────────────

def generate_report(py_count: int, ts_count: int, output_json: bool = False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Produce the fix script
    FIX_SCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FIX_SCRIPT_PATH, "w") as f:
        f.write("#!/bin/bash\n# AetherOS Auto-Fixes Script\n# Generated: " + timestamp + "\n\n")
        f.write("\n".join(auto_fix_commands))
    os.chmod(FIX_SCRIPT_PATH, 0o755)

    if output_json:
        report = {
            "timestamp": timestamp,
            "files_scanned": {"python": py_count, "typescript": ts_count},
            "totals": dict(stats),
            "issues": [i.to_dict() for i in issues],
            "macro_improvements": generate_macro_improvements()
        }
        output_path = PROJECT_ROOT / "docs" / "audits" / f"health_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 JSON report saved to: {output_path}")
        return

    print("\n" + "=" * 80)
    print(f"  🧬 AetherOS AI Architect: Codebase Health & Intel Engine — {timestamp}")
    print("=" * 80)
    print(f"\n  📁 Files scanned:  {py_count} Python  |  {ts_count} TypeScript/JSX")
    print(f"  ❌ Errors:    {stats.get('ERROR', 0)}")
    print(f"  ⚠️  Warnings:  {stats.get('WARNING', 0)}")
    print(f"  ℹ️  Info:      {stats.get('INFO', 0)}")
    print(f"  📊 Total:     {len(issues)}")

    # 1. Print Micro Issues
    for severity in ("ERROR", "WARNING", "INFO"):
        group = [i for i in issues if i.severity == severity]
        if not group:
            continue

        sev_label = {"ERROR": "❌ ERRORS", "WARNING": "⚠️  WARNINGS", "INFO": "ℹ️  INFORMATIONAL"}.get(severity)
        print(f"\n{'─' * 80}")
        print(f"  {sev_label} ({len(group)})")
        print(f"{'─' * 80}")

        by_category = defaultdict(list)
        for i in group:
            by_category[i.category].append(i)

        for cat, cat_issues in sorted(by_category.items()):
            print(f"\n  [{cat}] ({len(cat_issues)} issues)")
            for issue in cat_issues[:5]:  # Cap to strictly 5 so it's readable
                print(f"    {issue}")
            if len(cat_issues) > 5:
                print(f"    ... and {len(cat_issues) - 5} more. View full JSON for detail.")


    # 2. Print Macro Architectural Self-Improvement Intel
    print(f"\n{'=' * 80}")
    print("  🚀 SELF-IMPROVEMENT: MACRO ARCHITECTURE INTEL ")
    print("=" * 80)
    macro_intel = generate_macro_improvements()
    if macro_intel:
        for intel in macro_intel:
            print(f"  {intel}\n")
    else:
        print("  ✅ Base Architecture is solid. Keep up the clean code.\n")

    # 3. Print Actionable Next Steps
    print(f"{'─' * 80}")
    print(f"  🤖 AUTOMATED FIXES: Generated {len(auto_fix_commands)} safe auto-fixes.")
    print("  👉 Run fixes via: ./docs/audits/suggested_fixes.sh")
    print(f"{'─' * 80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AetherOS Health Scanner")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    py_count, ts_count = scan_codebase()
    generate_report(py_count, ts_count, output_json=args.json)
