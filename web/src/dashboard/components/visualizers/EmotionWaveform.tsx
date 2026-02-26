"use client";

import { useEffect, useRef } from "react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function EmotionWaveform({ className }: { className?: string }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationFrameId: number;
        let time = 0;

        // MVP: Simulate random emotional data for the demo fallback if no websocket
        const render = () => {
            time += 0.05;

            const width = canvas.width = canvas.clientWidth;
            const height = canvas.height = canvas.clientHeight;

            ctx.clearRect(0, 0, width, height);

            // Simulate base frustration vector
            const frustration = Math.sin(time * 0.5) * 0.5 + 0.5;

            // Cyberpunk gradient: Calm (Blue) to Frustrated (Red/Pink)
            const gradient = ctx.createLinearGradient(0, 0, width, 0);
            gradient.addColorStop(0, `rgba(0, 240, 255, ${1 - frustration})`);
            gradient.addColorStop(0.5, `rgba(157, 78, 221, 0.8)`);
            gradient.addColorStop(1, `rgba(255, 51, 51, ${frustration})`);

            ctx.beginPath();
            ctx.moveTo(0, height / 2);

            for (let i = 0; i < width; i++) {
                // High frequency jitter when frustrated
                const noise = (Math.random() - 0.5) * (frustration * 50);
                // Base sine wave
                const y = Math.sin(i * 0.02 + time) * 30 + height / 2 + noise;
                ctx.lineTo(i, y);
            }

            ctx.strokeStyle = gradient;
            ctx.lineWidth = 3;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.stroke();

            // Soft glow
            ctx.shadowBlur = 15;
            ctx.shadowColor = `rgba(255, 51, 51, ${frustration * 0.5})`;
            ctx.stroke();

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <div className={cn("glass-panel rounded-2xl p-6 relative overflow-hidden", className)}>
            <div className="absolute top-4 left-6 z-10">
                <h3 className="text-sm font-mono tracking-widest text-[#00f0ff] glow-text-blue uppercase">
                    Neural Resonance
                </h3>
                <p className="text-xs text-gray-400 font-mono mt-1">Live Frustration Matrix</p>
            </div>
            <canvas
                ref={canvasRef}
                className="w-full h-full min-h-[200px]"
                style={{ filter: "drop-shadow(0 0 10px rgba(0,240,255,0.2))" }}
            />
        </div>
    );
}
