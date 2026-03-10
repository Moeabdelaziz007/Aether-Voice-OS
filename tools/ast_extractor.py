import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FunctionInfo:
    """Metadata for a Python function."""

    name: str
    lineno: int
    end_lineno: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    is_async: bool
    is_method: bool = False


@dataclass
class ClassInfo:
    """Metadata for a Python class."""

    name: str
    lineno: int
    end_lineno: int
    docstring: Optional[str]
    decorators: List[str]
    bases: List[str]
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    """Complete metadata for a Python module."""

    file_path: str
    docstring: Optional[str]
    imports: List[str]
    from_imports: Dict[str, List[str]]
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    global_variables: List[str]
    type_hints: Dict[str, str]


class PythonASTExtractor:
    """Extract comprehensive metadata from Python files using AST."""

    def extract(self, file_path: Path) -> ModuleInfo:
        """Parse a Python file and extract all metadata."""

        source = file_path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Handle files with syntax errors gracefully
            return ModuleInfo(
                file_path=str(file_path),
                docstring=None,
                imports=[],
                from_imports={},
                classes=[],
                functions=[],
                global_variables=[],
                type_hints={},
            )

        # Extract module-level docstring
        module_docstring = ast.get_docstring(tree)

        # Extract all components
        imports = []
        from_imports = {}
        classes = []
        functions = []
        global_vars = []
        type_hints = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                from_imports[module] = names

            elif isinstance(node, ast.ClassDef):
                classes.append(self._extract_class(node))

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Only top-level functions (not methods)
                parent = self._find_parent(tree, node)
                if parent is None or isinstance(parent, ast.Module):
                    functions.append(self._extract_function(node))

            elif isinstance(node, ast.AnnAssign):
                # Type-hinted global variable
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    type_hints[var_name] = self._get_annotation(node.annotation) or ""
                    global_vars.append(var_name)

        return ModuleInfo(
            file_path=str(file_path),
            docstring=module_docstring,
            imports=imports,
            from_imports=from_imports,
            classes=classes,
            functions=functions,
            global_variables=global_vars,
            type_hints=type_hints,
        )

    def _extract_class(self, node: ast.ClassDef) -> ClassInfo:
        """Extract metadata from a class definition."""

        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_string(d) for d in node.decorator_list]
        bases = [self._get_name(base) for base in node.bases]

        methods = []
        attributes = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function(item, is_method=True)
                methods.append(method_info)

            elif isinstance(item, ast.AnnAssign):
                # Class attribute with type hint
                if isinstance(item.target, ast.Name):
                    attributes.append(item.target.id)

            elif isinstance(item, ast.Assign):
                # Class attribute without type hint
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)

        return ClassInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            docstring=docstring,
            decorators=decorators,
            bases=bases,
            methods=methods,
            attributes=attributes,
        )

    def _extract_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool = False) -> FunctionInfo:
        """Extract metadata from a function definition."""

        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_string(d) for d in node.decorator_list]

        # Extract arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        # Extract return type
        returns = self._get_annotation(node.returns) if node.returns else None

        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            args=args,
            returns=returns,
            docstring=docstring,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=is_method,
        )

    def _get_annotation(self, node) -> Optional[str]:
        """Convert annotation node to string."""
        if node is None:
            return None

        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif hasattr(ast, "unparse"):
            try:
                return ast.unparse(node)
            except Exception:
                return str(type(node))
        return str(type(node))

    def _get_decorator_string(self, node) -> str:
        """Convert decorator node to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif hasattr(ast, "unparse"):
            try:
                return ast.unparse(node)
            except Exception:
                return str(type(node))
        return str(type(node))

    def _get_name(self, node) -> str:
        """Get name from a node (for bases)."""
        if isinstance(node, ast.Name):
            return node.id
        elif hasattr(ast, "unparse"):
            try:
                return ast.unparse(node)
            except Exception:
                return str(type(node))
        return str(type(node))

    def _find_parent(self, tree, target_node):
        """Find the parent node of a target node."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child is target_node:
                    return node
        return None
