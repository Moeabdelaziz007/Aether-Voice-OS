"use client";

import React, { useEffect, useRef, useCallback } from "react";

interface LiveWaveLineProps {
    analyzing: boolean;
    audioData?: number[];
}

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    life: number;
    maxLife: number;
    size: number;
    hue: number;
}

export const LiveWaveLine: React.FC<LiveWaveLineProps> = ({ analyzing, audioData }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const particlesRef = useRef<Particle[]>([]);
    const prevDataRef = useRef<number[]>([]);
    const timeRef = useRef(0);
    const frameRef = useRef(0);

    const spawnParticles = useCallback((x: number, y: number, intensity: number) => {
        const count = Math.floor(intensity / 40);
        for (let i = 0; i < count; i++) {
            particlesRef.current.push({
                x,
                y,
                vx: (Math.random() - 0.5) * 3,
                vy: (Math.random() - 0.5) * 4 - 1,
                life: 1,
                maxLife: 30 + Math.random() * 30,
                size: 1 + Math.random() * 2,
                hue: 185 + Math.random() * 30, // Cyan-range
            });
        }
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // High-DPI canvas
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        const width = rect.width;
        const height = rect.height;
        const centerY = height / 2;

        let animId: number;

        const draw = () => {
            timeRef.current += 0.02;
            frameRef.current++;
            const t = timeRef.current;

            // Fade trail
            ctx.fillStyle = "rgba(0, 0, 0, 0.15)";
            ctx.fillRect(0, 0, width, height);

            // ─── Layer 1: Deep ambient wave (slow, purple) ───
            ctx.beginPath();
            ctx.strokeStyle = "rgba(188, 19, 254, 0.15)";
            ctx.lineWidth = 3;
            for (let x = 0; x < width; x++) {
                const y = centerY + Math.sin(x * 0.008 + t * 0.3) * 25 + Math.sin(x * 0.02 + t * 0.7) * 8;
                x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            }
            ctx.stroke();

            // ─── Layer 2: Mid-frequency accent (medium speed, teal) ───
            ctx.beginPath();
            ctx.strokeStyle = "rgba(0, 243, 255, 0.2)";
            ctx.lineWidth = 1.5;
            for (let x = 0; x < width; x++) {
                const y = centerY + Math.sin(x * 0.015 + t * 1.2) * 15 + Math.cos(x * 0.04 + t * 0.9) * 6;
                x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            }
            ctx.stroke();

            // ─── Layer 3: Primary data-driven wave ───
            if (audioData && audioData.length > 0) {
                const sliceWidth = width / audioData.length;
                const prev = prevDataRef.current;

                // Main wave (cyan)
                ctx.beginPath();
                ctx.strokeStyle = "#00f3ff";
                ctx.lineWidth = 2.5;
                ctx.shadowColor = "#00f3ff";
                ctx.shadowBlur = 15;

                for (let i = 0; i < audioData.length; i++) {
                    const x = i * sliceWidth;
                    const amplitude = (audioData[i] / 255.0) * (height / 2.2);
                    const y = centerY - amplitude;
                    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);

                    // Spawn particles on transients
                    const prevAmp = prev[i] || 0;
                    const delta = Math.abs(audioData[i] - prevAmp);
                    if (delta > 30 && frameRef.current % 2 === 0) {
                        spawnParticles(x, y, delta);
                    }
                }
                ctx.stroke();
                ctx.shadowBlur = 0;

                // Mirror reflection wave (purple, inverted)
                ctx.beginPath();
                ctx.strokeStyle = "rgba(188, 19, 254, 0.35)";
                ctx.lineWidth = 1.5;
                ctx.shadowColor = "#bc13fe";
                ctx.shadowBlur = 8;

                for (let i = 0; i < audioData.length; i++) {
                    const x = i * sliceWidth;
                    const amplitude = (audioData[i] / 255.0) * (height / 3.5);
                    const y = centerY + amplitude;
                    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
                }
                ctx.stroke();
                ctx.shadowBlur = 0;

                prevDataRef.current = [...audioData];

            } else if (analyzing) {
                // Idle breathing wave
                ctx.beginPath();
                ctx.strokeStyle = "#00f3ff";
                ctx.lineWidth = 2;
                ctx.shadowColor = "#00f3ff";
                ctx.shadowBlur = 10;

                for (let x = 0; x < width; x++) {
                    const y = centerY
                        + Math.sin(x * 0.03 + t * 2) * 8 * Math.sin(t * 0.5)
                        + Math.sin(x * 0.07 + t * 3) * 3;
                    x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
                }
                ctx.stroke();
                ctx.shadowBlur = 0;

            } else {
                // Flat dormant line with subtle pulse
                const pulse = Math.sin(t * 1.5) * 0.3 + 0.7;
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 243, 255, ${pulse * 0.3})`;
                ctx.lineWidth = 1;
                ctx.moveTo(width * 0.1, centerY);
                ctx.lineTo(width * 0.9, centerY);
                ctx.stroke();
            }

            // ─── Particle System ───
            const particles = particlesRef.current;
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.02; // Gravity
                p.life -= 1 / p.maxLife;

                if (p.life <= 0) {
                    particles.splice(i, 1);
                    continue;
                }

                const alpha = p.life * 0.8;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, 100%, 70%, ${alpha})`;
                ctx.shadowColor = `hsla(${p.hue}, 100%, 60%, 0.5)`;
                ctx.shadowBlur = 6;
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            // Keep particle count manageable
            if (particles.length > 200) {
                particles.splice(0, particles.length - 200);
            }

            // ─── Scan Line Effect ───
            const scanY = (t * 80) % height;
            ctx.fillStyle = "rgba(0, 243, 255, 0.03)";
            ctx.fillRect(0, scanY, width, 2);

            animId = requestAnimationFrame(draw);
        };

        draw();
        return () => cancelAnimationFrame(animId);
    }, [audioData, analyzing, spawnParticles]);

    return (
        <div className="relative w-full h-40 flex items-center justify-center overflow-hidden rounded-lg">
            <canvas
                ref={canvasRef}
                style={{ width: "100%", height: "100%" }}
                className="w-full h-full"
            />
            {/* Top/Bottom edge glow */}
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-black/80 via-transparent to-black/80" />
            {/* Side fades */}
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-r from-black via-transparent to-black" />
        </div>
    );
};
