"use client";
/**
 * AetherOS — Single-Page Voice Portal.
 *
 * No page routing. The entire UI morphs between 5 realms
 * triggered by voice commands. The 3D Orb never disappears —
 * it resizes and repositions via Framer Motion layoutId.
 */

import { useEffect } from "react";
import { LayoutGroup } from "framer-motion";
import AetherOrb from "@/components/core/AetherOrb";
import RealmController from "@/components/realms/RealmController";
import CommandBar from "@/components/shared/CommandBar";
import EdgeGlow from "@/components/shared/EdgeGlow";
import HUDContainer from "@/components/HUD/HUDContainer";
import { useVoiceCommands } from "@/hooks/useVoiceCommands";
import { useAetherStore } from "@/store/useAetherStore";

export default function AetherPortal() {
    const preferences = useAetherStore((s) => s.preferences);
    const engineState = useAetherStore((s) => s.engineState);

    // Wire voice command → realm navigation
    useVoiceCommands();

    // ── Drive CSS custom properties from accent color ────────
    useEffect(() => {
        const root = document.documentElement;
        const ACCENT_RGB: Record<string, [number, number, number]> = {
            cyan: [0, 243, 255],
            purple: [188, 19, 254],
            amber: [245, 158, 11],
            emerald: [16, 185, 129],
            rose: [244, 63, 94],
        };

        const rgb = ACCENT_RGB[preferences.accentColor] || ACCENT_RGB.cyan;
        root.style.setProperty("--accent-r", String(rgb[0]));
        root.style.setProperty("--accent-g", String(rgb[1]));
        root.style.setProperty("--accent-b", String(rgb[2]));

        // Glow intensity based on engine state
        const intensityMap: Record<string, number> = {
            IDLE: 0.2,
            LISTENING: 0.6,
            THINKING: 0.8,
            SPEAKING: 1.0,
            INTERRUPTING: 1.2,
        };
        root.style.setProperty(
            "--glow-intensity",
            String(intensityMap[engineState] ?? 0.2)
        );
    }, [preferences.accentColor, engineState]);

    return (
        <LayoutGroup>
            {/* Siri-style edge glow */}
            <EdgeGlow />

            {/* HUD frame (corner markers + scan line) */}
            <HUDContainer>
                <div className="relative w-full h-screen overflow-hidden">
                    {/* The Orb — always visible, morphs between realms */}
                    <AetherOrb />

                    {/* Active realm content */}
                    <RealmController />
                </div>
            </HUDContainer>

            {/* Command bar — always visible at bottom */}
            <CommandBar />
        </LayoutGroup>
    );
}
