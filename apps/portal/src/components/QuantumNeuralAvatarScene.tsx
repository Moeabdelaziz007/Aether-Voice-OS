"use client";

import React, { useMemo, memo } from 'react';
import { motion } from 'framer-motion';
import { useAetherStore, type EngineState, type AvatarCinematicState } from '@/store/useAetherStore';
import { QuantumConsciousnessCore } from './avatar/QuantumConsciousnessCore';
import { HolographicVoiceRings, NeuralSynapticMesh } from './avatar/AvatarSubComponents';

/**
 * AvatarSceneContent
 * Direct 3D logic to be consumed by UnifiedScene's Canvas.
 * Separated from the 2D wrapper to maintain WebGL context efficiency.
 */
export const AvatarSceneContent = memo(function AvatarSceneContent({
  state,
  cinematicState,
  mouthOpenness = 0,
  variant = "standard",
  showConnections = true,
  gazeTarget = [0, 0, 1.25],
  lowMotionMode = false,
}: {
  state: EngineState;
  cinematicState: AvatarCinematicState;
  mouthOpenness?: number;
  variant?: string;
  showConnections?: boolean;
  gazeTarget?: [number, number, number];
  lowMotionMode?: boolean;
}) {
  const micLevel = useAetherStore((s) => s.micLevel);
  const speakerLevel = useAetherStore((s) => s.speakerLevel);
  const audioLevel = state === "SPEAKING" ? speakerLevel : micLevel;

  return (
    <group>
      {/* 1. The Core Being */}
      <QuantumConsciousnessCore
        state={state}
        audioLevel={audioLevel}
        lowMotionMode={lowMotionMode}
      />

      {/* 2. Reactive Voice Rings */}
      <HolographicVoiceRings
        state={state}
        audioLevel={audioLevel}
        cinematicState={cinematicState}
      />

      {/* 3. Neural Connectivity Layer */}
      {showConnections && (
        <NeuralSynapticMesh
          state={state}
          audioLevel={audioLevel}
          nodeCount={variant === "immersive" ? 40 : 20}
        />
      )}
    </group>
  );
});

/**
 * QuantumNeuralAvatarScene.tsx
 * The centerpiece of the GemiGram interface (2D Responsive Wrapper).
 * Acts as a backup or specific HUD overlay.
 */
export default function QuantumNeuralAvatarScene() {
  const engineState = useAetherStore((s) => s.engineState);
  const micLevel = useAetherStore((s) => s.micLevel);

  // Derived visual parameters based on state
  const stateConfig = useMemo(() => {
    switch (engineState) {
      case 'LISTENING':
        return {
          scale: 1 + micLevel * 2,
          color: 'var(--neon-cyan)',
          blur: 'blur(40px)',
          opacity: 0.8,
          animateSpeed: 2
        };
      case 'THINKING':
        return {
          scale: 1.1,
          color: 'var(--neon-purple)',
          blur: 'blur(60px)',
          opacity: 0.6,
          animateSpeed: 0.5
        };
      case 'SPEAKING':
        return {
          scale: 1.2,
          color: 'var(--neon-pink)',
          blur: 'blur(50px)',
          opacity: 0.9,
          animateSpeed: 3
        };
      case 'INTERRUPTING':
        return {
          scale: 1.5,
          color: '#FF1A1A',
          blur: 'blur(80px)',
          opacity: 1,
          animateSpeed: 5
        };
      default: // IDLE
        return {
          scale: 1,
          color: 'rgba(255, 255, 255, 0.1)',
          blur: 'blur(100px)',
          opacity: 0.3,
          animateSpeed: 1
        };
    }
  }, [engineState, micLevel]);

  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
      {/* Background Atmosphere */}
      <motion.div
        animate={{
          backgroundColor: stateConfig.color,
          opacity: stateConfig.opacity * 0.1,
        }}
        className="absolute inset-0 z-0 transition-colors duration-1000"
      />

      {/* The Neural Core */}
      <div className="relative z-10 w-96 h-96">
        {/* Outer Glow Ring */}
        <motion.div
          animate={{
            scale: stateConfig.scale * 1.5,
            borderColor: stateConfig.color,
            opacity: stateConfig.opacity * 0.2,
          }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="absolute inset-0 rounded-full border border-white/20 blur-xl"
        />

        {/* Primary Amorphous Orb */}
        <motion.div
          animate={{
            scale: stateConfig.scale,
            backgroundColor: stateConfig.color,
            boxShadow: `0 0 100px ${stateConfig.color}`,
          }}
          transition={{
            type: "spring",
            stiffness: 100,
            damping: 20,
            duration: 0.3
          }}
          className="absolute inset-0 rounded-full mix-blend-screen overflow-hidden"
          style={{ filter: stateConfig.blur }}
        >
          {/* Generative Noise Layers (CSS Gradients) */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20 / stateConfig.animateSpeed, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/20 to-transparent opacity-50"
          />
        </motion.div>

        {/* The "Eye" of the Nexus */}
        <motion.div
          animate={{
            scale: engineState === 'THINKING' ? [1, 1.2, 1] : 1,
            opacity: stateConfig.opacity,
          }}
          transition={{ repeat: engineState === 'THINKING' ? Infinity : 0, duration: 1.5 }}
          className="absolute inset-[40%] rounded-full bg-white shadow-[0_0_40px_rgba(255,255,255,0.8)] z-20"
        />

        {/* Audio Wave Geometry (Simulated) */}
        <div className="absolute inset-0 flex items-center justify-center gap-1 opacity-40">
          {Array.from({ length: 12 }).map((_, i) => (
            <motion.div
              key={i}
              animate={{
                height: engineState === 'SPEAKING' ? [20, 60, 20] : 10,
                backgroundColor: stateConfig.color
              }}
              transition={{
                delay: i * 0.1,
                repeat: Infinity,
                duration: 0.5
              }}
              className="w-1 rounded-full"
            />
          ))}
        </div>
      </div>

      {/* HUD Status Label */}
      <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        <motion.span
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="text-[10px] uppercase tracking-[0.4em] font-black text-white/40"
        >
          Neural Engine Status
        </motion.span>
        <span className="text-xl font-black uppercase tracking-tighter text-white">
          {engineState}
        </span>
      </div>
    </div>
  );
}
