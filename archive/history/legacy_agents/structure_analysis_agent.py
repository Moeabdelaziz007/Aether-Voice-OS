"""
🏗️ StructureAnalysisAgent
Analyzes project structure, identifies architectural issues, code smells,
and proposes structural improvements for Aether Voice OS.
"""

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class CodeSmell:
    """Represents a detected code smell or architectural issue."""

    file_path: str
    line_number: Optional[int]
    smell_type: str
    severity: str  # "critical", "warning", "info"
    description: str
    suggestion: str


@dataclass
class ModuleInfo:
    """Information about a Python module."""

    path: str
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    lines_of_code: int = 0
    complexity_score: float = 0.0
    dependencies: Set[str] = field(default_factory=set)


@dataclass
class StructureReport:
    """Complete structure analysis report."""

    total_files: int = 0
    total_lines: int = 0
    code_smells: List[CodeSmell] = field(default_factory=list)
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class StructureAnalysisAgent:
    """Analyzes project structure and identifies improvements."""

    def __init__(self):
        self.name = "StructureAnalysisAgent"
        self.target_dirs = ["core", "apps", "tests", "skills"]
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.report = StructureReport()

        # Thresholds for code quality
        self.max_file_lines = 500
        self.max_function_lines = 50
        self.max_class_methods = 15
        self.max_function_params = 5
        self.max_cyclomatic_complexity = 10
        self.max_import_depth = 5

    async def run(self) -> Dict[str, Any]:
        """Execute structure analysis."""
        self.logger.info("🏗️ Starting structure analysis...")
        results = {
            "files_analyzed": 0,
            "code_smells_found": 0,
            "critical_issues": 0,
            "suggestions": [],
            "errors": []
        }

        try:
            # Analyze all Python files
            python_files = self._get_python_files()
            results["files_analyzed"] = len(python_files)

            for file_path in python_files:
                await self._analyze_file(file_path)

            # Detect circular dependencies
            self._detect_circular_dependencies()

            # Analyze module coupling
            self._analyze_module_coupling()

            # Generate architectural suggestions
            self._generate_suggestions()

            # Compile results
            results["code_smells_found"] = len(self.report.code_smells)
            results["critical_issues"] = sum(
                1 for smell in self.report.code_smells
                if smell.severity == "critical"
            )
            results["suggestions"] = self.report.suggestions[:10]
            results["metrics"] = self.report.metrics
            results["circular_dependencies"] = len(
                self.report.circular_dependencies
            )
            results["status"] = "success"

            self.logger.info(
                f"✅ Structure analysis completed: "
                f"{results['code_smells_found']} smells, "
                f"{results['critical_issues']} critical"
            )

        except Exception as e:
            self.logger.error(f"💥 StructureAnalysisAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"

        return results

    def _get_python_files(self) -> List[Path]:
        """Get all Python files to analyze."""
        files = []
        for dir_name in self.target_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                files.extend(dir_path.rglob("*.py"))
        return files

    async def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for structure issues."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Parse AST
            tree = ast.parse(content)

            # Create module info
            module_info = ModuleInfo(
                path=str(file_path),
                lines_of_code=len(lines)
            )

            # Analyze imports
            module_info.imports = self._extract_imports(tree)
            module_info.dependencies = set(
                imp.split('.')[0] for imp in module_info.imports
            )

            # Analyze classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    module_info.classes.append(node.name)
                    self._analyze_class(node, file_path)
                elif isinstance(node, ast.FunctionDef):
                    module_info.functions.append(node.name)
                    self._analyze_function(node, file_path)

            # File-level checks
            self._check_file_size(file_path, len(lines))
            self._check_imports_organization(tree, file_path)

            # Store module info
            self.report.modules[str(file_path)] = module_info
            self.report.total_files += 1
            self.report.total_lines += len(lines)

        except SyntaxError as e:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=e.lineno,
                smell_type="syntax_error",
                severity="critical",
                description=f"Syntax error: {str(e)}",
                suggestion="Fix the syntax error before further analysis"
            ))
        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {str(e)}")

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all imports from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _analyze_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """Analyze a class for code smells."""
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

        # Check for God Class (too many methods)
        if len(methods) > self.max_class_methods:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=node.lineno,
                smell_type="god_class",
                severity="warning",
                description=(
                    f"Class '{node.name}' has {len(methods)} methods "
                    f"(max: {self.max_class_methods})"
                ),
                suggestion="Consider breaking down the class into smaller, focused classes"
            ))

        # Check for missing docstring
        if not ast.get_docstring(node):
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=node.lineno,
                smell_type="missing_docstring",
                severity="info",
                description=f"Class '{node.name}' lacks a docstring",
                suggestion="Add a docstring describing the class purpose"
            ))

        # Check inheritance depth
        if len(node.bases) > 3:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=node.lineno,
                smell_type="deep_inheritance",
                severity="warning",
                description=(
                    f"Class '{node.name}' has {len(node.bases)} base classes"
                ),
                suggestion="Favor composition over inheritance"
            ))

    def _analyze_function(self, node: ast.FunctionDef, file_path: Path) -> None:
        """Analyze a function for code smells."""
        # Check function length
        func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        if func_lines > self.max_function_lines:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=node.lineno,
                smell_type="long_function",
                severity="warning",
                description=(
                    f"Function '{node.name}' has {func_lines} lines "
                    f"(max: {self.max_function_lines})"
                ),
                suggestion="Break down into smaller, focused functions"
            ))

        # Check parameter count
        params = len(node.args.args)
        if params > self.max_function_params:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=node.lineno,
                smell_type="too_many_parameters",
                severity="warning",
                description=(
                    f"Function '{node.name}' has {params} parameters "
                    f"(max: {self.max_function_params})"
                ),
                suggestion="Consider using a data class or configuration object"
            ))

        # Check cyclomatic complexity
        complexity = self._calculate_complexity(node)
        if complexity > self.max_cyclomatic_complexity:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=node.lineno,
                smell_type="high_complexity",
                severity="warning",
                description=(
                    f"Function '{node.name}' has complexity {complexity} "
                    f"(max: {self.max_cyclomatic_complexity})"
                ),
                suggestion="Refactor to reduce branching and nesting"
            ))

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def _check_file_size(self, file_path: Path, lines: int) -> None:
        """Check if file is too large."""
        if lines > self.max_file_lines:
            self.report.code_smells.append(CodeSmell(
                file_path=str(file_path),
                line_number=None,
                smell_type="large_file",
                severity="warning",
                description=f"File has {lines} lines (max: {self.max_file_lines})",
                suggestion="Consider splitting into multiple modules"
            ))

    def _check_imports_organization(self, tree: ast.AST, file_path: Path) -> None:
        """Check import organization and detect star imports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == '*':
                        self.report.code_smells.append(CodeSmell(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            smell_type="star_import",
                            severity="warning",
                            description=f"Star import from '{node.module}'",
                            suggestion="Use explicit imports instead of star imports"
                        ))

    def _detect_circular_dependencies(self) -> None:
        """Detect circular dependencies between modules."""
        # Build dependency graph
        graph = defaultdict(set)
        for module_path, info in self.report.modules.items():
            module_name = Path(module_path).stem
            for dep in info.dependencies:
                if dep in ['core', 'apps', 'tests', 'skills']:
                    graph[module_name].add(dep)

        # Find cycles using DFS
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor) if neighbor in path else 0
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [node])

        self.report.circular_dependencies = cycles

        if cycles:
            for cycle in cycles[:5]:  # Limit to 5 reported
                self.report.code_smells.append(CodeSmell(
                    file_path="project",
                    line_number=None,
                    smell_type="circular_dependency",
                    severity="critical",
                    description=f"Circular dependency: {' -> '.join(cycle)}",
                    suggestion="Break the cycle by introducing interfaces or dependency injection"
                ))

    def _analyze_module_coupling(self) -> None:
        """Analyze coupling between modules."""
        coupling_scores = {}

        for module_path, info in self.report.modules.items():
            # Afferent coupling (incoming dependencies)
            afferent = sum(
                1 for other_info in self.report.modules.values()
                if Path(module_path).stem in other_info.dependencies
            )

            # Efferent coupling (outgoing dependencies)
            efferent = len(info.dependencies)

            # Instability metric: I = Ce / (Ca + Ce)
            total = afferent + efferent
            instability = efferent / total if total > 0 else 0

            coupling_scores[module_path] = {
                "afferent": afferent,
                "efferent": efferent,
                "instability": instability
            }

        self.report.metrics["coupling"] = coupling_scores

        # Flag highly coupled modules
        for module_path, scores in coupling_scores.items():
            if scores["efferent"] > 10:
                self.report.code_smells.append(CodeSmell(
                    file_path=module_path,
                    line_number=None,
                    smell_type="high_coupling",
                    severity="warning",
                    description=(
                        f"High efferent coupling ({scores['efferent']} "
                        f"dependencies)"
                    ),
                    suggestion="Consider reducing dependencies through abstraction"
                ))

    def _generate_suggestions(self) -> None:
        """Generate architectural improvement suggestions."""
        suggestions = []

        # Analyze code smell patterns
        smell_counts = defaultdict(int)
        for smell in self.report.code_smells:
            smell_counts[smell.smell_type] += 1

        if smell_counts["god_class"] > 3:
            suggestions.append(
                "🏗️ Multiple God Classes. Apply Single Responsibility "
                "Principle by extracting methods into focused classes."
            )

        if smell_counts["long_function"] > 5:
            suggestions.append(
                "📏 Many long functions. Refactor into smaller, composable "
                "functions with clear responsibilities."
            )

        if smell_counts["high_complexity"] > 5:
            suggestions.append(
                "🔀 High cyclomatic complexity across codebase. Consider using "
                "strategy pattern or polymorphism to reduce conditionals."
            )

        if self.report.circular_dependencies:
            suggestions.append(
                "🔄 Circular dependencies. Use dependency inversion with "
                "abstract interfaces or a service container."
            )

        # Check directory structure
        if self.report.total_files > 50 and len(self.target_dirs) < 5:
            suggestions.append(
                "📁 Large codebase in few directories. Consider organizing "
                "by feature/domain rather than by type."
            )

        # Audio-specific suggestions for Aether Voice OS
        audio_files = [
            p for p in self.report.modules.keys()
            if 'audio' in p.lower()
        ]
        if len(audio_files) > 10:
            suggestions.append(
                "🎵 Create an 'audio' package with sub-modules: "
                "input, output, processing, analysis, effects."
            )

        # Add general best practices
        suggestions.extend([
            "📝 Add type hints to public functions for IDE support and docs.",
            "🧪 Ensure each module has unit tests in tests/unit/.",
            "📊 Implement OpenTelemetry metrics for performance monitoring.",
            "🔧 Use dependency injection container for testability."
        ])

        self.report.suggestions = suggestions

        # Calculate overall metrics
        self.report.metrics["summary"] = {
            "total_files": self.report.total_files,
            "total_lines": self.report.total_lines,
            "avg_lines_per_file": (
                self.report.total_lines / max(1, self.report.total_files)
            ),
            "total_smells": len(self.report.code_smells),
            "critical_smells": sum(
                1 for s in self.report.code_smells if s.severity == "critical"
            ),
            "warning_smells": sum(
                1 for s in self.report.code_smells if s.severity == "warning"
            ),
            "info_smells": sum(
                1 for s in self.report.code_smells if s.severity == "info"
            ),
        }

    def get_report(self) -> StructureReport:
        """Get the complete analysis report."""
        return self.report

    def get_critical_issues(self) -> List[CodeSmell]:
        """Get only critical issues."""
        return [s for s in self.report.code_smells if s.severity == "critical"]

    def export_report_json(self) -> Dict[str, Any]:
        """Export report as JSON-serializable dictionary."""
        return {
            "total_files": self.report.total_files,
            "total_lines": self.report.total_lines,
            "code_smells": [
                {
                    "file": s.file_path,
                    "line": s.line_number,
                    "type": s.smell_type,
                    "severity": s.severity,
                    "description": s.description,
                    "suggestion": s.suggestion
                }
                for s in self.report.code_smells
            ],
            "circular_dependencies": self.report.circular_dependencies,
            "suggestions": self.report.suggestions,
            "metrics": self.report.metrics
        }
