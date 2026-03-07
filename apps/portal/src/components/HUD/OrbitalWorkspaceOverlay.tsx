"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

const LANE_RADIUS: Record<"inner" | "mid" | "outer", number> = {
  inner: 120,
  mid: 180,
  outer: 250,
};

const LANE_COLOR: Record<"inner" | "mid" | "outer", string> = {
  inner: "rgba(0,243,255,0.3)",
  mid: "rgba(57,255,20,0.25)",
  outer: "rgba(188,19,254,0.25)",
};

export default function OrbitalWorkspaceOverlay() {
  const orbitRegistry = useAetherStore((s) => s.orbitRegistry);
  const focusedPlanetId = useAetherStore((s) => s.focusedPlanetId);
  const orbitalLayoutPreset = useAetherStore((s) => s.orbitalLayoutPreset);
  const focusModeEnvironment = useAetherStore((s) => s.focusModeEnvironment);

  const planets = useMemo(
    () =>
      Object.values(orbitRegistry).filter(
        (planet) => planet.isMaterialized && !planet.isCollapsed
      ),
    [orbitRegistry]
  );

  const presetScale =
    orbitalLayoutPreset === "inner"
      ? 0.82
      : orbitalLayoutPreset === "outer"
        ? 1.22
        : 1;

  return (
    <div className="absolute inset-0 pointer-events-none z-20 overflow-hidden">
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        {(Object.keys(LANE_RADIUS) as Array<keyof typeof LANE_RADIUS>).map((lane) => (
          <div
            key={lane}
            className="absolute rounded-full border border-dashed"
            style={{
              width: LANE_RADIUS[lane] * 2 * presetScale,
              height: LANE_RADIUS[lane] * 2 * presetScale,
              marginLeft: -LANE_RADIUS[lane] * presetScale,
              marginTop: -LANE_RADIUS[lane] * presetScale,
              borderColor: LANE_COLOR[lane],
              opacity: focusModeEnvironment ? 0.8 : 0.45,
            }}
          />
        ))}

        {planets.map((planet) => {
          const isFocused = focusedPlanetId === planet.planetId;
          return (
            <motion.div
              key={planet.planetId}
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{
                x: planet.position.x * presetScale,
                y: planet.position.y * presetScale,
                scale: isFocused ? 1.25 : 0.95,
                opacity: isFocused ? 1 : 0.85,
              }}
              transition={{ type: "spring", stiffness: 220, damping: 22 }}
              className="absolute -translate-x-1/2 -translate-y-1/2"
            >
              <div
                className={`h-3 w-3 rounded-full ${isFocused ? "shadow-[0_0_24px_rgba(0,243,255,0.95)]" : "shadow-[0_0_14px_rgba(57,255,20,0.65)]"}`}
                style={{
                  background: isFocused ? "#00f3ff" : "#39ff14",
                }}
              />
              <div className="mt-1 text-[9px] text-white/70 font-mono tracking-wider whitespace-nowrap text-center">
                {planet.planetId}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
