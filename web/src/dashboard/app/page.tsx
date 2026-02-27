"use client";

import { useState, useEffect } from "react";
import { EmotionWaveform } from "../components/visualizers/EmotionWaveform";
import { StateVisualizer } from "../components/visualizers/StateVisualizer";
import { useAetherStore } from "../../store/useAetherStore";
import { useEngineTelemetry } from "../../hooks/useEngineTelemetry";

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);

  // Call the telemetry hook to connect to Python backend
  useEngineTelemetry();

  const engineState = useAetherStore(state => state.engineState);
  const systemLogs = useAetherStore(state => state.systemLogs);
  const latencyMs = useAetherStore(state => state.latencyMs);

  // Prevent hydration errors
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <header className="flex items-center justify-between pb-6 border-b border-white/10 mb-8">
        <div>
          <h1 className="text-3xl font-mono font-bold tracking-tighter glow-text-blue">
            AetherOS
          </h1>
          <p className="text-gray-400 font-mono text-sm mt-1 uppercase tracking-widest">
            Neural Telemetry & Proactive Engine
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#39ff14] shadow-[0_0_10px_#39ff14] animate-pulse" />
            <span className="text-sm font-mono text-[#39ff14]">SECURE LINK</span>
          </div>
          <div className="text-xs font-mono text-gray-500 bg-white/5 px-3 py-1 rounded-full border border-white/10">
            LATENCY: <span className="text-white">{latencyMs}ms</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Column: Emotion & Metrics */}
        <div className="lg:col-span-1 space-y-6 flex flex-col">
          {/* Emotion Waveform handles flex-grow to fill vertical space */}
          <EmotionWaveform className="flex-1 min-h-[300px]" />

          {/* Demo Safety Overrides Panel */}
          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-sm font-mono tracking-widest text-[#ff007f] uppercase mb-4">
              Demo Safeguards
            </h3>
            <div className="space-y-3">
              <button className="w-full text-left px-4 py-3 rounded-lg bg-black/40 border border-white/5 hover:border-[#ff3333]/50 transition-colors group flex justify-between items-center text-sm font-mono">
                <span className="text-gray-300 group-hover:text-white transition-colors">Force Intervention</span>
                <span className="text-[#ff3333] opacity-0 group-hover:opacity-100 transition-opacity uppercase text-[10px] tracking-wider">Execute</span>
              </button>
              <button className="w-full text-left px-4 py-3 rounded-lg bg-black/40 border border-white/5 hover:border-[#00f0ff]/50 transition-colors group flex justify-between items-center text-sm font-mono">
                <span className="text-gray-300 group-hover:text-white transition-colors">Toggle Auto-Detect</span>
                <span className="text-[#00f0ff]">ON</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: State Machine & Logs */}
        <div className="lg:col-span-2 space-y-6 flex flex-col">
          <StateVisualizer currentState={engineState} />

          {/* Terminal / Logs panel */}
          <div className="glass-panel rounded-2xl p-6 flex-1 flex flex-col">
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
              <h3 className="text-sm font-mono tracking-widest text-white uppercase flex items-center gap-2">
                <span className="text-[#9d4edd]">&gt;_</span> System Stream
              </h3>
              <span className="text-xs text-gray-500 font-mono text-right flex-shrink-0 ml-4">
                T-GATE V2 ACTIVE (0.85 THRESHOLD)
              </span>
            </div>
            <div className="font-mono text-xs space-y-3 overflow-y-auto h-full pr-2 text-gray-400">
              {systemLogs.length === 0 ? (
                <p className="text-gray-600 italic">Awaiting telemetry stream...</p>
              ) : (
                systemLogs.map((log, i) => (
                  <p key={i}>
                    {log}
                  </p>
                ))
              )}
              {engineState === "INTERRUPTING" && (
                <p className="text-[#ff3333] glow-text-red">
                  [WARNING] FRUSTRATION PEAK DETECTED - OVERRIDING OUTPUT
                </p>
              )}
            </div>
          </div>
        </div>

      </div>
    </main>
  );
}
