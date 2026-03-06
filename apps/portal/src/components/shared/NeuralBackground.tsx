"use client";

import React, { useEffect, useRef } from "react";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * NeuralBackground — High-performance Canvas-based ambient animation.
 * Creates a "Neural Network" / "Data Stream" effect that reacts to the accent color.
 */
export default function NeuralBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const engineState = useAetherStore((s) => s.engineState);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationFrameId: number;
        let w: number, h: number;
        let particles: any[] = [];

        const resize = () => {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        };

        window.addEventListener("resize", resize);
        resize();

        class Particle {
            x: number;
            y: number;
            vx: number;
            vy: number;
            size: number;

            constructor() {
                this.x = Math.random() * w;
                this.y = Math.random() * h;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.size = Math.random() * 2;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0 || this.x > w) this.vx *= -1;
                if (this.y < 0 || this.y > h) this.vy *= -1;
            }

            draw() {
                if (!ctx) return;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const init = () => {
            particles = [];
            for (let i = 0; i < 100; i++) {
                particles.push(new Particle());
            }
        };

        const draw = () => {
            ctx.clearRect(0, 0, w, h);

            // Get current accent color from CSS variables
            const r = getComputedStyle(document.documentElement).getPropertyValue("--accent-r").trim() || "0";
            const g = getComputedStyle(document.documentElement).getPropertyValue("--accent-g").trim() || "243";
            const b = getComputedStyle(document.documentElement).getPropertyValue("--accent-b").trim() || "255";

            ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.2)`;
            ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.05)`;

            particles.forEach((p, i) => {
                p.update();
                p.draw();

                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            });

            animationFrameId = requestAnimationFrame(draw);
        };

        init();
        draw();

        return () => {
            window.removeEventListener("resize", resize);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 pointer-events-none z-0 opacity-40 mix-blend-screen"
        />
    );
}
