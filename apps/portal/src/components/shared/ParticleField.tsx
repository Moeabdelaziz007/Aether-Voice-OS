"use client";

/**
 * ParticleField — Ambient floating particles background.
 * Quantum Topology theme: particles drift and connect like neural nodes.
 * Uses pure CSS animations for zero-JS overhead.
 */

import { useMemo } from "react";
import { motion } from "framer-motion";

interface Particle {
    id: number;
    x: number;
    y: number;
    size: number;
    delay: number;
    duration: number;
    opacity: number;
}

function generateParticles(count: number): Particle[] {
    return Array.from({ length: count }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: 1 + Math.random() * 2.5,
        delay: Math.random() * 5,
        duration: 12 + Math.random() * 18,
        opacity: 0.08 + Math.random() * 0.15,
    }));
}

export default function ParticleField({ count = 40 }: { count?: number }) {
    const particles = useMemo(() => generateParticles(count), [count]);

    return (
        <div
            className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
            aria-hidden="true"
        >
            {/* Particles */}
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    className="absolute rounded-full"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: p.size,
                        height: p.size,
                        backgroundColor: `rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity})`,
                        boxShadow: `0 0 ${p.size * 3}px rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * 0.5})`,
                    }}
                    animate={{
                        y: [0, -30 - Math.random() * 40, 0],
                        x: [0, 15 - Math.random() * 30, 0],
                        opacity: [p.opacity, p.opacity * 1.8, p.opacity],
                    }}
                    transition={{
                        duration: p.duration,
                        delay: p.delay,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            ))}

            {/* Subtle connection lines — static SVG web */}
            <svg
                className="absolute inset-0 w-full h-full opacity-[0.03]"
                xmlns="http://www.w3.org/2000/svg"
            >
                {particles.slice(0, 15).map((p, i) => {
                    const next = particles[(i + 3) % particles.length];
                    return (
                        <line
                            key={`line-${p.id}`}
                            x1={`${p.x}%`}
                            y1={`${p.y}%`}
                            x2={`${next.x}%`}
                            y2={`${next.y}%`}
                            stroke={`rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.3)`}
                            strokeWidth="0.5"
                        />
                    );
                })}
            </svg>

            {/* Radial gradient overlay — depth effect */}
            <div
                className="absolute inset-0"
                style={{
                    background: `
                        radial-gradient(ellipse 60% 50% at 50% 50%, transparent 0%, var(--void) 100%),
                        radial-gradient(ellipse 40% 30% at 30% 70%, rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.02) 0%, transparent 70%),
                        radial-gradient(ellipse 35% 25% at 70% 30%, rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.015) 0%, transparent 70%)
                    `,
                }}
            />
        </div>
    );
}
