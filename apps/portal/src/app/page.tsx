"use client";
/**
 * AetherOS — Quantum Neural Voice Portal
 *
 * An immersive single-page voice interface featuring:
 * - Quantum Neural Avatar with advanced 3D visualization
 * - Fluid Thought Particles for conversation visualization
 * - State-responsive ambient effects and edge glow
 * - Dynamic realm morphing triggered by voice commands
 * 
 * The Quantum Neural Avatar is the living heart of the interface,
 * evolving and pulsing in response to voice patterns and system state.
 */

import { useEffect, useMemo } from "react";
import { LayoutGroup, motion, AnimatePresence } from "framer-motion";
import QuantumNeuralAvatar from "@/components/QuantumNeuralAvatar";
import FluidThoughtParticles from "@/components/FluidThoughtParticles";
import RealmController from "@/components/realms/RealmController";
import CommandBar from "@/components/shared/CommandBar";
import EdgeGlow from "@/components/shared/EdgeGlow";
import HUDContainer from "@/components/HUD/HUDContainer";
import SystemFailure from "@/components/HUD/SystemFailure";
import PoweredByStrip from "@/components/shared/PoweredByStrip";
import ParticleField from "@/components/shared/ParticleField";
import SilentHintsOverlay from "@/components/shared/SilentHintsOverlay";
import { useVoiceCommands } from "@/hooks/useVoiceCommands";
import { useAetherStore } from "@/store/useAetherStore";

// Quantum Neural Color Palette
const ACCENT_RGB: Record<string, [number, number, number]> = {
    cyan: [0, 243, 255],
    purple: [188, 19, 254],
    amber: [245, 158, 11],
    emerald: [16, 185, 129],
    rose: [244, 63, 94],
    green: [57, 255, 20],    // Neon green - Primary
    blue: [59, 130, 246],
};

// State intensity mapping for visual effects
const STATE_INTENSITY: Record<string, number> = {
    IDLE: 0.2,
    LISTENING: 0.6,
    THINKING: 0.8,
    SPEAKING: 1.0,
    INTERRUPTING: 1.2,
};

export default function AetherPortal() {
    const preferences = useAetherStore((s) => s.preferences);
    const engineState = useAetherStore((s) => s.engineState);
    const currentRealm = useAetherStore((s) => s.currentRealm);

    // Wire voice command → realm navigation
    useVoiceCommands();

    // Avatar size based on realm
    const avatarConfig = useMemo(() => {
        switch (currentRealm) {
            case "void":
                return { size: "large" as const, variant: "immersive" as const };
            case "neural":
                return { size: "fullscreen" as const, variant: "immersive" as const };
            default:
                return { size: "medium" as const, variant: "detailed" as const };
        }
    }, [currentRealm]);

    // ── Drive CSS custom properties from accent color ────────
    useEffect(() => {
        const root = document.documentElement;
        const rgb = ACCENT_RGB[preferences.accentColor] || ACCENT_RGB.green;
        
        root.style.setProperty("--accent-r", String(rgb[0]));
        root.style.setProperty("--accent-g", String(rgb[1]));
        root.style.setProperty("--accent-b", String(rgb[2]));
        root.style.setProperty(
            "--glow-intensity",
            String(STATE_INTENSITY[engineState] ?? 0.2)
        );
    }, [preferences.accentColor, engineState]);

    return (
        <LayoutGroup>
            {/* Quantum Neural Particle Field — Deep background layer */}
            <ParticleField count={45} />

            {/* Fluid Thought Particles — 3D conversation experience */}
            <FluidThoughtParticles />

            {/* Chromatic Edge Glow — State-responsive border */}
            <EdgeGlow />

            {/* HUD Frame (corner markers + scan line) */}
            <HUDContainer>
                <div className="relative w-full h-screen overflow-hidden aether-boot-enter">
                    {/* Quantum Neural Avatar — The Living AI Consciousness */}
                    <motion.div 
                        className="absolute inset-0 flex items-center justify-center z-10"
                        layoutId="quantum-avatar-container"
                        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                    >
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={currentRealm}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 1.1 }}
                                transition={{ duration: 0.4, ease: "easeOut" }}
                            >
                                <QuantumNeuralAvatar 
                                    size={avatarConfig.size}
                                    variant={avatarConfig.variant}
                                    showConnections={true}
                                />
                            </motion.div>
                        </AnimatePresence>
                    </motion.div>

                    {/* Ambient State Indicator */}
                    <motion.div
                        className="absolute top-6 left-1/2 -translate-x-1/2 z-20"
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ 
                            opacity: engineState !== "IDLE" ? 1 : 0,
                            y: engineState !== "IDLE" ? 0 : -20,
                        }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-black/40 backdrop-blur-md border border-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.2)]">
                            <motion.div
                                className="w-2 h-2 rounded-full bg-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),1)]"
                                animate={{
                                    scale: [1, 1.3, 1],
                                    opacity: [0.8, 1, 0.8],
                                }}
                                transition={{
                                    duration: 1.5,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                }}
                            />
                            <span className="text-[10px] font-mono tracking-wider text-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.9)] uppercase">
                                {engineState}
                            </span>
                        </div>
                    </motion.div>

                    {/* Autonomous Repair Overlay */}
                    <SystemFailure />

                    {/* Active realm content */}
                    <RealmController />
                </div>
            </HUDContainer>

            {/* Silent tool result hints — top-right floating cards */}
            <SilentHintsOverlay />

            {/* Tech attribution — ambient, premium */}
            <PoweredByStrip />

            {/* Command bar — always visible at bottom */}
            <CommandBar />
        </LayoutGroup>
    );
}
