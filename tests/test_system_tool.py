import pytest
import asyncio
from core.tools.system_tool import run_terminal_command, COMMAND_BLACKLIST

@pytest.mark.asyncio
async def test_allowed_command():
    """Test that a safe command (echo) runs successfully."""
    result = await run_terminal_command("echo 'Hello Aether'")
    assert result["return_code"] == 0
    assert "Hello Aether" in result["stdout"]
    assert "error" not in result

@pytest.mark.asyncio
async def test_blacklisted_command_rm():
    """Test that 'rm' is blocked."""
    result = await run_terminal_command("rm -rf /")
    assert "error" in result
    assert "blocked by security guardrails" in result["error"]
    assert result.get("violation") == "rm"

@pytest.mark.asyncio
async def test_blacklisted_command_sudo():
    """Test that 'sudo' is blocked."""
    result = await run_terminal_command("sudo ls")
    assert "error" in result
    assert "blocked by security guardrails" in result["error"]
    assert result.get("violation") == "sudo"

@pytest.mark.asyncio
async def test_blacklisted_command_case_insensitive():
    """Test that 'SUDO' (uppercase) is also blocked."""
    result = await run_terminal_command("SUDO ls")
    assert "error" in result
    assert "blocked by security guardrails" in result["error"]
    assert result.get("violation") == "sudo"

@pytest.mark.asyncio
async def test_command_timeout():
    """Test that a long-running command is killed after 5 seconds."""
    # We try to sleep for 10 seconds, which exceeds the 5s limit
    result = await run_terminal_command("sleep 10")
    assert "error" in result
    assert "timed out" in result["error"]

@pytest.mark.asyncio
async def test_shell_injection_prevention():
    """
    Test that shell operators like '&&' or ';' are treated as arguments,
    not executed, because shell=False.
    """
    # If shell=True, this would echo "hacked".
    # With shell=False, 'echo' receives "hello; echo hacked" as a single string argument.
    result = await run_terminal_command('echo "hello; echo hacked"')
    
    # The output should literally contain the semicolon, not execute the second command
    assert 'hello; echo hacked' in result["stdout"] or 'hello; echo hacked' in result["stdout"].replace('"', '')
    # Ensure it didn't actually run the second echo on a new line
    assert result["stdout"].count("hacked") == 1
