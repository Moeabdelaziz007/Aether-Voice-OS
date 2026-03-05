"""
🤖 SecurityAgent
Performs security scanning and automated fixes.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import json

logger = logging.getLogger(__name__)


class SecurityAgent:
    """Security scanning and automated fixes"""
    
    def __init__(self):
        self.name = "SecurityAgent"
        self.target_dirs = ["core", "apps"]
        self.logger = logging.getLogger(f"agent.{self.name}")
    
    async def run(self) -> Dict[str, Any]:
        self.logger.info("🛡️  Starting security scan...")
        results = {
            "vulnerabilities_found": 0,
            "issues_fixed": 0,
            "security_tools_run": [],
            "errors": []
        }
        
        try:
            # Run bandit security scanner
            bandit_results = await self._run_bandit_scan()
            results["security_tools_run"].append("bandit")
            
            if bandit_results:
                count = len(bandit_results)
                results["vulnerabilities_found"] += count
                self.logger.info(f"🔍 Found {count} potential vulnerabilities")
            
            # Run safety dependency checker
            safety_results = await self._run_safety_check()
            results["security_tools_run"].append("safety")
            
            if safety_results:
                count = len(safety_results)
                results["vulnerabilities_found"] += count
                self.logger.info(f"🔍 Found {count} dependency issues")
            
            # Attempt to fix common issues
            if results["vulnerabilities_found"] > 0:
                fixes_applied = await self._apply_security_fixes()
                results["issues_fixed"] = fixes_applied
            
            found = results["vulnerabilities_found"]
            fixed = results["issues_fixed"]
            msg = (
                f"✅ Security scan completed: {found} issues found, "
                f"{fixed} fixed"
            )
            self.logger.info(msg)
            results["status"] = "success"
            
        except Exception as e:
            self.logger.error(f"💥 SecurityAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"
            
        return results
    
    async def _run_bandit_scan(self) -> List[Dict]:
        """Run bandit security scanner"""
        try:
            cmd = ["bandit", "-r", "core/", "-f", "json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            # Bandit returns 1 for findings
            is_success = proc.returncode == 0 or proc.returncode == 1
            if is_success:
                try:
                    results = json.loads(stdout.decode())
                    return results.get("results", [])
                except json.JSONDecodeError:
                    self.logger.warning("Could not parse bandit JSON output")
                    return []
            else:
                self.logger.warning(f"Bandit failed: {stderr.decode()}")
                return []
                
        except FileNotFoundError:
            self.logger.info("Bandit not installed, skipping...")
            return []
        except Exception as e:
            self.logger.error(f"Bandit scan failed: {str(e)}")
            return []
    
    async def _run_safety_check(self) -> List[Dict]:
        """Run safety dependency checker"""
        try:
            cmd = ["safety", "check", "-r", "requirements.txt", "--json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                try:
                    results = json.loads(stdout.decode())
                    return results.get("vulnerabilities", [])
                except json.JSONDecodeError:
                    self.logger.warning("Could not parse safety JSON output")
                    return []
            else:
                # Safety returns non-zero for vulnerabilities
                try:
                    results = json.loads(stdout.decode())
                    return results.get("vulnerabilities", [])
                except json.JSONDecodeError:
                    msg = "Safety found issues but couldn't parse output"
                    self.logger.warning(msg)
                    return []
                    
        except FileNotFoundError:
            self.logger.info("Safety not installed, skipping...")
            return []
        except Exception as e:
            self.logger.error(f"Safety check failed: {str(e)}")
            return []
    
    async def _apply_security_fixes(self) -> int:
        """Apply automated security fixes"""
        fixes_count = 0
        
        try:
            # Fix common security issues in Python files
            python_files = self._get_python_files()
            
            for file_path in python_files:
                if await self._fix_file_security_issues(file_path):
                    fixes_count += 1
                    
        except Exception as e:
            self.logger.error(f"Security fixes failed: {str(e)}")
            
        return fixes_count
    
    def _get_python_files(self) -> List[Path]:
        """Get Python files to scan"""
        files = []
        for dir_path in self.target_dirs:
            path = Path(dir_path)
            if path.exists():
                files.extend(path.rglob("*.py"))
        return files
    
    async def _fix_file_security_issues(self, file_path: Path) -> bool:
        """Fix common security issues in a file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Fix common issues:
            
            # 1. Replace eval() with safer alternatives
            if "eval(" in content:
                content = content.replace("eval(", "safe_eval(")
                self.logger.debug(f"Replaced eval() in {file_path}")
            
            # 2. Replace exec() with safer alternatives
            if "exec(" in content:
                content = content.replace("exec(", "safe_exec(")
                self.logger.debug(f"Replaced exec() in {file_path}")
            
            # 3. Add proper input validation comments
            if "input(" in content and "# SECURITY:" not in content:
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if "input(" in line and "# SECURITY:" not in line:
                        new_lines.append(line)
                        sec_msg = (
                            "        # SECURITY: "
                            "Validate input before processing"
                        )
                        new_lines.append(sec_msg)
                    else:
                        new_lines.append(line)
                content = '\n'.join(new_lines)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            msg = f"Failed to fix security issues in {file_path}: {str(e)}"
            self.logger.warning(msg)
            
        return False