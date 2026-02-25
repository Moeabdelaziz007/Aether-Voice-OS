"use client";
/**
 * Aether Voice OS — AetherLine Reactive Visualizer.
 *
 * A single horizontal neon line that reacts to audio energy:
 *   - Flat thin line when idle
 *   - Cyan (#00f3ff) sine wave when user speaks
 *   - Purple (#bc13fe) sine wave when AI speaks
 *   - Smooth transitions between states
 *   - Mirror reflection + neon glow effects
 *
 * The signature visual of Aether OS — inspired by Wispr Flow
 * but with Cyberpunk aesthetics.
 */

import { useEffect, useRef, useCallback } from "react";

interface AetherLineProps {
    micLevel: number;       // 0.0 – 1.0
    speakerLevel: number;   // 0.0 – 1.0
    status: "idle" | "listening" | "speaking" | "connecting" | "error";
}

// Colors
const CYAN = "#00f3ff";
const PURPLE = "#bc13fe";
const DIM_CYAN = "rgba(0, 243, 255, 0.3)";
const IDLE_COLOR = "rgba(0, 243, 255, 0.15)";

export default function AetherLine({ micLevel, speakerLevel, status }: AetherLineProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const rafRef = useRef<number>(0);
    const timeRef = useRef(0);

    // Smoothed levels for fluid animation
    const smoothMicRef = useRef(0);
    const smoothSpeakerRef = useRef(0);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Handle HiDPI
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const W = rect.width;
        const H = rect.height;
        const centerY = H * 0.4; // Line sits slightly above center for reflection space
        const time = timeRef.current;

        // Smooth the levels (exponential moving average)
        const smoothing = 0.12;
        smoothMicRef.current += (micLevel - smoothMicRef.current) * smoothing;
        smoothSpeakerRef.current += (speakerLevel - smoothSpeakerRef.current) * smoothing;

        const mic = smoothMicRef.current;
        const speaker = smoothSpeakerRef.current;

        // Determine who's active
        const isSpeaking = status === "speaking" || speaker > 0.05;
        const isListening = status === "listening" || mic > 0.02;
        const activeLevel = isSpeaking ? speaker : mic;
        const baseAmplitude = isSpeaking ? 40 : 25;
        const amplitude = Math.max(2, activeLevel * baseAmplitude * H / 100);

        // Color selection with smooth transition
        let lineColor = IDLE_COLOR;
        let glowColor = "transparent";
        let lineWidth = 1.5;

        if (isSpeaking) {
            lineColor = PURPLE;
            glowColor = "rgba(188, 19, 254, 0.4)";
            lineWidth = 2.5 + speaker * 2;
        } else if (isListening) {
            lineColor = CYAN;
            glowColor = "rgba(0, 243, 255, 0.3)";
            lineWidth = 2 + mic * 2;
        } else {
            lineColor = DIM_CYAN;
            glowColor = "rgba(0, 243, 255, 0.05)";
            lineWidth = 1.5;
        }

        // Clear
        ctx.clearRect(0, 0, W, H);

        // Background gradient (subtle)
        const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
        bgGrad.addColorStop(0, "rgba(0, 0, 0, 0)");
        bgGrad.addColorStop(0.5, "rgba(0, 0, 0, 0.02)");
        bgGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, W, H);

        // --- Main wave line ---
        const drawWave = (yBase: number, alpha: number, widthMul: number) => {
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.strokeStyle = lineColor;
            ctx.lineWidth = lineWidth * widthMul;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";

            // Glow effect
            if (activeLevel > 0.02) {
                ctx.shadowColor = glowColor;
                ctx.shadowBlur = 15 + activeLevel * 25;
            }

            ctx.beginPath();

            const segments = Math.max(200, W);
            const step = W / segments;

            for (let i = 0; i <= segments; i++) {
                const x = i * step;
                const progress = x / W;

                // Multi-frequency wave for organic feel
                const wave1 = Math.sin(progress * Math.PI * 4 + time * 3) * amplitude;
                const wave2 = Math.sin(progress * Math.PI * 7 + time * 2.3) * amplitude * 0.3;
                const wave3 = Math.sin(progress * Math.PI * 11 + time * 4.1) * amplitude * 0.15;

                // Edge fade: taper amplitude near edges
                const edgeFade =
                    Math.sin(progress * Math.PI) * // basic taper
                    (1 - Math.pow(Math.abs(progress - 0.5) * 2, 4)); // sharper falloff

                const y = yBase + (wave1 + wave2 + wave3) * edgeFade;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }

            ctx.stroke();
            ctx.restore();
        };

        // Draw multiple layers for depth
        drawWave(centerY, 0.15, 3);   // Wide soft glow
        drawWave(centerY, 0.4, 1.5);  // Mid glow
        drawWave(centerY, 1.0, 1);    // Main line

        // --- Mirror reflection ---
        const reflectY = centerY + amplitude + 20;
        ctx.save();
        ctx.globalAlpha = 0.12;
        ctx.transform(1, 0, 0, -0.4, 0, reflectY * 1.4 + reflectY * 0.4);
        drawWave(reflectY, 0.3, 0.8);
        ctx.restore();

        // --- Subtle particles (only when active) ---
        if (activeLevel > 0.05) {
            const particleCount = Math.floor(activeLevel * 12);
            for (let i = 0; i < particleCount; i++) {
                const px = Math.random() * W;
                const py = centerY + (Math.random() - 0.5) * amplitude * 2;
                const size = Math.random() * 2 + 0.5;
                const opacity = Math.random() * 0.5 * activeLevel;

                ctx.beginPath();
                ctx.arc(px, py, size, 0, Math.PI * 2);
                ctx.fillStyle = isSpeaking
                    ? `rgba(188, 19, 254, ${opacity})`
                    : `rgba(0, 243, 255, ${opacity})`;
                ctx.fill();
            }
        }

        // --- Status indicator dot ---
        if (status === "connecting") {
            const pulse = Math.sin(time * 5) * 0.3 + 0.7;
            ctx.beginPath();
            ctx.arc(W / 2, H - 15, 4, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 200, 0, ${pulse})`;
            ctx.fill();
        }

        // Advance time
        timeRef.current += 0.016; // ~60fps
        rafRef.current = requestAnimationFrame(draw);
    }, [micLevel, speakerLevel, status]);

    useEffect(() => {
        rafRef.current = requestAnimationFrame(draw);
        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [draw]);

    return (
        <canvas
            ref={canvasRef}
            style={{
                width: "100%",
                height: "100%",
                display: "block",
            }}
        />
    );
}
