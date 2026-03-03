"use client";
import { useEffect, useRef } from "react";
import AetherLine from "@/components/AetherLine";
import {
    useAetherStore,
    ACCENT_COLORS,
    SUPERPOWER_META,
    type EngineState
} from "@/store/useAetherStore";
// Import some basic icons if lucide-react is installed, if not we fall back to emojis from store.
// The store has emojis in SUPERPOWER_META so we'll just use those to avoid dependency issues.

// Helper to map engine state to a base hue offset or intensity, 
// though the new CSS mostly relies on persona colors.
export default function AmbientVoicePortal() {
    const {
        status,
        engineState,
        visionActive,
        persona,
        preferences,
        toggleSuperpower
    } = useAetherStore();

    const portalRef = useRef<HTMLDivElement>(null);

    // ─── 1. Apply Persona Colors to CSS Variables ───────────
    useEffect(() => {
        const root = document.documentElement;
        const colorToken = ACCENT_COLORS[preferences.accentColor] || ACCENT_COLORS.cyan;

        // Extract RGB array from the config "r, g, b"
        const rgbVals = colorToken.rgb.split(',').map(v => parseInt(v.trim()));

        // Calculate a rough Hue for the radial gradient background
        // Simple approximation: check highest value
        let h = 190; // default cyan
        if (preferences.accentColor === 'rose') h = 340;
        if (preferences.accentColor === 'emerald') h = 150;
        if (preferences.accentColor === 'amber') h = 40;
        if (preferences.accentColor === 'purple') h = 280;

        // Increase brightness based on engine state
        let glowAlpha = 0.2;
        if (engineState === 'LISTENING') glowAlpha = 0.4;
        if (engineState === 'THINKING') glowAlpha = 0.6;
        if (engineState === 'SPEAKING') glowAlpha = 0.8;
        if (engineState === 'INTERRUPTING') { h = 0; glowAlpha = 0.9; }

        root.style.setProperty("--persona-hue", String(h));
        root.style.setProperty("--persona-glow", `rgba(${colorToken.rgb}, ${glowAlpha})`);
    }, [preferences.accentColor, engineState]);


    // ─── 2. Top Header: Persona & Multimodal ────────────────
    const renderHeader = () => (
        <header className="portal-header">
            {/* Persona Identity */}
            <div className="persona-badge">
                <h1 className="persona-name">{persona.name}</h1>
                <div className="persona-role">
                    {persona.role} • LVL {preferences.experienceLevel.toUpperCase()}
                </div>
                {persona.feeling && (
                    <div className="persona-feeling">{persona.feeling}</div>
                )}
            </div>

            {/* Multimodal Active Nodes */}
            <div className="multimodal-nodes hidden sm:flex">
                <div className={`node ${status === 'connected' || status === 'listening' || status === 'speaking' ? 'active' : ''}`} data-mode="voice" title="Voice Channel">
                    🎙️
                </div>
                <div className={`node ${visionActive ? 'active' : ''}`} data-mode="vision" title="Vision Channel">
                    👁️
                </div>
                <div className={`node ${preferences.superpowers.codeSearch ? 'active' : ''}`} data-mode="code" title="Codebase RAG">
                    {/* Using a code bracket or file icon */}
                    {'</>'}
                </div>
            </div>
        </header>
    );

    // ─── 3. Footer: Superpowers HUD ─────────────────────────
    const renderFooter = () => (
        <footer className="portal-footer">
            {/* Left: Active Superpowers Toggle */}
            <div className="superpowers-bar hide-scrollbar overflow-x-auto max-w-[70vw] pb-2 sm:pb-0">
                {(Object.keys(SUPERPOWER_META) as (keyof typeof SUPERPOWER_META)[]).map((key) => {
                    const meta = SUPERPOWER_META[key];
                    const isActive = preferences.superpowers[key];
                    return (
                        <button
                            key={key}
                            onClick={() => toggleSuperpower(key)}
                            className={`power-pill ${isActive ? 'active' : ''}`}
                            title={meta.desc}
                        >
                            <span className="power-icon">{meta.icon}</span>
                            <span className="hidden sm:inline">{meta.label}</span>
                        </button>
                    )
                })}
            </div>

            {/* Right: Minimal Connection Status */}
            <div className="conn-status" data-state={status}>
                <span className="conn-dot" />
                {status === 'disconnected' ? 'OFFLINE' :
                    status === 'connecting' ? 'BOOTING...' :
                        status === 'error' ? 'FAULT' : 'SYNCED'}
            </div>
        </footer>
    );

    // ─── 4. Ephemeral Transcripts (Whispers) ────────────────
    const renderWhispers = () => {
        const transcript = useAetherStore(s => s.transcript);
        if (preferences.transcriptMode === 'hidden' || transcript.length === 0) return null;

        // Get the latest user message and the latest agent message
        const lastUser = [...transcript].reverse().find(m => m.role === 'user');
        const lastAgent = [...transcript].reverse().find(m => m.role === 'agent');

        return (
            <div className="whisper-container">
                {lastUser && (
                    <div className="whisper-text user fade-in-up">
                        "{lastUser.content}"
                    </div>
                )}
                {lastAgent && (
                    <div className="whisper-text agent fade-in-up">
                        {lastAgent.content}
                    </div>
                )}
            </div>
        );
    };

    // ─── Render full UI ─────────────────────────────────────
    return (
        <div ref={portalRef} className="portal">
            {renderHeader()}

            <main className="portal-hero">
                {renderWhispers()}
                {/* 
                  The AetherLine serves as the primary visualizer. 
                  We let it fill the space. 
                */}
                <div className="w-full h-full flex items-center justify-center">
                    <AetherLine />
                </div>
            </main>

            {renderFooter()}
        </div>
    );
}
