"use client";

/**
 * NeuralRealm — Diagnostics HUD.
 * Orb at 80px top-center, 4 telemetry panels in 2x2 grid below.
 * Wired to live Zustand store telemetry data.
 */

import { useMemo } from "react";
import { motion } from "framer-motion";
import GlassPanel from "@/components/shared/GlassPanel";
import { useAetherStore } from "@/store/useAetherStore";

function SparkLine() {
    const bars = useMemo(
        () => Array.from({ length: 20 }, () => 10 + Math.random() * 90),
        []
    );

    return (
        <div className="flex items-end gap-[2px] h-8 mt-2">
            {bars.map((h, i) => (
                <motion.div
                    key={i}
                    animate={{
                        height: [`${h}%`, `${10 + Math.random() * 90}%`, `${h}%`],
                    }}
                    transition={{
                        duration: 1.5 + Math.random() * 1,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                    className="w-[3px] bg-cyan-400/40 rounded-full"
                />
            ))}
        </div>
    );
}

function WaveformBar() {
    const segments = useMemo(
        () => Array.from({ length: 32 }, () => 0.2 + Math.random() * 0.8),
        []
    );

    return (
        <div className="flex items-center gap-[1px] h-6 mt-2">
            {segments.map((h, i) => (
                <motion.div
                    key={i}
                    animate={{
                        scaleY: [h, 0.2 + Math.random() * 0.8, h],
                    }}
                    transition={{
                        duration: 0.8 + Math.random() * 0.6,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                    className="w-[2px] h-full bg-purple-400/50 rounded-full origin-center"
                />
            ))}
        </div>
    );
}

function ProgressBar({ value, max }: { value: number; max: number }) {
    const pct = Math.min((value / max) * 100, 100);

    return (
        <div className="w-full h-1.5 bg-white/5 rounded-full mt-3 overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-cyan-400/60 to-cyan-400/30 rounded-full"
            />
        </div>
    );
}

interface TelemetryCardProps {
    title: string;
    index: number;
    children: React.ReactNode;
}

function TelemetryCard({ title, index, children }: TelemetryCardProps) {
    return (
        <GlassPanel
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
                delay: 0.15 + index * 0.1,
                duration: 0.5,
                ease: [0.16, 1, 0.3, 1],
            }}
        >
            <span className="text-white/30 text-[10px] uppercase tracking-[0.15em] font-mono">
                {title}
            </span>
            {children}
        </GlassPanel>
    );
}

// Map valence score to emotion display
function getEmotionState(valence: number, frustration: number): { label: string; icon: string } {
    if (frustration > 0.6) return { label: "Frustrated", icon: "😤" };
    if (valence > 0.7) return { label: "Positive", icon: "😊" };
    if (valence > 0.4) return { label: "Focused", icon: "🎯" };
    if (valence > 0.2) return { label: "Neutral", icon: "😐" };
    return { label: "Concerned", icon: "🤔" };
}

export default function NeuralRealm() {
    // ── Live store bindings ──
    const latencyMs = useAetherStore((s) => s.latencyMs);
    const neuralEvents = useAetherStore((s) => s.neuralEvents);
    const valence = useAetherStore((s) => s.valence);
    const frustration = useAetherStore((s) => s.frustrationScore);
    const transcript = useAetherStore((s) => s.transcript);
    const activeSoul = useAetherStore((s) => s.activeSoul);
    const toolCallHistory = useAetherStore((s) => s.toolCallHistory);

    // Derived values
    const emotion = useMemo(() => getEmotionState(valence, frustration), [valence, frustration]);
    const estimatedTokens = useMemo(() => transcript.reduce((acc, m) => acc + (m.content?.length || 0) * 0.75, 0), [transcript]);
    const displayLatency = latencyMs > 0 ? latencyMs : 0;

    return (
        <div className="w-full h-full flex flex-col items-center pt-[18%] px-6">
            {/* Section Title + Model Badge */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="flex items-center gap-3 mb-6"
            >
                <h2 className="text-white/30 text-xs uppercase tracking-[0.2em] font-mono">
                    Neural Diagnostics
                </h2>
                <span className="font-mono text-[9px] tracking-widest text-cyan-400/40 bg-cyan-400/[0.05] px-2 py-0.5 rounded-full border border-cyan-400/10">
                    Gemini 2.0 Flash
                </span>
                {activeSoul && (
                    <span className="font-mono text-[9px] tracking-widest text-emerald-400/60 bg-emerald-400/[0.06] px-2 py-0.5 rounded-full border border-emerald-400/10">
                        {activeSoul}
                    </span>
                )}
            </motion.div>

            {/* 2x2 Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl pb-24">
                {/* Latency */}
                <TelemetryCard title="Latency" index={0}>
                    <div className="flex items-baseline gap-1 mt-2">
                        <span className="text-3xl font-mono font-bold text-cyan-400">
                            {displayLatency}
                        </span>
                        <span className="text-white/30 text-xs font-mono">ms</span>
                    </div>
                    <p className="text-white/20 text-[10px] font-mono mt-1">
                        avg round-trip to Gemini Live
                    </p>
                </TelemetryCard>

                {/* Neural Events */}
                <TelemetryCard title="Neural Events" index={1}>
                    <div className="flex items-baseline gap-1 mt-2">
                        <span className="text-3xl font-mono font-bold text-white/90">
                            {neuralEvents.length.toLocaleString()}
                        </span>
                        {toolCallHistory.length > 0 && (
                            <span className="text-white/30 text-xs font-mono ml-2">
                                {toolCallHistory.length} tools
                            </span>
                        )}
                    </div>
                    <SparkLine />
                </TelemetryCard>

                {/* Emotion State */}
                <TelemetryCard title="Emotion State" index={2}>
                    <div className="flex items-baseline gap-2 mt-2">
                        <span className="text-xl font-semibold text-white/90">
                            {emotion.label}
                        </span>
                        <span className="text-xl">{emotion.icon}</span>
                    </div>
                    <WaveformBar />
                </TelemetryCard>

                {/* Session Tokens */}
                <TelemetryCard title="Session Tokens" index={3}>
                    <div className="flex items-baseline gap-1 mt-2">
                        <span className="text-2xl font-mono font-bold text-white/90">
                            {Math.round(estimatedTokens).toLocaleString()}
                        </span>
                        <span className="text-white/30 text-xs font-mono">
                            / 1000K
                        </span>
                    </div>
                    <ProgressBar value={estimatedTokens} max={1000000} />
                </TelemetryCard>
            </div>

            {/* Scan-line overlay */}
            <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden opacity-[0.03]">
                <motion.div
                    animate={{ backgroundPositionY: ["0px", "200px"] }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                    className="w-full h-full"
                    style={{
                        backgroundImage:
                            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255,255,255,0.5) 3px, rgba(255,255,255,0.5) 4px)",
                        backgroundSize: "100% 4px",
                    }}
                />
            </div>
        </div>
    );
}
