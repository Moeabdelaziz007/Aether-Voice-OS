"use client";

import React, { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

const PHASE_LABEL: Record<string, string> = {
  SEARCHING: "TARGET_ACQUIRED",
  PLANNING: "STRATEGY_MAPPED",
  EXECUTING: "SYNAPSES_LINKED",
  VERIFYING: "SIGNAL_VALIDATION",
  COMPLETED: "MISSION_CONFIRMED",
  FAILED: "RECOVERY_REQUIRED",
};

const STATUS_TONE: Record<string, string> = {
  started: "text-cyan-300",
  "in-progress": "text-amber-300",
  completed: "text-emerald-300",
  failed: "text-rose-300",
};

export default function MissionControlHUD() {
  const taskPulse = useAetherStore((s) => s.taskPulse);
  const missionLog = useAetherStore((s) => s.missionLog);
  const voyagerLatencyRows = useAetherStore((s) => s.voyagerLatencyRows);
  const workspaceGalaxy = useAetherStore((s) => s.workspaceGalaxy);
  const compactMissionHud = useAetherStore((s) => s.preferences.compactMissionHud);

  const timeline = useMemo(
    () => missionLog.slice(compactMissionHud ? -4 : -7).reverse(),
    [compactMissionHud, missionLog]
  );
  const latencyRows = useMemo(
    () => voyagerLatencyRows.slice(compactMissionHud ? -2 : -4).reverse(),
    [compactMissionHud, voyagerLatencyRows]
  );

  return (
    <div
      className={`absolute right-8 bottom-10 z-30 ${
        compactMissionHud ? "w-[min(420px,38vw)] space-y-2" : "w-[min(560px,46vw)] space-y-3"
      } pointer-events-none`}
    >
      <div className={`rounded-2xl border border-white/10 bg-black/45 backdrop-blur-md ${compactMissionHud ? "p-3" : "p-4"} shadow-[0_0_40px_rgba(0,243,255,0.1)]`}>
        <div className="flex items-center justify-between text-[10px] tracking-[0.2em] text-cyan-200/80 font-mono uppercase">
          <span>Mission Control</span>
          <span>{workspaceGalaxy}</span>
        </div>
        <div className="mt-2 min-h-[52px]">
          <AnimatePresence mode="wait">
            {taskPulse ? (
              <motion.div
                key={taskPulse.taskId + String(taskPulse.timestamp)}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-1"
              >
                <div className="text-xs text-cyan-100 font-semibold tracking-wide">
                  {PHASE_LABEL[taskPulse.phase] || taskPulse.phase}
                </div>
                <div className="text-sm text-white/90">{taskPulse.action}</div>
                {!compactMissionHud ? (
                  <div className="text-xs text-white/60 line-clamp-2">
                    {taskPulse.thought || "Processing tactical reasoning stream."}
                  </div>
                ) : null}
              </motion.div>
            ) : (
              <motion.div
                key="idle-thought"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-xs text-white/50"
              >
                Awaiting mission pulse.
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <div className={`rounded-2xl border border-white/10 bg-black/45 backdrop-blur-md ${compactMissionHud ? "p-3" : "p-4"} shadow-[0_0_40px_rgba(57,255,20,0.08)]`}>
        <div className="text-[10px] tracking-[0.2em] text-emerald-200/80 font-mono uppercase">
          Action Timeline
        </div>
        <div className={`mt-3 space-y-2 ${compactMissionHud ? "max-h-[160px]" : "max-h-[240px]"} overflow-auto pr-1`}>
          {timeline.length === 0 ? (
            <div className="text-xs text-white/50">No timeline entries yet.</div>
          ) : (
            timeline.map((entry) => (
              <div
                key={entry.id}
                className="rounded-lg border border-white/5 bg-white/[0.03] px-3 py-2"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs text-white/90 font-medium">{entry.title}</span>
                  <span className={`text-[10px] uppercase tracking-wider ${STATUS_TONE[entry.status] || "text-white/60"}`}>
                    {entry.status}
                  </span>
                </div>
                {entry.detail && !compactMissionHud ? (
                  <div className="mt-1 text-[11px] text-white/60 line-clamp-2">
                    {entry.detail}
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>
        <div className={`${compactMissionHud ? "mt-2" : "mt-3"} border-t border-white/10 pt-2`}>
          <div className="text-[10px] tracking-[0.2em] text-cyan-200/70 font-mono uppercase">
            Voyager Latency
          </div>
          <div className="mt-2 space-y-1">
            {latencyRows.length === 0 ? (
              <div className="text-[11px] text-white/45">No voyager latency rows.</div>
            ) : (
              latencyRows.map((row) => (
                <div
                  key={row.id}
                  className="flex items-center justify-between rounded-md border border-white/5 bg-white/[0.02] px-2 py-1"
                >
                  <span className="text-[11px] text-white/70">{row.label}</span>
                  <span
                    className={`text-[11px] font-mono ${
                      row.status === "ok" ? "text-emerald-300" : "text-rose-300"
                    }`}
                  >
                    {Math.round(row.latencyMs)}ms
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
