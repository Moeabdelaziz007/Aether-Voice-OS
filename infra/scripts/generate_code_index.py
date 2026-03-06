#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".next",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
}

LANGUAGE_BY_EXT = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".toml": "toml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".md": "markdown",
}


@dataclass(frozen=True)
class FileRecord:
    path: str
    language: str
    lines: int
    size_bytes: int
    layer: str


def detect_layer(rel_path: Path) -> str:
    parts = rel_path.parts
    if not parts:
        return "root"
    if parts[0] == "core" and len(parts) > 1:
        return f"core/{parts[1]}"
    if parts[0] in {"apps", "tests", "docs", "infra", "cortex", "agents", "tools"}:
        return parts[0]
    return parts[0]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def collect_files(repo_root: Path) -> list[FileRecord]:
    records: list[FileRecord] = []
    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(repo_root)
        if should_skip(rel):
            continue
        language = LANGUAGE_BY_EXT.get(file_path.suffix.lower(), "other")
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        records.append(
            FileRecord(
                path=rel.as_posix(),
                language=language,
                lines=content.count("\n") + (1 if content else 0),
                size_bytes=file_path.stat().st_size,
                layer=detect_layer(rel),
            )
        )
    return sorted(records, key=lambda r: r.path)


def build_python_module_map(records: list[FileRecord]) -> dict[str, str]:
    module_map: dict[str, str] = {}
    for rec in records:
        if not rec.path.endswith(".py"):
            continue
        rel = Path(rec.path)
        if rel.name == "__init__.py":
            module = ".".join(rel.with_suffix("").parts[:-1])
        else:
            module = ".".join(rel.with_suffix("").parts)
        if module:
            module_map[module] = rec.path
    return module_map


def resolve_python_module(module: str, module_map: dict[str, str]) -> str | None:
    if module in module_map:
        return module_map[module]
    parts = module.split(".")
    while len(parts) > 1:
        parts.pop()
        candidate = ".".join(parts)
        if candidate in module_map:
            return module_map[candidate]
    return None


def resolve_relative_import(
    source: Path, target: str, all_files: set[str]
) -> str | None:
    base = source.parent
    raw = (base / target).as_posix()
    candidates = [
        raw,
        f"{raw}.ts",
        f"{raw}.tsx",
        f"{raw}.js",
        f"{raw}.jsx",
        f"{raw}/index.ts",
        f"{raw}/index.tsx",
        f"{raw}/index.js",
        f"{raw}/index.jsx",
    ]
    for candidate in candidates:
        normalized = Path(candidate).as_posix()
        if normalized in all_files:
            return normalized
    return None


def build_dependency_graph(
    repo_root: Path, records: list[FileRecord]
) -> tuple[list[dict], dict]:
    all_files = {rec.path for rec in records}
    module_map = build_python_module_map(records)
    edges: list[dict] = []
    out_degree = Counter()
    in_degree = Counter()

    import_pattern = re.compile(
        r"""import\s+(?:[\w*\s{},]+\s+from\s+)?["']([^"']+)["']"""
    )
    require_pattern = re.compile(r"""require\(\s*["']([^"']+)["']\s*\)""")

    for rec in records:
        path = repo_root / rec.path
        if rec.language == "python":
            try:
                source = path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source, filename=rec.path)
            except Exception:
                continue
            for node in ast.walk(tree):
                module_name = None
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        target = resolve_python_module(module_name, module_map)
                        if target:
                            edges.append(
                                {
                                    "source": rec.path,
                                    "target": target,
                                    "type": "python",
                                    "symbol": module_name,
                                }
                            )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    module_name = node.module
                    target = resolve_python_module(module_name, module_map)
                    if target:
                        edges.append(
                            {
                                "source": rec.path,
                                "target": target,
                                "type": "python",
                                "symbol": module_name,
                            }
                        )

        if rec.language in {"typescript", "javascript"}:
            try:
                source = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            matches = list(import_pattern.findall(source)) + list(
                require_pattern.findall(source)
            )
            for imp in matches:
                if not imp.startswith("."):
                    continue
                target = resolve_relative_import(Path(rec.path), imp, all_files)
                if target:
                    edges.append(
                        {
                            "source": rec.path,
                            "target": target,
                            "type": "js_ts",
                            "symbol": imp,
                        }
                    )

    unique_edges = []
    seen = set()
    for edge in edges:
        key = (edge["source"], edge["target"], edge["symbol"])
        if key in seen:
            continue
        seen.add(key)
        unique_edges.append(edge)
        out_degree[edge["source"]] += 1
        in_degree[edge["target"]] += 1

    stats = {
        "edge_count": len(unique_edges),
        "nodes_with_outgoing": len(out_degree),
        "nodes_with_incoming": len(in_degree),
        "top_outgoing": out_degree.most_common(20),
        "top_incoming": in_degree.most_common(20),
    }
    return unique_edges, stats


def write_outputs(
    output_dir: Path,
    records: list[FileRecord],
    edges: list[dict],
    edge_stats: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    by_language = Counter(rec.language for rec in records)
    by_layer = Counter(rec.layer for rec in records)
    generated_at = datetime.now(timezone.utc).isoformat()

    inventory = {
        "generated_at": generated_at,
        "total_files": len(records),
        "by_language": dict(by_language),
        "by_layer": dict(by_layer),
        "files": [rec.__dict__ for rec in records],
    }
    graph = {
        "generated_at": generated_at,
        "node_count": len(records),
        "nodes": [rec.path for rec in records],
        "edges": edges,
        "stats": edge_stats,
    }

    (output_dir / "code_inventory.json").write_text(
        json.dumps(inventory, indent=2), encoding="utf-8"
    )
    (output_dir / "dependency_graph.json").write_text(
        json.dumps(graph, indent=2), encoding="utf-8"
    )

    summary_lines = [
        "# Code Index Summary",
        "",
        f"- Generated at: {generated_at}",
        f"- Total files: {len(records)}",
        f"- Dependency edges: {len(edges)}",
        "",
        "## Languages",
    ]
    for lang, count in by_language.most_common():
        summary_lines.append(f"- {lang}: {count}")
    summary_lines.extend(["", "## Layers"])
    for layer, count in by_layer.most_common():
        summary_lines.append(f"- {layer}: {count}")
    summary_lines.extend(["", "## Top Outgoing Dependencies"])
    for node, count in edge_stats["top_outgoing"]:
        summary_lines.append(f"- {node}: {count}")
    summary_lines.extend(["", "## Top Incoming Dependencies"])
    for node, count in edge_stats["top_incoming"]:
        summary_lines.append(f"- {node}: {count}")

    (output_dir / "index_summary.md").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
    )
    parser.add_argument("--output-dir", default="artifacts/code-index")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir

    records = collect_files(repo_root)
    edges, edge_stats = build_dependency_graph(repo_root, records)
    write_outputs(output_dir, records, edges, edge_stats)
    print(f"Wrote code index artifacts to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
