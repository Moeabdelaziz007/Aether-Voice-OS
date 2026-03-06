"use client";
/**
 * AetherOS — Quantum Neural Voice Portal
 *
 * An immersive single-page voice interface featuring:
 * - Unified 3D Scene with consolidated WebGL context
 * - State-responsive ambient effects and edge glow
 * - Dynamic realm morphing triggered by voice commands
 * 
 * Performance Optimized: Single Canvas for all 3D elements
 */

import { useEffect, useMemo } from "react";
import { LayoutGroup, motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
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
import NeuralBackground from "@/components/shared/NeuralBackground";

// Dynamic import for 3D scene to improve initial load
const UnifiedScene = dynamic(() => import("@/components/UnifiedScene"), {
    ssr: false,
    loading: () => <div className="fixed inset-0 bg-black" />,
});

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

    // Avatar config based on realm (optimized for unified scene)
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

    // State indicator color
    const stateIndicatorColor = useMemo(() => {
        switch (engineState) {
            case "SPEAKING": return "#00ff88";
            case "LISTENING": return "#39ff14";
            case "THINKING": return "#ffd700";
            case "INTERRUPTING": return "#ff1744";
            default: return "#4b5563";
        }
    }, [engineState]);

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
            {/* ── Ambient Background Layers ── */}
            <NeuralBackground />
            <ParticleField count={20} />

            {/* Unified 3D Scene — Single WebGL Context */}
            <UnifiedScene
                avatarConfig={avatarConfig}
                showAvatar={true}
                showParticles={true}
                showConnections={true}
            />

            {/* Chromatic Edge Glow — State-responsive border */}
            <EdgeGlow />

            {/* HUD Frame (corner markers + scan line) */}
            <HUDContainer>
                <div className="relative w-full h-screen overflow-hidden aether-boot-enter">
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
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: stateIndicatorColor }}
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
                            <span
                                className="text-[10px] font-mono tracking-wider uppercase"
                                style={{ color: stateIndicatorColor, opacity: 0.9 }}
                            >
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
