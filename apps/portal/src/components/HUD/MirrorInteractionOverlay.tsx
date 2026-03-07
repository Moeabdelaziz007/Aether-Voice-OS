"use client";

import React, { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

const colorByKind: Record<string, string> = {
  navigation: "bg-cyan-300/70",
  click: "bg-emerald-300/80",
  typing: "bg-violet-300/80",
  scroll: "bg-amber-300/80",
  capture: "bg-white/70",
};

export default function MirrorInteractionOverlay() {
  const mirrorFrames = useAetherStore((s) => s.mirrorFrames);
  const recent = useMemo(() => mirrorFrames.slice(-5), [mirrorFrames]);

  return (
    <div className="absolute inset-0 pointer-events-none z-20">
      <AnimatePresence>
        {recent.map((event, index) => {
          const left = typeof event.x === "number" ? `${Math.max(5, Math.min(95, event.x * 100))}%` : `${15 + index * 16}%`;
          const top = typeof event.y === "number" ? `${Math.max(10, Math.min(90, event.y * 100))}%` : `${20 + (index % 3) * 20}%`;
          const tint = colorByKind[event.eventKind] || "bg-white/70";
          return (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 0.9, scale: 1 }}
              exit={{ opacity: 0, scale: 1.25 }}
              transition={{ duration: 0.55 }}
              className="absolute"
              style={{ left, top }}
            >
              <div className={`h-4 w-4 rounded-full ${tint} shadow-[0_0_26px_rgba(255,255,255,0.45)]`} />
              <div className="mt-1 text-[10px] uppercase tracking-wide text-white/75 font-mono">
                {event.eventKind}
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
