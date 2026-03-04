"use client";
/**
 * AetherOrb — The Living Voice Entity.
 *
 * A breathing, reactive orb at the center of the experience.
 * Replaces traditional mic buttons with an organic voice presence.
 *
 * States:
 *   IDLE      → Slow pulsing nebula (navy → deep purple)
 *   LISTENING → Mic-energy ripples, faster breathing
 *   THINKING  → Internal particle swirl, amber glow
 *   SPEAKING  → Pulse with amplitude, cyan rings expand outward
 *   ERROR     → Red flash + shake
 */

import React, { useRef, useEffect, useCallback } from "react";
import { useAetherStore, type EngineState } from "@/store/useAetherStore";

// Color palettes per state
const STATE_COLORS: Record<EngineState, { core: string; glow: string; ring: string }> = {
    IDLE: { core: "#1a1a3e", glow: "#2d1b69", ring: "#4a3080" },
    LISTENING: { core: "#1a2a5e", glow: "#3b4bff", ring: "#6366f1" },
    THINKING: { core: "#3d2b1a", glow: "#f59e0b", ring: "#d97706" },
    SPEAKING: { core: "#0a2a3e", glow: "#06b6d4", ring: "#22d3ee" },
    INTERRUPTING: { core: "#4a1a1a", glow: "#ef4444", ring: "#f87171" },
};

interface Props {
    size?: number;
}

