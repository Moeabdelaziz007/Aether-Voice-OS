import logging

logger = logging.getLogger(__name__)


class DemoFallback:
    """
    Ensures the demo always succeeds by providing manual intervention triggers.
    In high-stakes presentations, acoustics might fail; this is the safety net.
    """

    def __init__(self, engine):
        self._engine = engine
        self._manual_trigger = False
        logger.info("🛡️ Demo Fallback: Safety system initialized.")

    def enable_manual_trigger(self):
        """Toggle manual mode for reliability."""
        self._manual_trigger = True
        logger.warning("🛡️ EXPLICIT OVERRIDE: Manual intervention mode ENABLED.")

    def trigger_intervention(self, reason: str = "MANUAL_BYPASS"):
        """Forces the agent to speak immediately."""
        if self._manual_trigger:
            logger.info("🛡️ [SAFETY] [MANUAL] Forcing engine intervention: %s", reason)
            # This will hook into engine.interrupt_and_speak()
            self._engine.force_intervention(reason)
        else:
            logger.debug("🛡️ Manual trigger ignored (system in Auto mode).")

    def disable_auto_detection(self):
        """Silences the auto-trigger to prevent double-speaking during manual demo."""
        logger.warning("🛡️ AUTO-DETECTION DISABLED: Relying on manual triggers.")
        self._manual_trigger = True
