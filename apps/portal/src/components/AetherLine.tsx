"use client";
/**
 * Aether Voice OS — AetherLine Reactive Visualizer.
 *
 * A single horizontal line that reacts to audio energy.
 * Now fully autonomous, pulling telemetry directly from the store,
 * and coloring itself based on the user's selected Persona AccentColor.
 */

import { useEffect, useRef, useCallback } from "react";
import { useAetherStore, ACCENT_COLORS } from "@/store/useAetherStore";

export default function AetherLine() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const rafRef = useRef<number>(0);
    const timeRef = useRef(0);

    // Smoothed levels for fluid animation
    const smoothMicRef = useRef(0);
    const smoothSpeakerRef = useRef(0);

    const draw = useCallback(() => {
        const state = useAetherStore.getState();
        const { micLevel, speakerLevel, status, engineState, preferences } = state;

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
        const centerY = H * 0.4;
        const time = timeRef.current;

        // Smooth the levels
        const smoothing = 0.12;
        smoothMicRef.current += (micLevel - smoothMicRef.current) * smoothing;
        smoothSpeakerRef.current += (speakerLevel - smoothSpeakerRef.current) * smoothing;

        const mic = smoothMicRef.current;
        const speaker = smoothSpeakerRef.current;

        // Determine who's active based on engine state & audio
        const isSpeaking = engineState === "SPEAKING" || speaker > 0.05;
        const isListening = engineState === "LISTENING" || mic > 0.02;
        const activeLevel = isSpeaking ? speaker : mic;
        const baseAmplitude = isSpeaking ? 60 : 35;
        const amplitude = Math.max(2, activeLevel * baseAmplitude * (H / 100));

        // Get Persona color
        const colorToken = ACCENT_COLORS[preferences.accentColor] || ACCENT_COLORS.cyan;
        const personaRgb = colorToken.rgb;

        // Apply colors
        let lineColor = `rgba(${personaRgb}, 0.15)`; // default dim
        let glowColor = "transparent";
        let lineWidth = 1.5;

        if (isSpeaking) {
            lineColor = colorToken.primary;
            glowColor = colorToken.glow;
            lineWidth = 2.5 + speaker * 3;
        } else if (isListening) {
            // slightly lighter/white for listening contrast
            lineColor = "#ffffff";
            glowColor = "rgba(255,255,255, 0.3)";
            lineWidth = 2 + mic * 2;
        } else {
            lineColor = `rgba(${personaRgb}, 0.2)`;
            glowColor = `rgba(${personaRgb}, 0.05)`;
            lineWidth = 1.5;
        }

        // Clear canvas
        ctx.clearRect(0, 0, W, H);

        // --- Main wave function ---
        const drawWave = (yBase: number, alpha: number, widthMul: number) => {
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.strokeStyle = lineColor;
            ctx.lineWidth = lineWidth * widthMul;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";

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
                const wave1 = Math.sin(progress * Math.PI * 3 + time * 3) * amplitude;
                const wave2 = Math.sin(progress * Math.PI * 5 + time * 2.1) * amplitude * 0.4;
                const wave3 = Math.sin(progress * Math.PI * 9 + time * 4.5) * amplitude * 0.15;

                // Edge fade
                const edgeFade =
                    Math.sin(progress * Math.PI) *
                    (1 - Math.pow(Math.abs(progress - 0.5) * 2, 4));

                const y = yBase + (wave1 + wave2 + wave3) * edgeFade;

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            ctx.restore();
        };

        // Draw multiple layers for depth
        drawWave(centerY, 0.15, 3);   // Wide soft glow
        drawWave(centerY, 0.5, 1.5);  // Mid glow
        drawWave(centerY, 1.0, 1);    // Main line

        // --- Mirror reflection ---
        const reflectY = centerY + amplitude + 30;
        ctx.save();
        ctx.globalAlpha = 0.08;
        ctx.transform(1, 0, 0, -0.4, 0, reflectY * 1.4);
        drawWave(reflectY, 0.3, 0.8);
        ctx.restore();

        // --- Particles (only when very active) ---
        if (activeLevel > 0.1) {
            const particleCount = Math.floor(activeLevel * 10);
            for (let i = 0; i < particleCount; i++) {
                const px = Math.random() * W;
                const py = centerY + (Math.random() - 0.5) * amplitude * 2.5;
                const size = Math.random() * 2 + 0.5;
                const opacity = Math.random() * 0.4 * activeLevel;

                ctx.beginPath();
                ctx.arc(px, py, size, 0, Math.PI * 2);
                ctx.fillStyle = isListening
                    ? `rgba(255, 255, 255, ${opacity})`
                    : `rgba(${personaRgb}, ${opacity})`;
                ctx.fill();
            }
        }

        timeRef.current += 0.012; // animation speed
        rafRef.current = requestAnimationFrame(draw);
    }, []);

    useEffect(() => {
        // Start animation loop
        rafRef.current = requestAnimationFrame(draw);
        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [draw]);

    return (
        <canvas
            ref={canvasRef}
            className="w-full h-full block"
            style={{ minHeight: "200px" }}
        />
    );
}
