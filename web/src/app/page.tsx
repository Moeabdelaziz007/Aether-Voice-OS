"use client";
/**
 * Aether Voice Portal — Main Page.
 *
 * The Living Voice Portal: an immersive, voice-first interface
 * centered on the AetherOrb, with ambient floating transcript
 * and ephemeral HUD telemetry cards.
 *
 * No chatbox. No text input. A breathing, chromatic organism.
 */

import { useEffect, useRef } from "react";
import AetherOrb from "@/components/AetherOrb";
import AmbientTranscript from "@/components/AmbientTranscript";
import HUDCards from "@/components/HUDCards";
import { useAetherStore, type EngineState } from "@/store/useAetherStore";

// Atmospheric color map per engine state
const ATM_COLORS: Record<EngineState, { hue: number; sat: number; brightness: number }> = {
    IDLE: { hue: 240, sat: 10, brightness: 4 },
    LISTENING: { hue: 245, sat: 25, brightness: 8 },
    THINKING: { hue: 35, sat: 40, brightness: 10 },
    SPEAKING: { hue: 190, sat: 35, brightness: 10 },
    INTERRUPTING: { hue: 0, sat: 40, brightness: 12 },
};

export default function VoicePortal() {
    const engineState = useAetherStore((s) => s.engineState);
    const status = useAetherStore((s) => s.status);
    const visionActive = useAetherStore((s) => s.visionActive);
    const portalRef = useRef<HTMLDivElement>(null);

    // ─── Chromatic Atmosphere: update CSS custom properties ─────
    useEffect(() => {
        const root = document.documentElement;
        const target = ATM_COLORS[engineState] || ATM_COLORS.IDLE;
        root.style.setProperty("--atm-hue", String(target.hue));
        root.style.setProperty("--atm-sat", `${target.sat}%`);
        root.style.setProperty("--atm-brightness", `${target.brightness}%`);
    }, [engineState]);

    // Status label based on current state (minimal text, no chatbot labels)
    const stateLabel = (() => {
        switch (status) {
            case "disconnected": return "tap to begin";
            case "connecting": return "awakening…";
            case "connected":
            case "listening": return "listening";
            case "speaking": return "speaking";
            case "error": return "reconnecting…";
            default: return "";
        }
    })();

    const statusDotClass = (() => {
        switch (status) {
            case "connecting": return "status-dot--connecting";
            case "listening":
            case "connected": return "status-dot--listening";
            case "speaking": return "status-dot--speaking";
            case "error": return "status-dot--error";
            default: return "status-dot--idle";
        }
    })();

    return (
        <div ref={portalRef} className="portal">
            {/* Vision Active indicator */}
            {visionActive && (
                <div className="vision-indicator">
                    <span className="vision-indicator__dot" />
                    Vision Active
                </div>
            )}

            {/* Ambient AI transcript (top) */}
            <AmbientTranscript />

            {/* The Orb — the hero element */}
            <AetherOrb size={220} />

            {/* Minimal status label */}
            <div className="orb-label">
                <span className={`status-dot ${statusDotClass}`} />
                {stateLabel}
            </div>

            {/* HUD telemetry cards (bottom) */}
            <HUDCards />
        </div>
    );
}