export default function AetherOrb({ size = 240 }: Props) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animRef = useRef<number>(0);
    const timeRef = useRef(0);

    const engineState = useAetherStore((s) => s.engineState);
    const status = useAetherStore((s) => s.status);
    const setStatus = useAetherStore((s) => s.setStatus);

    // Smoothed values for animation (avoid jitter)
    const smoothMic = useRef(0);
    const smoothSpeaker = useRef(0);

    const handleClick = useCallback(() => {
        if (status === "disconnected" || status === "error") {
            setStatus("connecting");
        } else if (status === "listening" || status === "speaking" || status === "connected") {
            setStatus("disconnected");
        }
    }, [status, setStatus]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d")!;
        const dpr = window.devicePixelRatio || 1;
        canvas.width = size * dpr;
        canvas.height = size * dpr;
        ctx.scale(dpr, dpr);

        const cx = size / 2;
        const cy = size / 2;
        const baseRadius = size * 0.28;

        const draw = () => {
            timeRef.current += 0.016; // ~60fps
            const t = timeRef.current;

            // Read transient values directly to avoid React re-render loops
            const currentMicLevel = useAetherStore.getState().micLevel;
            const currentSpeakerLevel = useAetherStore.getState().speakerLevel;

            // Smooth interpolation (exponential smoothing)
            smoothMic.current += (currentMicLevel - smoothMic.current) * 0.15;
            smoothSpeaker.current += (currentSpeakerLevel - smoothSpeaker.current) * 0.15;

            const colors = STATE_COLORS[engineState] || STATE_COLORS.IDLE;
            const energy = engineState === "SPEAKING"
                ? smoothSpeaker.current
                : smoothMic.current;

            ctx.clearRect(0, 0, size, size);

            // ── Outer glow rings ──
            const ringCount = 3;
            for (let i = ringCount; i >= 1; i--) {
                const ringPhase = t * (0.5 + i * 0.3) + i;
                const breathe = Math.sin(ringPhase) * 0.5 + 0.5;
                const energyBoost = energy * 30 * i;
                const r = baseRadius + i * 18 + breathe * 8 + energyBoost;
                const alpha = (0.06 - i * 0.015) + energy * 0.05;

                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, Math.PI * 2);
                ctx.strokeStyle = colors.ring;
                ctx.globalAlpha = Math.max(0, alpha);
                ctx.lineWidth = 1.5;
                ctx.stroke();
                ctx.globalAlpha = 1;
            }

            // ── Main orb body ──
            const breathe = Math.sin(t * 1.2) * 0.03 + 1;
            const energyPulse = energy * 0.15;
            const orbRadius = baseRadius * (breathe + energyPulse);

            // Radial gradient
            const grad = ctx.createRadialGradient(
                cx - orbRadius * 0.2, cy - orbRadius * 0.2, orbRadius * 0.1,
                cx, cy, orbRadius
            );
            grad.addColorStop(0, colors.glow + "cc");
            grad.addColorStop(0.5, colors.core + "ee");
            grad.addColorStop(1, colors.core + "40");

            ctx.beginPath();
            ctx.arc(cx, cy, orbRadius, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();

            // ── Inner glow ──
            const innerGlow = ctx.createRadialGradient(
                cx, cy, 0,
                cx, cy, orbRadius * 0.7
            );
            innerGlow.addColorStop(0, colors.glow + "60");
            innerGlow.addColorStop(1, "transparent");
            ctx.beginPath();
            ctx.arc(cx, cy, orbRadius * 0.7, 0, Math.PI * 2);
            ctx.fillStyle = innerGlow;
            ctx.fill();

            // ── Mic-energy ripples (LISTENING only) ──
            if (engineState === "LISTENING" && smoothMic.current > 0.02) {
                const rippleCount = 4;
                for (let i = 0; i < rippleCount; i++) {
                    const phase = (t * 2 + i * 1.5) % (Math.PI * 2);
                    const rippleRadius = orbRadius + Math.sin(phase) * 20 * smoothMic.current + i * 12;
                    const alpha = Math.max(0, 0.3 - i * 0.08) * smoothMic.current * 3;

                    ctx.beginPath();
                    ctx.arc(cx, cy, rippleRadius, 0, Math.PI * 2);
                    ctx.strokeStyle = colors.ring;
                    ctx.globalAlpha = Math.min(alpha, 0.5);
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    ctx.globalAlpha = 1;
                }
            }

            // ── Speaking pulse rings ──
            if (engineState === "SPEAKING" && smoothSpeaker.current > 0.02) {
                const pulseCount = 3;
                for (let i = 0; i < pulseCount; i++) {
                    const expand = ((t * 1.5 + i * 0.8) % 3) / 3; // 0→1 over 3s
                    const r = orbRadius + expand * 60 * smoothSpeaker.current;
                    const alpha = (1 - expand) * 0.3 * smoothSpeaker.current;

                    ctx.beginPath();
                    ctx.arc(cx, cy, r, 0, Math.PI * 2);
                    ctx.strokeStyle = colors.ring;
                    ctx.globalAlpha = Math.max(0, alpha);
                    ctx.lineWidth = 2.5 * (1 - expand);
                    ctx.stroke();
                    ctx.globalAlpha = 1;
                }
            }

            // ── Thinking swirl particles ──
            if (engineState === "THINKING") {
                const pCount = 12;
                for (let i = 0; i < pCount; i++) {
                    const angle = (t * 2 + i * (Math.PI * 2 / pCount)) % (Math.PI * 2);
                    const dist = orbRadius * 0.5 + Math.sin(t * 3 + i) * orbRadius * 0.2;
                    const px = cx + Math.cos(angle) * dist;
                    const py = cy + Math.sin(angle) * dist;
                    const pSize = 2 + Math.sin(t * 4 + i * 0.7) * 1;

                    ctx.beginPath();
                    ctx.arc(px, py, pSize, 0, Math.PI * 2);
                    ctx.fillStyle = colors.glow;
                    ctx.globalAlpha = 0.6 + Math.sin(t * 3 + i) * 0.3;
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
            }

            // ── Center dot (status light) ──
            ctx.beginPath();
            ctx.arc(cx, cy, 3, 0, Math.PI * 2);
            ctx.fillStyle = engineState === "IDLE" ? "#4a3080" : colors.glow;
            ctx.globalAlpha = 0.5 + Math.sin(t * 3) * 0.3;
            ctx.fill();
            ctx.globalAlpha = 1;

            animRef.current = requestAnimationFrame(draw);
        };

        draw();
        return () => cancelAnimationFrame(animRef.current);
    }, [size, engineState]);

    return (
        <canvas
            ref={canvasRef}
            onClick={handleClick}
            className="aether-orb"
            style={{
                width: size,
                height: size,
                cursor: "pointer",
            }}
            aria-label={`Aether Voice: ${engineState.toLowerCase()}. Click to ${status === "disconnected" ? "start" : "stop"}.`}
            role="button"
            tabIndex={0}
        />
    );
}
