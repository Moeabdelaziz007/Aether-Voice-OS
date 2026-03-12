import asyncio
import logging
import sys
import time

# Add core to path
sys.path.append(".")

import os

from dotenv import find_dotenv, load_dotenv

print(f"DEBUG: CWD: {os.getcwd()}")
dotenv_path = find_dotenv()
print(f"DEBUG: find_dotenv() found: {dotenv_path}")
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"DEBUG: GOOGLE_API_KEY in os.environ: {'SET' if 'GOOGLE_API_KEY' in os.environ else 'MISSING'}")
else:
    print("DEBUG: NO .env file found!")

from core.engine import AetherEngine


# Custom formatter for the preflight dashboard
class PreflightFormatter(logging.Formatter):
    def format(self, record):
        if "PREFLIGHT" in record.name:
            return f"\n[ {record.levelname} ] {record.msg}"
        return super().format(record)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PREFLIGHT.Checker")

class PreflightMonitor:
    def __init__(self, engine: AetherEngine):
        self.engine = engine
        self.bus = engine._event_bus
        self.results = {
            "test_1_voice": False,
            "test_1_latency": 0.0,
            "test_2_bargein": False,
            "test_3_tool": False
        }
        self.request_time = 0

    async def start_monitoring(self):
        # Hook into EventBus
        self.bus.subscribe("ai_request_started", self._on_ai_start)
        self.bus.subscribe("audio_out_started", self._on_audio_out)
        self.bus.subscribe("barge_in_detected", self._on_barge_in)
        self.bus.subscribe("tool_call_executed", self._on_tool_call)
        
        logger.info("📡 Preflight Monitor: Active. Please start the manual tests.")

    def _on_ai_start(self, data):
        self.request_time = time.time()
        logger.info("Test 1 Started: Voice Input detected. Waiting for response...")

    def _on_audio_out(self, data):
        if self.request_time > 0:
            latency = (time.time() - self.request_time) * 1000
            self.results["test_1_latency"] = latency
            self.results["test_1_voice"] = True
            status = "✅ SUCCESS" if latency < 2000 else "⚠️ SLOW"
            logger.info(f"Test 1 Results: Gemini Responded | Latency: {latency:.2f}ms | {status}")
            self.request_time = 0

    def _on_barge_in(self, data):
        self.results["test_2_bargein"] = True
        logger.info("Test 2 Results: ✅ Interruption (Barge-in) detected and handled.")

    def _on_tool_call(self, data):
        self.results["test_3_tool"] = True
        logger.info(f"Test 3 Results: ✅ Tool Executed: {data.get('name')} | Output Received.")

    async def report_loop(self):
        while True:
            await asyncio.sleep(5)
            self._print_dashboard()

    def _print_dashboard(self):
        print("\n" + "="*50)
        print("🚀 GEMIGRAM PRE-RECORDING CHECKLIST")
        print("="*50)
        t1 = "PASS" if self.results["test_1_voice"] else "WAIT"
        lat = f"({self.results['test_1_latency']:.0f}ms)" if self.results['test_1_latency'] > 0 else ""
        print(f"[ {t1} ] Test 1: Voice & Latency < 2s {lat}")
        
        t2 = "PASS" if self.results["test_2_bargein"] else "WAIT"
        print(f"[ {t2} ] Test 2: Interruption / Barge-in")
        
        t3 = "PASS" if self.results["test_3_tool"] else "WAIT"
        print(f"[ {t3} ] Test 3: Tool Invocation & Output")
        print("="*50 + "\n")

async def main():
    engine = AetherEngine()
    monitor = PreflightMonitor(engine)
    
    # Start engine and monitor in parallel
    await monitor.start_monitoring()
    
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(engine.run())
            tg.create_task(monitor.report_loop())
    except KeyboardInterrupt:
        print("Tests stopped by user.")

if __name__ == "__main__":
    asyncio.run(main())
