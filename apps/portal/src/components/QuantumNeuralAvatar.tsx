"use client";

import React, { useMemo } from "react";
import { useAetherStore } from "@/store/useAetherStore";
import { AvatarCanvas } from "./avatar/AvatarCanvas";
import { AvatarEmotion } from "./avatar/AvatarEmotion";
import { useAvatarVisemes } from "@/hooks/avatar/useAvatarVisemes";
import { AvatarSceneContent } from "./QuantumNeuralAvatarScene";

interface AvatarProps {
  size?: "icon" | "small" | "medium" | "large" | "fullscreen";
  variant?: "minimal" | "standard" | "detailed" | "immersive";
  showConnections?: boolean;
}

/**
 * QuantumNeuralAvatar — The High-Performance Evolutionary Container
 * 
 * Fission complete. This component is now a pure container that orchestrates:
 * 1. Emotional Auras (AvatarEmotion)
 * 2. Visual Hook (useAvatarVisemes)
 * 3. 3D Canvas Env (AvatarCanvas)
 * 4. Declarative Scene (AvatarSceneContent)
 */
export default function QuantumNeuralAvatar({
  size = "medium",
  variant = "standard",
  showConnections = true,
}: AvatarProps) {
  const { mouthOpenness, engineState } = useAvatarVisemes();
  const cinematicState = useAetherStore((s) => s.avatarCinematicState);
  const gazeTarget = useAetherStore((s) => s.gazeTarget);

  // Size mapping
  const sizeMap = {
    icon: 4,
    small: 6,
    medium: 10,
    large: 14,
    fullscreen: 18,
  };

  const containerStyles = {
    icon: { width: 64, height: 64 },
    small: { width: 160, height: 160 },
    medium: { width: 320, height: 320 },
    large: { width: 500, height: 500 },
    fullscreen: { width: "100%", height: "100%" },
  };

  const stateColor = useMemo(() => {
    switch (engineState) {
      case "SPEAKING": return "#00ff88";
      case "LISTENING": return "#39ff14";
      case "THINKING": return "#ffd700";
      case "INTERRUPTING": return "#ff1744";
      default: return "#4b5563";
    }
  }, [engineState]);

  return (
    <div
      className="quantum-neural-avatar relative"
      style={{
        ...containerStyles[size],
        borderRadius: size === "icon" ? "50%" : "32px",
        overflow: "hidden",
        background: "#050505",
      }}
    >
      <AvatarEmotion
        engineState={engineState}
        color={stateColor}
        intensity={mouthOpenness}
      />

      <AvatarCanvas cameraZ={sizeMap[size]}>
        <AvatarSceneContent
          mouthOpenness={mouthOpenness}
          state={engineState}
          cinematicState={cinematicState}
          variant={variant}
          showConnections={showConnections && variant !== "minimal"}
          lowMotionMode={false}
          gazeTarget={gazeTarget}
        />
      </AvatarCanvas>
    </div>
  );
}

export function AvatarIcon() { return <QuantumNeuralAvatar size="icon" variant="minimal" />; }
export function AvatarSmall() { return <QuantumNeuralAvatar size="small" variant="minimal" />; }
export function AvatarMedium() { return <QuantumNeuralAvatar size="medium" variant="standard" />; }
export function AvatarLarge() { return <QuantumNeuralAvatar size="large" variant="detailed" />; }
export function AvatarFullscreen() { return <QuantumNeuralAvatar size="fullscreen" variant="immersive" />; }
