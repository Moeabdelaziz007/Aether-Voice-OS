"use client";
/**
 * AetherOS V5 — Expert-Level Voice Portal
 *
 * Design DNA:
 * • Siri iOS 18: Edge-glow chromatic border reacting to AI state
 * • Whispr Flow:  Invisible UI, floating pill command bar
 * • ChatGPT AVM: Presence orb with ambient aura breathing
 * • Gemini Live:  Multi-layer radial gradient atmosphere
 *
 * Zero clutter. Every pixel intentional.
 */

import { useEffect, useRef, useMemo, useCallback, useState } from "react";
import AetherLine from "@/components/AetherLine";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useGeminiLive } from "@/hooks/useGeminiLive";
import {
    useAetherStore,
    ACCENT_COLORS,
    SUPERPOWER_META,
    type Superpowers,
    type AccentColor,
} from "@/store/useAetherStore";

// ── Color config per accent ──────────────────────────────────────
const ACCENT_RGB: Record<AccentColor, [number, number, number]> = {
    cyan: [0, 243, 255],
    purple: [188, 19, 254],
    amber: [245, 158, 11],
    emerald: [16, 185, 129],
    rose: [244, 63, 94],
};

export default function AetherPortal() {
    const status = useAetherStore((s) => s.status);
    const engineState = useAetherStore((s) => s.engineState);
    const visionActive = useAetherStore((s) => s.visionActive);
    const transcript = useAetherStore((s) => s.transcript);
    const preferences = useAetherStore((s) => s.preferences);
    const settingsOpen = useAetherStore((s) => s.settingsOpen);
    const toggleSuperpower = useAetherStore((s) => s.toggleSuperpower);
    const toggleSettings = useAetherStore((s) => s.toggleSettings);

    const portalRef = useRef<HTMLDivElement>(null);
    const hasStarted = useRef(false);

    // Live AI hooks
    const audio = useAudioPipeline();
    const gemini = useGeminiLive();

    const handleStart = async () => {
        if (hasStarted.current || isActive) return;
        hasStarted.current = true;
        try {
            await audio.start();
            await gemini.connect();
        } catch (err) {
            console.error("Failed to start Aether:", err);
            hasStarted.current = false;
        }
    };

    // Wire audio data flows
    useEffect(() => {
        if (audio.onPCMChunk) {
            audio.onPCMChunk.current = (pcm: ArrayBuffer) => gemini.sendAudio(pcm);
        }
        if (gemini.onAudioResponse) {
            gemini.onAudioResponse.current = (pcm: ArrayBuffer) => audio.playPCM(pcm);
        }
        if (gemini.onInterrupt) {
            gemini.onInterrupt.current = () => console.log("User interrupted AI");
        }
    }, [audio, gemini]);

    // ── 1. Drive CSS custom properties from persona state ────────
    useEffect(() => {
        const root = document.documentElement;
        const rgb = ACCENT_RGB[preferences.accentColor] || ACCENT_RGB.cyan;

        root.style.setProperty("--accent-r", String(rgb[0]));
        root.style.setProperty("--accent-g", String(rgb[1]));
        root.style.setProperty("--accent-b", String(rgb[2]));

        // Glow intensity based on engine state
        let intensity = 0.2;
        let edgeOpacity = 0;

        switch (engineState) {
            case "LISTENING":
                intensity = 0.6;
                edgeOpacity = 0.7;
                break;
            case "THINKING":
                intensity = 0.8;
                edgeOpacity = 0.5;
                break;
            case "SPEAKING":
                intensity = 1.0;
                edgeOpacity = 0.9;
                break;
            case "INTERRUPTING":
                intensity = 1.2;
                edgeOpacity = 1.0;
                // Override to red for interruption
                root.style.setProperty("--accent-r", "239");
                root.style.setProperty("--accent-g", "68");
                root.style.setProperty("--accent-b", "68");
                break;
            default:
                intensity = 0.2;
                edgeOpacity = 0;
        }

        root.style.setProperty("--glow-intensity", String(intensity));
        root.style.setProperty("--edge-glow-opacity", String(edgeOpacity));
    }, [preferences.accentColor, engineState]);

    // ── 2. Get latest transcript whispers ────────────────────────
    const lastUser = useMemo(() => {
        if (preferences.transcriptMode === "hidden") return null;
        return [...transcript].reverse().find((m) => m.role === "user");
    }, [transcript, preferences.transcriptMode]);

    const lastAgent = useMemo(() => {
        if (preferences.transcriptMode === "hidden") return null;
        return [...transcript].reverse().find((m) => m.role === "agent");
    }, [transcript, preferences.transcriptMode]);

    // ── 3. State label (ultra-minimal) ──────────────────────────
    const stateLabel = useMemo(() => {
        switch (status) {
            case "disconnected": return "tap to begin";
            case "connecting": return "awakening";
            case "connected":
            case "listening": return "listening";
            case "speaking": return "speaking";
            case "error": return "reconnecting";
            default: return "";
        }
    }, [status]);

    const isActive = status !== "disconnected";

    // ── 4. Connection heartbeat class ───────────────────────────
    const heartbeatClass = useMemo(() => {
        if (status === "error") return "heartbeat error";
        if (status === "connecting") return "heartbeat connecting";
        if (status === "connected" || status === "listening" || status === "speaking") return "heartbeat connected";
        return "heartbeat";
    }, [status]);

    // ═════════════════════════════════════════════════════════════
    // RENDER
    // ═════════════════════════════════════════════════════════════
    return (
        <>
            {/* Siri-style Edge Glow */}
            <div className="edge-glow" />

            <div ref={portalRef} className="portal">
                {/* ── TOP BAR: Brand + Mode Dots ── */}
                <div className="top-bar">
                    <span
                        className="brand-mark"
                        onClick={toggleSettings}
                        role="button"
                        tabIndex={0}
                        aria-label="Open settings"
                    >
                        AETHER
                    </span>
                    <div className="mode-indicators">
                        <div
                            className={`mode-dot ${isActive ? "active" : ""}`}
                            data-mode="voice"
                            title="Voice"
                        />
                        <div
                            className={`mode-dot ${visionActive ? "active" : ""}`}
                            data-mode="vision"
                            title="Vision"
                        />
                        <div
                            className={`mode-dot ${preferences.superpowers.codeSearch ? "active" : ""}`}
                            data-mode="code"
                            title="Code"
                        />
                    </div>
                </div>

                {/* ── HERO ZONE: Whispers + Orb ── */}
                <div className="hero-zone">
                    {/* User's last words — ghost text above */}
                    {lastUser && (
                        <div className="user-whisper" key={lastUser.id}>
                            &ldquo;{lastUser.content}&rdquo;
                        </div>
                    )}

                    {/* The Orb — AetherLine visualizer */}
                    <div className="orb-container" onClick={handleStart} style={{ cursor: isActive ? 'default' : 'pointer' }}>
                        <div className="orb-aura" />
                        <AetherLine />
                    </div>

                    {/* State label below the orb */}
                    <div className={`state-label ${isActive ? "active" : ""}`}>
                        {stateLabel}
                    </div>

                    {/* Agent's response — elegant text below */}
                    {lastAgent && (
                        <div className="agent-whisper" key={lastAgent.id}>
                            {lastAgent.content}
                        </div>
                    )}
                </div>

                {/* ── COMMAND BAR: Floating pill with power icons ── */}
                <div className="command-bar">
                    {(Object.keys(SUPERPOWER_META) as (keyof Superpowers)[]).map((key) => {
                        const meta = SUPERPOWER_META[key];
                        const isOn = preferences.superpowers[key];
                        return (
                            <button
                                key={key}
                                className={`power-btn ${isOn ? "active" : ""}`}
                                onClick={() => toggleSuperpower(key)}
                                title={meta.label}
                                aria-label={`${meta.label}: ${isOn ? "on" : "off"}`}
                            >
                                {meta.icon}
                            </button>
                        );
                    })}

                    <div className="bar-divider" />

                    {/* Settings gear */}
                    <button
                        className="power-btn"
                        onClick={toggleSettings}
                        title="Settings"
                        aria-label="Open settings"
                    >
                        ⚙️
                    </button>

                    <div className={heartbeatClass} />
                </div>
            </div>

            {/* ── SETTINGS OVERLAY ── */}
            {settingsOpen && <SettingsPanel />}
        </>
    );
}

