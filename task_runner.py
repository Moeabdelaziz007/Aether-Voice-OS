#!/usr/bin/env python3
"""
🤖 Aether Voice OS - AI Agent Task Runner
Orchestrates automated code improvement agents for solo developer workflow.

Agents:
- FormatterAgent: Code formatting & linting
- RefactorAgent: Logging & config refactoring
- TestAgent: Unit & integration tests
- DIInjectorAgent: Dependency injection
- SecurityAgent: Security scanning & fixes
- LearningAgent: Continuous improvement
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Import custom agents
from agents.di_injector import DIInjectorAgent
from agents.security_agent import SecurityAgent
from agents.learning_agent import LearningAgent
from agents.optimization_agent import OptimizationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("aether_agents.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class AgentBase:
    """Base class for all AI agents"""

    def __init__(self, name: str, target_dirs: List[str]):
        self.name = name
        self.target_dirs = target_dirs
        self.logger = logging.getLogger(f"agent.{name}")

    async def run(self) -> Dict[str, Any]:
        """Execute agent task"""
        raise NotImplementedError

    def get_target_files(self, extensions: List[str]) -> List[Path]:
        """Get all target files with specified extensions"""
        files = []
        for dir_path in self.target_dirs:
            path = Path(dir_path)
            if path.exists():
                for ext in extensions:
                    files.extend(path.rglob(f"*.{ext}"))
        return files


class FormatterAgent(AgentBase):
    """Formats code and fixes linting issues"""

    def __init__(self):
        super().__init__("FormatterAgent", ["core", "apps", "cortex", "tests"])

    async def run(self) -> Dict[str, Any]:
        self.logger.info("🚀 Starting code formatting...")
        results = {"formatted_files": [], "lint_errors_fixed": 0, "errors": []}

        try:
            # Run ruff format
            format_cmd = ["ruff", "format"] + self.target_dirs
            proc = await asyncio.create_subprocess_exec(
                *format_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                self.logger.info("✅ Code formatting completed")
                results["status"] = "success"
            else:
                self.logger.error(f"❌ Formatting failed: {stderr.decode()}")
                results["errors"].append(stderr.decode())
                results["status"] = "failed"

            # Run ruff check with auto-fix
            check_cmd = ["ruff", "check", "--fix"] + self.target_dirs
            proc = await asyncio.create_subprocess_exec(
                *check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                self.logger.info("✅ Linting completed")
                count = len(stdout.decode().split("\n")) if stdout else 0
                results["lint_errors_fixed"] = count
            else:
                msg = stderr.decode()
                self.logger.warning(f"⚠️ Some linting issues remain: {msg}")

        except Exception as e:
            self.logger.error(f"💥 FormatterAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"

        return results


class RefactorAgent(AgentBase):
    """Refactors print statements to structured logging and improves config"""

    def __init__(self):
        super().__init__("RefactorAgent", ["core"])

    async def run(self) -> Dict[str, Any]:
        self.logger.info("🔧 Starting refactoring...")
        results = {"files_modified": [], "print_statements_converted": 0, "errors": []}

        try:
            python_files = self.get_target_files(["py"])

            for file_path in python_files:
                if await self._convert_print_to_logging(file_path):
                    results["files_modified"].append(str(file_path))

            count = len(results["files_modified"])
            self.logger.info(f"✅ Refactored {count} files")
            results["status"] = "success"

        except Exception as e:
            self.logger.error(f"💥 RefactorAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"

        return results

    async def _convert_print_to_logging(self, file_path: Path) -> bool:
        """Convert print statements to structured logging"""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Simple pattern matching for print statements
            import re

            # Match print statements (basic pattern)
            print_pattern = r'print\s*\(\s*["\']([^"\']*)["\']\s*\)'
            replacement = r'logger.info("\1")'

            content = re.sub(print_pattern, replacement, content)

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                self.logger.debug(f"Converted print statements in {file_path}")
                return True

        except Exception as e:
            self.logger.warning(f"Failed to refactor {file_path}: {str(e)}")

        return False


class TestAgent(AgentBase):
    """Runs tests and generates new test cases"""

    def __init__(self):
        super().__init__("TestAgent", ["tests", "core"])

    async def run(self) -> Dict[str, Any]:
        self.logger.info("🧪 Running tests...")
        results = {"tests_passed": 0, "tests_failed": 0, "coverage": 0, "errors": []}

        try:
            # Run pytest
            cmd = ["pytest", "tests/", "-v", "--tb=short"]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            output = stdout.decode()

            # Parse results
            if "passed" in output:
                lines = [line for line in output.split("\n") if "PASSED" in line]
                results["tests_passed"] = len(lines)

            if "failed" in output:
                lines = [line for line in output.split("\n") if "FAILED" in line]
                results["tests_failed"] = len(lines)

            passed = results["tests_passed"]
            failed = results["tests_failed"]
            self.logger.info(f"✅ Tests completed: {passed} passed, {failed} failed")
            is_success = results["tests_failed"] == 0
            results["status"] = "success" if is_success else "partial"

        except Exception as e:
            self.logger.error(f"💥 TestAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"

        return results


class TaskRunner:
    """Main orchestrator for AI agents"""

    def __init__(self):
        self.agents = [
            FormatterAgent(),
            RefactorAgent(),
            TestAgent(),
            DIInjectorAgent(),
            SecurityAgent(),
            LearningAgent(),
            OptimizationAgent(),
        ]
        self.results = {}
        self.logger = logging.getLogger("runner")

    async def run_all_agents(self) -> Dict[str, Any]:
        """Run all agents in sequence"""
        self.results = {}

        for agent in self.agents:
            msg = f"▶️  Running {agent.name}"
            self.logger.info(msg)

            try:
                result = await agent.run()
                self.results[agent.name] = result

                if result.get("status") == "failed":
                    msg = f"❌ {agent.name} failed, stopping execution"
                    self.logger.error(msg)
                    break

            except Exception as e:
                msg = f"💥 {agent.name} crashed: {str(e)}"
                self.logger.error(msg)
                self.results[agent.name] = {"status": "crashed", "error": str(e)}

        return self.results

    def generate_report(self) -> str:
        """Generate execution report"""
        report = ["#" * 50, "🤖 AETHER AGENT EXECUTION REPORT", "#" * 50, ""]

        for agent_name, result in self.results.items():
            status = result.get("status", "unknown")
            emoji_map = {
                "success": "✅",
                "failed": "❌",
                "partial": "⚠️",
                "crashed": "💥",
            }
            emoji = emoji_map.get(status, "❓")

            report.append(f"{emoji} {agent_name}: {status.upper()}")

            if "files_modified" in result:
                count = len(result["files_modified"])
                report.append(f"   📄 Files modified: {count}")
            if "tests_passed" in result:
                report.append(f"   ✅ Tests passed: {result['tests_passed']}")
                report.append(f"   ❌ Tests failed: {result['tests_failed']}")
            if result.get("errors"):
                report.append(f"   💥 Errors: {len(result['errors'])}")

            report.append("")

        return "\n".join(report)


async def main():
    """Main entry point"""
    logger.info("🚀 Starting Aether AI Agent Task Runner")

    runner = TaskRunner()
    results = await runner.run_all_agents()

    # Generate and save report
    report = runner.generate_report()
    print(report)

    # Save detailed results
    with open("agent_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("🏁 Task runner completed")


if __name__ == "__main__":
    asyncio.run(main())
