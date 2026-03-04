"use client";

import { useAetherStore } from "@/store/useAetherStore";

/**
 * EdgeGlow — Siri-inspired chromatic screen border.
 * Visible primarily during SPEAKING state.
 */
export default function EdgeGlow() {
    const engineState = useAetherStore((s) => s.engineState);
    const isSpeaking = engineState === "SPEAKING";

    return <div className="edge-glow" style={{ opacity: isSpeaking ? 0.9 : 0 }} />;
}
