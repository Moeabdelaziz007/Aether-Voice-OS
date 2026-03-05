"use client";

/**
 * ParticleField — Advanced Ambient Neural Background
 * 
 * Creates an immersive quantum neural topology visualization with:
 * - Floating particle nodes with pulse effects
 * - Dynamic connection lines that respond to system state
 * - Layered gradient depth effects
 * - Energy wave ripples
 * 
 * Color Palette: Quantum Neural Topology
 * - Neon Green (#39ff14) — Primary accent
 * - Dark Carbon (#0a0a0a) — Background
 * - Medium Gray (#6b7280) — Secondary
 */

import { useMemo, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

interface Particle {
    id: number;
    x: number;
    y: number;
    size: number;
    delay: number;
    duration: number;
    opacity: number;
    pulseSpeed: number;
    layer: number;
}

interface EnergyWave {
    id: string;
    x: number;
    y: number;
    startTime: number;
}

function generateParticles(count: number): Particle[] {
    return Array.from({ length: count }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: 1.5 + Math.random() * 3,
        delay: Math.random() * 6,
        duration: 15 + Math.random() * 20,
        opacity: 0.06 + Math.random() * 0.12,
        pulseSpeed: 2 + Math.random() * 3,
        layer: Math.floor(Math.random() * 3),
    }));
}

