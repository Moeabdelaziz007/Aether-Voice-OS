"use client";

import React, { useEffect, useRef } from "react";
import { useAetherStore } from "@/store/useAetherStore";
import { useForgeStore } from "@/store/useForgeStore";

export default function NeuralBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const mouseRef = useRef({ x: 0, y: 0, active: false });
    
    // Neural Links to Store
    const micLevel = useAetherStore((s) => s.micLevel || 0);
    const speakerLevel = useAetherStore((s) => s.speakerLevel || 0);
    const voiceMode = useForgeStore((s) => s.voiceMode);
    
    // Combine audio for reactivity
    const totalAudio = Math.max(micLevel, speakerLevel);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationFrameId: number;
        let w: number, h: number;
        let particles: any[] = [];

        class Particle {
            x: number;
            y: number;
            vx: number;
            vy: number;
            size: number;
            baseSize: number;
            color: string;

            constructor(currentW: number, currentH: number) {
                this.x = Math.random() * currentW;
                this.y = Math.random() * currentH;
                this.vx = (Math.random() - 0.5) * 0.3;
                this.vy = (Math.random() - 0.5) * 0.3;
                this.baseSize = Math.random() * 1.2 + 0.3;
                this.size = this.baseSize;
                this.color = Math.random() > 0.95 ? "#22d3ee" : "#ffffff";
            }

            update(audio: number, currentW: number, currentH: number) {
                const speedMult = 1 + audio * 5;
                this.x += this.vx * speedMult;
                this.y += this.vy * speedMult;

                if (mouseRef.current.active) {
                    const dx = this.x - mouseRef.current.x;
                    const dy = this.y - mouseRef.current.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    const maxDist = 200;
                    if (dist < maxDist) {
                        const force = (maxDist - dist) / maxDist;
                        this.x += dx * force * 0.02;
                        this.y += dy * force * 0.02;
                        this.size = this.baseSize * (1 + force * 1.5 + audio * 3);
                    } else {
                        this.size = this.baseSize * (1 + audio * 2);
                    }
                } else {
                    this.size = this.baseSize * (1 + audio * 2);
                }

                if (this.x < 0) this.x = currentW;
                if (this.x > currentW) this.x = 0;
                if (this.y < 0) this.y = currentH;
                if (this.y > currentH) this.y = 0;
            }

            draw() {
                if (!ctx) return;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color === "#ffffff" ? `rgba(255,255,255,${0.1 + totalAudio * 0.4})` : `rgba(34,211,238,${0.3 + totalAudio})`;
                ctx.fill();
            }
        }

        const resize = () => {
            w = canvas.width = window.innerWidth * window.devicePixelRatio;
            h = canvas.height = window.innerHeight * window.devicePixelRatio;
            canvas.style.width = window.innerWidth + "px";
            canvas.style.height = window.innerHeight + "px";
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
            w = window.innerWidth;
            h = window.innerHeight;
            init();
        };

        const init = () => {
            particles = [];
            const count = Math.min(Math.floor((w * h) / 15000), 120);
            for (let i = 0; i < count; i++) {
                particles.push(new Particle(w, h));
            }
        };

        const handleMouseMove = (e: MouseEvent) => {
            mouseRef.current = { x: e.clientX, y: e.clientY, active: true };
        };

        const handleMouseLeave = () => {
            mouseRef.current.active = false;
        };

        window.addEventListener("resize", resize);
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseleave", handleMouseLeave);
        resize();

        const drawLoop = () => {
            ctx.clearRect(0, 0, w, h);
            const r = getComputedStyle(document.documentElement).getPropertyValue("--accent-r").trim() || "34";
            const g = getComputedStyle(document.documentElement).getPropertyValue("--accent-g").trim() || "211";
            const b = getComputedStyle(document.documentElement).getPropertyValue("--accent-b").trim() || "238";

            particles.forEach((p, i) => {
                p.update(totalAudio, w, h);
                p.draw();

                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const distSq = dx * dx + dy * dy;
                    const maxDist = 150;
                    if (distSq < maxDist * maxDist) {
                        const dist = Math.sqrt(distSq);
                        const alpha = (1 - dist / maxDist) * (0.05 + totalAudio * 0.3);
                        const isFiring = Math.random() > (0.9992 - totalAudio * 0.01);
                        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${isFiring ? alpha * 4 : alpha})`;
                        ctx.lineWidth = isFiring ? 1.5 : 0.4;
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            });
            animationFrameId = requestAnimationFrame(drawLoop);
        };

        drawLoop();

        return () => {
            window.removeEventListener("resize", resize);
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseleave", handleMouseLeave);
            cancelAnimationFrame(animationFrameId);
        };
    }, [totalAudio, voiceMode]);

    return (
        <canvas
            ref={canvasRef}
            className={`fixed inset-0 pointer-events-none z-0 transition-opacity duration-1000 ${
                voiceMode !== 'idle' ? 'opacity-80' : 'opacity-40'
            } mix-blend-screen`}
            style={{ filter: 'blur(0.5px)' }}
        />
    );
}
