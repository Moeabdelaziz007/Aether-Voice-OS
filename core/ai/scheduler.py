import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from core.ai.echo import EchoGenerator
from core.ai.memory.buffer import WorkingBuffer
from core.ai.memory.wal import WALProtocol
from core.infra.event_bus import AcousticTraitEvent, VisionPulseEvent

logger = logging.getLogger("AetherOS.Cortex")


class CognitiveScheduler:
    """
    The Pre-frontal Cortex of AetherOS.
    Manages speculative tool execution, specialist scheduling, and
    sensory grounding (Temporal Memory).
    """

    def __init__(self, event_bus: Any, router: Any):
        self._event_bus = event_bus
        self._router = router
        self._temporal_memory: List[Dict[str, Any]] = []
        self._active_speculations: Dict[str, asyncio.Task] = {}
        self._overlap_buffer: List[str] = []  # Memory for interrupted thoughts

        # Thought Echo system
        self._echo_gen = EchoGenerator
        self._tool_start_times: Dict[str, float] = {}
        self._echo_threshold = 1.2  # seconds
        self._echo_callback: Optional[callable] = None

        # Subscribe to proactive pulses
        self._event_bus.subscribe(VisionPulseEvent, self._on_vision_pulse)
        self._event_bus.subscribe(AcousticTraitEvent, self._on_acoustic_trait)

        # Proactive Neural OS protocols
        self._wal = WALProtocol(
            workspace_path="/Users/cryptojoker710/Desktop/Aether Live Agent/workspace"
        )
        self._buffer = WorkingBuffer(
            workspace_path="/Users/cryptojoker710/Desktop/Aether Live Agent/workspace"
        )
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start_heartbeat(self):
        """Starts the proactive heartbeat loop."""
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("💓 Cortex: Proactive Heartbeat started.")

    async def stop_heartbeat(self):
        """Stops the proactive heartbeat loop."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def _heartbeat_loop(self):
        """Periodic check for proactive opportunities (every 15m)."""
        while True:
            await asyncio.sleep(15 * 60)
            await self.run_heartbeat_check()

    async def run_heartbeat_check(self):
        """Core heartbeat logic: Security, Self-Healing, and Proactive Builds."""
        logger.info("💓 Cortex: Running Heartbeat check...")

        # 1. Memory Watchdog (WAL Sync)
        last_details = self._wal.get_last_critical_details()
        if last_details:
            logger.info("🧠 Memory Watchdog: Reviewing WAL for fresh context.")
            # In a real impl, we'd trigger a 'Handover' update to the model.

        # 2. Pattern Detector (Reverse Prompting)
        # Using simple frequency analysis on temporal memory
        actions = [
            m.get("action") for m in self._temporal_memory[-20:] if "action" in m
        ]
        if actions:
            # Check for repetition
            for action in set(actions):
                if actions.count(action) >= 3:
                    logger.info(
                        f"💡 Pattern Detected: Repeated action '{action}'. Preparing proactive proposal."
                    )
                    if self._echo_callback:
                        await self._echo_callback(
                            f"I've noticed you've done '{action}' several times. Should I automate this?"
                        )

        # 3. Security Scan
        # Scan for high-arousal states or suspicious command patterns
        pass

    def _on_acoustic_trait(self, event: AcousticTraitEvent):
        """Adjust cognitive load based on user emotional state."""
        if event.trait_name == "arousal" and event.trait_value > 0.8:
            # User is excited/stressed: Prioritize 'Speed/Action' specialists
            logger.info(
                "⚡ Cortex: High arousal detected. Prioritizing Reactive Specialists."
            )

    def speculate(self, prompt_fragment: str):
        """
        Speculative Execution: Trigger tools based on incomplete user input.
        'Neural Pre-warming'
        """
        # Example logic: If user says 'check the error', start file_search/log_scan early
        keywords = {
            "error": ["system_tool.read_logs", "discovery_tool.scan_project"],
            "code": ["code_indexer.search", "rag_tool.query"],
            "fix": ["healing_tool.propose_fix"],
        }

        for key, tools in keywords.items():
            if key in prompt_fragment.lower():
                for tool in tools:
                    if tool not in self._active_speculations:
                        logger.info(
                            f"🔮 Speculation: Pre-warming {tool} for keyword '{key}'"
                        )
                        # In a real impl, we'd spawn a background task.
                        # For now, we track the speculation state.
                        self._active_speculations[tool] = True  # Mark as pre-warmed

    def is_tool_pre_warmed(self, tool_name: str) -> bool:
        """Helper for benchmarking and verification."""
        return tool_name in self._active_speculations

    def handle_interrupt(self, partial_text: str):
        """
        Conversational Overlap Buffer.
        Stores what the agent was saying when it got cut off.
        """
        if partial_text:
            self._overlap_buffer.append(f"Interrupted thought: {partial_text}")
            if len(self._overlap_buffer) > 3:
                self._overlap_buffer.pop(0)
            logger.debug("🧠 Cortex: Interrupted thought buffered for future context.")

        context = ""
        if self._overlap_buffer:
            context += f"Interrupted Context: {self._overlap_buffer[-1]}\n"
        return context

    def on_tool_start(self, tool_name: str):
        """Track start time for latency-based echoes."""
        self._tool_start_times[tool_name] = time.time()
        # Optionally schedule a delayed check for echo
        asyncio.create_task(self._check_for_echo(tool_name))

    def on_tool_end(self, tool_name: str):
        """Clean up tool tracking."""
        if tool_name in self._tool_start_times:
            del self._tool_start_times[tool_name]

    async def _check_for_echo(self, tool_name: str):
        """Check if an echo is needed if tool takes too long."""
        await asyncio.sleep(self._echo_threshold)
        if tool_name in self._tool_start_times and self._echo_callback:
            # Tool is still running! Trigger echo.
            echo = self._echo_gen.generate(tool_name)
            await self._echo_callback(echo)

    def set_echo_callback(self, callback: callable):
        """Set the callback to inject echo into the live session."""
        self._echo_callback = callback