// ═════════════════════════════════════════════════════════════════
// SETTINGS PANEL — Glassmorphism overlay
// ═════════════════════════════════════════════════════════════════
function SettingsPanel() {
    const preferences = useAetherStore((s) => s.preferences);
    const persona = useAetherStore((s) => s.persona);
    const setPreferences = useAetherStore((s) => s.setPreferences);
    const setPersona = useAetherStore((s) => s.setPersona);
    const toggleSettings = useAetherStore((s) => s.toggleSettings);
    const resetPreferences = useAetherStore((s) => s.resetPreferences);

    const accentColors: AccentColor[] = ["cyan", "purple", "amber", "emerald", "rose"];

    return (
        <div className="settings-overlay" onClick={(e) => {
            if (e.target === e.currentTarget) toggleSettings();
        }}>
            <div className="settings-panel" role="dialog" aria-label="Settings">
                {/* Close */}
                <button className="settings-close" onClick={toggleSettings} aria-label="Close">
                    ✕
                </button>

                {/* Accent Color */}
                <div className="settings-section">
                    <div className="settings-section__title">Accent Color</div>
                    <div className="color-picker">
                        {accentColors.map((color) => (
                            <div
                                key={color}
                                className={`color-swatch ${preferences.accentColor === color ? "selected" : ""}`}
                                style={{
                                    backgroundColor: ACCENT_COLORS[color].primary,
                                    color: ACCENT_COLORS[color].primary,
                                }}
                                onClick={() => setPreferences({ accentColor: color })}
                                role="button"
                                tabIndex={0}
                                aria-label={`Set accent color to ${color}`}
                            />
                        ))}
                    </div>
                </div>

                {/* Voice Tone */}
                <div className="settings-section">
                    <div className="settings-section__title">Voice Tone</div>
                    <div className="chip-grid">
                        {(["professional", "casual", "friendly", "mentor", "minimal"] as const).map((tone) => (
                            <div
                                key={tone}
                                className={`chip ${preferences.voiceTone === tone ? "selected" : ""}`}
                                onClick={() => setPreferences({ voiceTone: tone })}
                            >
                                {tone}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Experience Level */}
                <div className="settings-section">
                    <div className="settings-section__title">Experience Level</div>
                    <div className="chip-grid">
                        {(["beginner", "intermediate", "expert", "wizard"] as const).map((level) => (
                            <div
                                key={level}
                                className={`chip ${preferences.experienceLevel === level ? "selected" : ""}`}
                                onClick={() => setPreferences({ experienceLevel: level })}
                            >
                                {level}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Transcript Mode */}
                <div className="settings-section">
                    <div className="settings-section__title">Transcript Display</div>
                    <div className="chip-grid">
                        {(["whisper", "persistent", "hidden"] as const).map((mode) => (
                            <div
                                key={mode}
                                className={`chip ${preferences.transcriptMode === mode ? "selected" : ""}`}
                                onClick={() => setPreferences({ transcriptMode: mode })}
                            >
                                {mode}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Persona Name */}
                <div className="settings-section">
                    <div className="settings-section__title">Persona Name</div>
                    <input
                        type="text"
                        value={preferences.personaName}
                        onChange={(e) => {
                            setPreferences({ personaName: e.target.value });
                            setPersona({ name: e.target.value });
                        }}
                        className="chip"
                        style={{
                            width: "100%",
                            background: "var(--glass)",
                            border: "1px solid var(--glass-border)",
                            color: "var(--text-100)",
                            outline: "none",
                            padding: "0.5rem 1rem",
                        }}
                    />
                </div>

                {/* Reset */}
                <div className="settings-section">
                    <button
                        className="chip"
                        onClick={resetPreferences}
                        style={{ color: "rgba(239, 68, 68, 0.7)" }}
                    >
                        ↺ Reset to defaults
                    </button>
                </div>
            </div>
        </div>
    );
}
