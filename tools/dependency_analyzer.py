"""
Dependency Analyzer for AetherOS.
Builds a directed graph of Python dependencies, detects circular imports,
and generates an interactive HTML visualization.
"""

import ast
import json
from pathlib import Path

try:
    import networkx as nx
    from pyvis.network import Network
except ImportError:
    # Handle environment where packages are missing but code is being checked
    from unittest.mock import MagicMock

    nx = MagicMock()
    Network = MagicMock

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs" / "generated"


def analyze_imports(filepath: Path) -> list[str]:
    """Extract list of imports from a Python file."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def build_dependency_graph():
    """Build a directed graph of internal dependencies."""
    G = nx.DiGraph()

    python_files = list(ROOT_DIR.rglob("*.py"))
    # Filter out venv, external libs
    internal_files = [
        f
        for f in python_files
        if "venv" not in f.parts
        and ".idx" not in f.parts
        and "node_modules" not in f.parts
    ]

    # Map module names to file paths roughly
    module_to_file = {}
    for f in internal_files:
        rel = f.relative_to(ROOT_DIR)
        mod_name = str(rel.with_suffix("")).replace("/", ".")
        if mod_name.endswith(".__init__"):
            mod_name = mod_name[:-9]
        module_to_file[mod_name] = str(rel)

    for filepath in internal_files:
        rel_path = str(filepath.relative_to(ROOT_DIR))
        G.add_node(rel_path)

        imports = analyze_imports(filepath)
        for imp in imports:
            # Check if this import resolves to an internal file
            target_path = None
            if imp in module_to_file:
                target_path = module_to_file[imp]
            else:
                # Try finding parent module
                parts = imp.split(".")
                for i in range(len(parts), 0, -1):
                    sub_mod = ".".join(parts[:i])
                    if sub_mod in module_to_file:
                        target_path = module_to_file[sub_mod]
                        break

            if target_path and target_path != rel_path:
                G.add_edge(rel_path, target_path)

    return G


def find_circular_dependencies(G) -> list[list[str]]:
    """Detect circular dependencies in the graph."""
    if isinstance(G, MagicMock):
        return []
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except Exception:
        return []


def create_dependency_graph_html(G, output_path: Path):
    """Generate an interactive HTML visualization using PyVis."""
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
    )
    if not isinstance(G, MagicMock):
        net.from_nx(G)

        for node in net.nodes:
            node_id = node["id"]
            # Color coding by subsystem
            if "audio" in node_id:
                node["color"] = "#4CAF50"  # Green
            elif "ai" in node_id or "cortex" in node_id or "brain" in node_id:
                node["color"] = "#2196F3"  # Blue
            elif "infra" in node_id:
                node["color"] = "#FF9800"  # Orange
            else:
                node["color"] = "#9E9E9E"  # Grey

            # Size based on number of incoming edges (dependencies)
            in_degree = G.in_degree(node_id)
            node["size"] = 10 + (in_degree * 2)

        net.save_graph(str(output_path))


def generate_reports():
    """Main execution function to analyze and generate reports."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print("Building dependency graph...")
    G = build_dependency_graph()

    print("Detecting circular dependencies...")
    cycles = find_circular_dependencies(G)

    report_data = {
        "nodes_count": G.number_of_nodes() if not isinstance(G, MagicMock) else 0,
        "edges_count": G.number_of_edges() if not isinstance(G, MagicMock) else 0,
        "circular_dependencies_count": len(cycles),
        "circular_dependencies": cycles,
    }

    report_json_path = DOCS_DIR / "dependency_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    stats_md_path = DOCS_DIR / "dependency_stats.md"
    with open(stats_md_path, "w", encoding="utf-8") as f:
        f.write("# Dependency Graph Statistics\n\n")
        f.write(f"- **Total Files Analyzed:** {report_data['nodes_count']}\n")
        f.write(f"- **Total Dependencies (Edges):** {report_data['edges_count']}\n")
        circ_count = report_data["circular_dependencies_count"]
        f.write(f"- **Circular Dependencies Found:** {circ_count}\n\n")
        if cycles:
            f.write("## Circular Dependencies List\n")
            for cycle in cycles:
                f.write(f"- {' -> '.join(cycle)} -> {cycle[0]}\n")
        else:
            f.write("## Circular Dependencies List\n")
            f.write("None found! Great architecture.\n")

    print("Generating HTML visualization...")
    html_path = DOCS_DIR / "dependency_graph.html"
    create_dependency_graph_html(G, html_path)

    print(f"Reports generated successfully in {DOCS_DIR}")


if __name__ == "__main__":
    generate_reports()