export default function ParticleField({ count = 50 }: { count?: number }) {
    const particles = useMemo(() => generateParticles(count), [count]);
    const engineState = useAetherStore((s) => s.engineState);
    const [energyWaves, setEnergyWaves] = useState<EnergyWave[]>([]);

    // Generate energy waves on state changes
    useEffect(() => {
        if (engineState === "SPEAKING" || engineState === "LISTENING") {
            const wave: EnergyWave = {
                id: `wave-${Date.now()}`,
                x: 50,
                y: 50,
                startTime: Date.now(),
            };
            setEnergyWaves(prev => [...prev.slice(-3), wave]);
        }
    }, [engineState]);

    // Clean up old waves
    useEffect(() => {
        const interval = setInterval(() => {
            const now = Date.now();
            setEnergyWaves(prev => prev.filter(w => now - w.startTime < 4000));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    // State-based intensity
    const intensity = useMemo(() => {
        switch (engineState) {
            case "SPEAKING": return 1.5;
            case "LISTENING": return 1.2;
            case "THINKING": return 1.3;
            case "INTERRUPTING": return 2.0;
            default: return 1.0;
        }
    }, [engineState]);

    return (
        <div
            className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
            aria-hidden="true"
        >
            {/* Energy Waves */}
            <AnimatePresence>
                {energyWaves.map((wave) => (
                    <motion.div
                        key={wave.id}
                        className="absolute rounded-full border"
                        style={{
                            left: `${wave.x}%`,
                            top: `${wave.y}%`,
                            transform: "translate(-50%, -50%)",
                            borderColor: `rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.3)`,
                        }}
                        initial={{ width: 0, height: 0, opacity: 0.6 }}
                        animate={{ 
                            width: "150vw", 
                            height: "150vw", 
                            opacity: 0,
                        }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 4, ease: "easeOut" }}
                    />
                ))}
            </AnimatePresence>

            {/* Background Layer Particles */}
            {particles.filter(p => p.layer === 0).map((p) => (
                <motion.div
                    key={`bg-${p.id}`}
                    className="absolute rounded-full blur-sm"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: p.size * 1.5,
                        height: p.size * 1.5,
                        backgroundColor: `rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * 0.5})`,
                    }}
                    animate={{
                        y: [0, -40 - Math.random() * 50, 0],
                        x: [0, 20 - Math.random() * 40, 0],
                        scale: [1, 1.2, 1],
                    }}
                    transition={{
                        duration: p.duration * 1.2,
                        delay: p.delay,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            ))}

            {/* Main Particles */}
            {particles.filter(p => p.layer === 1).map((p) => (
                <motion.div
                    key={p.id}
                    className="absolute rounded-full"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: p.size,
                        height: p.size,
                        backgroundColor: `rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * intensity})`,
                        boxShadow: `
                            0 0 ${p.size * 4}px rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * 0.6}),
                            0 0 ${p.size * 8}px rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * 0.3})
                        `,
                    }}
                    animate={{
                        y: [0, -30 - Math.random() * 40, 0],
                        x: [0, 15 - Math.random() * 30, 0],
                        opacity: [p.opacity * intensity, p.opacity * intensity * 1.8, p.opacity * intensity],
                        scale: [1, 1.1 + Math.random() * 0.2, 1],
                    }}
                    transition={{
                        duration: p.duration,
                        delay: p.delay,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            ))}

            {/* Foreground Highlight Particles */}
            {particles.filter(p => p.layer === 2).map((p) => (
                <motion.div
                    key={`fg-${p.id}`}
                    className="absolute rounded-full"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: p.size * 0.7,
                        height: p.size * 0.7,
                        backgroundColor: `rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * 1.5 * intensity})`,
                        boxShadow: `0 0 ${p.size * 6}px rgba(var(--accent-r), var(--accent-g), var(--accent-b), ${p.opacity * 0.8})`,
                    }}
                    animate={{
                        y: [0, -20 - Math.random() * 30, 0],
                        x: [0, 10 - Math.random() * 20, 0],
                        scale: [1, 1.3, 1],
                        opacity: [p.opacity * intensity, p.opacity * intensity * 2, p.opacity * intensity],
                    }}
                    transition={{
                        duration: p.duration * 0.8,
                        delay: p.delay,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            ))}

            {/* Dynamic Neural Connection Lines */}
            <svg
                className="absolute inset-0 w-full h-full"
                xmlns="http://www.w3.org/2000/svg"
                style={{ opacity: 0.04 * intensity }}
            >
                <defs>
                    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor={`rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.5)`} />
                        <stop offset="50%" stopColor={`rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.2)`} />
                        <stop offset="100%" stopColor={`rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.5)`} />
                    </linearGradient>
                </defs>
                
                {particles.slice(0, 20).map((p, i) => {
                    const connections = [
                        particles[(i + 2) % particles.length],
                        particles[(i + 5) % particles.length],
                    ];
                    return connections.map((next, j) => (
                        <line
                            key={`line-${p.id}-${j}`}
                            x1={`${p.x}%`}
                            y1={`${p.y}%`}
                            x2={`${next.x}%`}
                            y2={`${next.y}%`}
                            stroke="url(#lineGradient)"
                            strokeWidth="0.5"
                            strokeLinecap="round"
                        />
                    ));
                })}
            </svg>

            {/* Quantum Grid Overlay */}
            <div
                className="absolute inset-0 opacity-[0.015]"
                style={{
                    backgroundImage: `
                        linear-gradient(rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.1) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.1) 1px, transparent 1px)
                    `,
                    backgroundSize: '60px 60px',
                }}
            />

            {/* Radial Depth Gradient */}
            <div
                className="absolute inset-0"
                style={{
                    background: `
                        radial-gradient(ellipse 70% 60% at 50% 50%, transparent 0%, var(--void) 100%),
                        radial-gradient(ellipse 50% 40% at 25% 75%, rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.025) 0%, transparent 70%),
                        radial-gradient(ellipse 45% 35% at 75% 25%, rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.02) 0%, transparent 70%),
                        radial-gradient(ellipse 30% 20% at 50% 50%, rgba(var(--accent-r), var(--accent-g), var(--accent-b), 0.015) 0%, transparent 50%)
                    `,
                }}
            />

            {/* Top & Bottom Fade */}
            <div 
                className="absolute inset-x-0 top-0 h-32"
                style={{
                    background: 'linear-gradient(to bottom, var(--void) 0%, transparent 100%)',
                }}
            />
            <div 
                className="absolute inset-x-0 bottom-0 h-32"
                style={{
                    background: 'linear-gradient(to top, var(--void) 0%, transparent 100%)',
                }}
            />
        </div>
    );
}
