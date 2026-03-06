"""
🤖 DIInjectorAgent
Automatically converts direct dependencies to dependency injection pattern.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DIInjectorAgent:
    """Converts direct instantiation to dependency injection"""

    def __init__(self):
        self.name = "DIInjectorAgent"
        self.target_dirs = ["core"]
        self.converted_classes = set()
        self.logger = logging.getLogger(f"agent.{self.name}")

    async def run(self) -> Dict[str, Any]:
        self.logger.info("💉 Starting dependency injection conversion...")
        results = {
            "files_modified": [],
            "dependencies_converted": 0,
            "service_container_added": False,
            "errors": [],
        }

        try:
            # First, create service container
            service_container_path = Path("core/infra/service_container.py")
            if not service_container_path.exists():
                await self._create_service_container(service_container_path)
                results["service_container_added"] = True

            # Convert direct instantiations
            python_files = self._get_python_files()

            for file_path in python_files:
                if await self._convert_direct_instantiation(file_path):
                    results["files_modified"].append(str(file_path))
                    results["dependencies_converted"] += 1

            self.logger.info(f"✅ Converted {len(results['files_modified'])} files")
            results["status"] = "success"

        except Exception as e:
            self.logger.error(f"💥 DIInjectorAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"

        return results

    def _get_python_files(self) -> List[Path]:
        """Get all Python files in target directories"""
        files = []
        for dir_path in self.target_dirs:
            path = Path(dir_path)
            if path.exists():
                files.extend(path.rglob("*.py"))
        return files

    async def _create_service_container(self, path: Path):
        """Create service container implementation"""
        container_code = '''"""
Service Container for Dependency Injection
"""

from typing import Dict, Type, Any, Callable
import threading


class ServiceContainer:
    """Singleton service container for dependency injection"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ServiceContainer, cls).__new__(cls)
                    cls._instance._services = {}
                    cls._instance._factories = {}
        return cls._instance
    
    def register_singleton(self, name: str, service_class: Type, *args, **kwargs):
        """Register a singleton service"""
        self._services[name] = service_class(*args, **kwargs)
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function"""
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """Get service instance"""
        if name in self._services:
            return self._services[name]
        elif name in self._factories:
            instance = self._factories[name]()
            self._services[name] = instance
            return instance
        else:
            raise KeyError(f"Service '{name}' not registered")
    
    def clear(self):
        """Clear all services"""
        self._services.clear()
        self._factories.clear()


# Global container instance
container = ServiceContainer()
'''

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(container_code, encoding="utf-8")
        self.logger.info(f"Created service container at {path}")

    async def _convert_direct_instantiation(self, file_path: Path) -> bool:
        """Convert direct class instantiation to DI"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Find class instantiations
            visitor = InstantiationVisitor()
            visitor.visit(tree)

            if not visitor.instantiations:
                return False

            # Apply conversions
            modified_content = content
            for inst in visitor.instantiations:
                # Convert to container.get() pattern
                old_pattern = f"{inst.class_name}("
                new_pattern = f"container.get('{inst.class_name.lower()}')"
                modified_content = modified_content.replace(old_pattern, new_pattern, 1)

            if modified_content != content:
                file_path.write_text(modified_content, encoding="utf-8")
                self.logger.debug(f"Converted dependencies in {file_path}")
                return True

        except Exception as e:
            self.logger.warning(f"Failed to convert {file_path}: {str(e)}")

        return False


class InstantiationNode:
    """Represents a class instantiation"""

    def __init__(self, class_name: str, line_no: int):
        self.class_name = class_name
        self.line_no = line_no


class InstantiationVisitor(ast.NodeVisitor):
    """AST visitor to find class instantiations"""

    def __init__(self):
        self.instantiations: List[InstantiationNode] = []

    def visit_Call(self, node):
        """Visit function calls"""
        if isinstance(node.func, ast.Name):
            # Direct class instantiation like ClassName()
            class_name = node.func.id
            if class_name[0].isupper():  # Likely a class name
                self.instantiations.append(InstantiationNode(class_name, node.lineno))
        self.generic_visit(node)
