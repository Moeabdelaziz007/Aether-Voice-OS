import ast
import glob
import sys

# Constants for analysis
MAX_FUNCTION_LENGTH = 50
MAX_COMPLEXITY = 10


class PatternAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.issues = []
        self.current_function = None

    def add_issue(self, node, message, severity="warning"):
        self.issues.append(
            {
                "file": self.filepath,
                "line": getattr(node, "lineno", 0),
                "message": message,
                "severity": severity,
            }
        )

    def visit_FunctionDef(self, node):
        # Check function length
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)
        length = end_line - start_line
        if length > MAX_FUNCTION_LENGTH:
            self.add_issue(
                node,
                f"Function '{node.name}' is too long ({length} lines). "
                "Consider refactoring.",
                "warning",
            )

        # Check cyclomatic complexity (simple heuristic: counting branches)
        complexity = 1
        for child in ast.walk(node):
            if isinstance(
                child,
                (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler),
            ):
                complexity += 1
            elif isinstance(child, ast.Return):
                # Multiple return points can increase perceived complexity
                complexity += 0.5

        if complexity > MAX_COMPLEXITY:
            self.add_issue(
                node,
                f"Function '{node.name}' has high complexity ({int(complexity)}). "
                "Consider breaking it down.",
                "warning",
            )

        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        # Check for empty except blocks
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.add_issue(
                node,
                "Empty except block (silenced error). Consider logging the exception.",
                "error",
            )
        # Check for broad except
        if node.type is None or (
            isinstance(node.type, ast.Name) and node.type.id == "Exception"
        ):
            self.add_issue(
                node,
                "Broad except clause. Catch specific exceptions instead.",
                "warning",
            )
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check for print statements in core code (suggest logging)
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            if "scripts" not in self.filepath and "tests" not in self.filepath:
                self.add_issue(
                    node,
                    "Use of print() found. "
                    "Consider using the structured logging module.",
                    "info",
                )
        self.generic_visit(node)


def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []

    analyzer = PatternAnalyzer(filepath)
    analyzer.visit(tree)
    return analyzer.issues


def main():
    print("🔍 Starting Automated Pattern Learning & Improvement Check...")
    files_to_check = glob.glob("**/*.py", recursive=True)

    # Filter out external libs, envs, or specific ignored dirs
    ignore_dirs = [".venv", "venv", "env", ".tox", "node_modules", ".git", ".idx"]
    files_to_check = [f for f in files_to_check if not any(d in f for d in ignore_dirs)]

    all_issues = []
    for filepath in files_to_check:
        issues = analyze_file(filepath)
        all_issues.extend(issues)

    if not all_issues:
        print("✅ No issues found. Code looks great!")
        sys.exit(0)

    # Generate Markdown Report
    report_lines = ["# 🤖 Automated Code Improvement Report\n"]
    report_lines.append(
        "I analyzed the codebase for structural patterns, "
        "complexity, and common anti-patterns.\n"
    )
    report_lines.append("### 📊 Summary")
    report_lines.append(f"- **Total Issues Found:** {len(all_issues)}")

    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    report_lines.append(f"- **Errors:** {len(errors)}")
    report_lines.append(f"- **Warnings:** {len(warnings)}")
    report_lines.append(f"- **Info:** {len(infos)}\n")

    report_lines.append("### 🔍 Details")

    # Group by file
    issues_by_file = {}
    for issue in all_issues:
        issues_by_file.setdefault(issue["file"], []).append(issue)

    for filepath, issues in issues_by_file.items():
        report_lines.append(f"#### 📄 `{filepath}`")
        for issue in issues:
            icon = (
                "🔴"
                if issue["severity"] == "error"
                else "🟠"
                if issue["severity"] == "warning"
                else "🔵"
            )
            report_lines.append(
                f"- {icon} **Line {issue['line']}:** {issue['message']}"
            )
        report_lines.append("")

    report_content = "\n".join(report_lines)

    # Write to file so CI can pick it up
    with open("auto_improve_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print(
        f"⚠️ Found {len(all_issues)} issues. Report generated at auto_improve_report.md"
    )

    # Exit with code 0 to not fail the pipeline immediately
    sys.exit(0)


if __name__ == "__main__":
    main()
