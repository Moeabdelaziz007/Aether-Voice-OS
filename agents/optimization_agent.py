"""
🤖 OptimizationAgent
Automatically identifies and applies performance optimizations.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class OptimizationAgent:
    """Identifies and applies performance optimizations"""
    
    def __init__(self):
        self.name = "OptimizationAgent"
        self.target_dirs = ["core", "apps"]
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.optimizations_applied = []
    
    async def run(self) -> Dict[str, Any]:
        self.logger.info("⚡ Starting performance optimization...")
        results = {
            "files_analyzed": 0,
            "optimizations_found": 0,
            "optimizations_applied": 0,
            "performance_improvements": [],
            "errors": []
        }
        
        try:
            # Analyze Python files for optimization opportunities
            python_files = self._get_python_files()
            results["files_analyzed"] = len(python_files)
            
            for file_path in python_files:
                optimizations = await self._analyze_file_for_optimizations(file_path)
                if optimizations:
                    results["optimizations_found"] += len(optimizations)
                    applied = await self._apply_optimizations(file_path, optimizations)
                    results["optimizations_applied"] += applied
                    results["performance_improvements"].extend(optimizations)
            
            self.logger.info(
                f"✅ Optimization completed: "
                f"{results['optimizations_applied']}/{results['optimizations_found']} applied"
            )
            results["status"] = "success"
            
        except Exception as e:
            self.logger.error(f"💥 OptimizationAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"
            
        return results
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files to analyze"""
        files = []
        for dir_path in self.target_dirs:
            path = Path(dir_path)
            if path.exists():
                files.extend(path.rglob("*.py"))
        return files
    
    async def _analyze_file_for_optimizations(self, file_path: Path) -> List[Dict]:
        """Analyze a file for performance optimization opportunities"""
        optimizations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Visitor to find optimization opportunities
            visitor = OptimizationVisitor()
            visitor.visit(tree)
            
            # Convert findings to optimization suggestions
            for loop_node in visitor.loops_with_range:
                optimizations.append({
                    "type": "loop_optimization",
                    "file": str(file_path),
                    "line": loop_node.lineno,
                    "description": "Range-based loop could use enumerate or direct iteration",
                    "suggestion": "Use enumerate() for index+value access or direct iteration"
                })
            
            for comprehension_node in visitor.list_comprehensions:
                if len(comprehension_node.generators) > 1:
                    optimizations.append({
                        "type": "comprehension_optimization",
                        "file": str(file_path),
                        "line": comprehension_node.lineno,
                        "description": "Nested list comprehension - consider generator or loop",
                        "suggestion": "Use generator expression or break into multiple steps"
                    })
            
            for func_node in visitor.functions_with_globals:
                optimizations.append({
                    "type": "global_access_optimization",
                    "file": str(file_path),
                    "line": func_node.lineno,
                    "description": "Function accesses global variables",
                    "suggestion": "Pass globals as parameters or use dependency injection"
                })
            
            # Check for inefficient string operations
            if " + " in content and ".join(" not in content:
                optimizations.append({
                    "type": "string_concatenation",
                    "file": str(file_path),
                    "line": None,
                    "description": "String concatenation detected",
                    "suggestion": "Use ''.join() for multiple string concatenations"
                })
            
            # Check for inefficient list operations
            if ".append(" in content and "extend(" not in content:
                optimizations.append({
                    "type": "list_operations",
                    "file": str(file_path),
                    "line": None,
                    "description": "Multiple .append() calls detected",
                    "suggestion": "Consider using .extend() or list comprehension"
                })
                
        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {str(e)}")
            
        return optimizations
    
    async def _apply_optimizations(self, file_path: Path, optimizations: List[Dict]) -> int:
        """Apply applicable optimizations to a file"""
        applied_count = 0
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply string concatenation optimization
            for opt in optimizations:
                if opt["type"] == "string_concatenation":
                    content = await self._optimize_string_concatenation(content)
                    applied_count += 1
                    
                elif opt["type"] == "list_operations":
                    content = await self._optimize_list_operations(content)
                    applied_count += 1
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.logger.debug(f"Applied {applied_count} optimizations to {file_path}")
                
        except Exception as e:
            self.logger.warning(f"Failed to apply optimizations to {file_path}: {str(e)}")
            
        return applied_count
    
    async def _optimize_string_concatenation(self, content: str) -> str:
        """Optimize string concatenation operations"""
        try:
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                # Simple pattern: multiple + operations on strings
                if '"' in line and '+' in line and '.join' not in line:
                    # Convert a + b + c to ''.join([a, b, c])
                    if line.count('+') >= 2 and line.count('"') >= 2:
                        # Simple replacement for common cases
                        if 'result =' in line and '+' in line:
                            # Example: result = "a" + "b" + "c"
                            parts = line.split(' = ')
                            if len(parts) == 2:
                                var_name = parts[0].strip()
                                expression = parts[1].strip()
                                if '+' in expression:
                                    # Simple join optimization
                                    new_line = f'{var_name} = "".join([{expression.replace("+", ", ")}])'
                                    new_lines.append(new_line)
                                    continue
                new_lines.append(line)
                
            return '\n'.join(new_lines)
            
        except Exception as e:
            self.logger.warning(f"String optimization failed: {str(e)}")
            return content
    
    async def _optimize_list_operations(self, content: str) -> str:
        """Optimize list operation patterns"""
        try:
            lines = content.split('\n')
            new_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # Look for patterns like:
                # items = []
                # items.append(a)
                # items.append(b)
                if 'items = []' in line and i + 2 < len(lines):
                    next_line = lines[i + 1]
                    next_next_line = lines[i + 2]
                    
                    if ('items.append(' in next_line and 
                        'items.append(' in next_next_line):
                        # Convert to list comprehension or direct assignment
                        var_lines = [next_line, next_next_line]
                        items = []
                        for var_line in var_lines:
                            if 'items.append(' in var_line:
                                item = var_line.split('items.append(')[1].rstrip(')')
                                items.append(item.strip())
                        
                        if len(items) >= 2:
                            new_lines.append(f'items = [{", ".join(items)}]')
                            i += 2  # Skip the next two lines
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
                
                i += 1
                
            return '\n'.join(new_lines)
            
        except Exception as e:
            self.logger.warning(f"List optimization failed: {str(e)}")
            return content


class OptimizationVisitor(ast.NodeVisitor):
    """AST visitor to find optimization opportunities"""
    
    def __init__(self):
        self.loops_with_range = []
        self.list_comprehensions = []
        self.functions_with_globals = []
        self.global_vars = set()
    
    def visit_For(self, node):
        """Visit for loops"""
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == 'range':
                    self.loops_with_range.append(node)
        self.generic_visit(node)
    
    def visit_ListComp(self, node):
        """Visit list comprehensions"""
        self.list_comprehensions.append(node)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        # Check if function accesses global variables
        for stmt in node.body:
            if isinstance(stmt, ast.Global):
                self.global_vars.update(stmt.names)
                self.functions_with_globals.append(node)
                break
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Visit name references"""
        if isinstance(node.ctx, ast.Load):
            if node.id in self.global_vars:
                # Find parent function
                parent_func = self._find_parent_function(node)
                if parent_func and parent_func not in self.functions_with_globals:
                    self.functions_with_globals.append(parent_func)
        self.generic_visit(node)
    
    def _find_parent_function(self, node):
        """Find parent function node"""
        # This is a simplified version - in practice, you'd need
        # to track the visitor state more carefully
        return None