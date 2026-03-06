"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * SystemAnalytics — Left-aligned holographic diagnostics.
 * Visualizes AI "Neural Flux" and "Temporal Sync".
 */

const MiniChart = ({ label, value, color }: { label: string; value: number; color: string }) => {
    const bars = useMemo(() => Array.from({ length: 12 }, () => Math.random() * 100), []);

    return (
        <div className="flex flex-col gap-2 mb-6">
            <div className="flex justify-between items-end">
                <span className="text-[10px] uppercase tracking-widest text-white/40 font-mono">{label}</span>
                <span className="text-[10px] text-white/60 font-mono">{Math.round(value)}%</span>
            </div>
            <div className="flex items-end gap-[2px] h-8">
                {bars.map((h, i) => (
                    <motion.div
                        key={i}
                        animate={{ height: [`${h}%`, `${Math.random() * 100}%`, `${h}%`] }}
                        transition={{ duration: 2 + Math.random(), repeat: Infinity }}
                        style={{ backgroundColor: color }}
                        className="w-[3px] opacity-40 rounded-full"
                    />
                ))}
            </div>
        </div>
    );
};

export default function SystemAnalytics() {
    const [telemetry, setTelemetry] = React.useState({
        micLevel: 0,
        speakerLevel: 0,
        latencyMs: 0,
        pitch: 0,
        spectralCentroid: 0
    });

    const engineState = useAetherStore((s) => s.engineState);

    // Bypass React state for high-frequency telemetry using requestAnimationFrame
    React.useEffect(() => {
        let rafId: number;
        const update = () => {
            const state = useAetherStore.getState();
            setTelemetry({
                micLevel: state.micLevel,
                speakerLevel: state.speakerLevel,
                latencyMs: state.latencyMs,
                pitch: state.pitch,
                spectralCentroid: state.spectralCentroid
            });
            // We throttle UI updates to 10fps for diagnostics panel to save CPU
            setTimeout(() => {
                rafId = requestAnimationFrame(update);
            }, 100);
        };
        rafId = requestAnimationFrame(update);
        return () => cancelAnimationFrame(rafId);
    }, []);

    return (
        <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="absolute left-12 top-1/2 -translate-y-1/2 w-48 hidden lg:flex flex-col select-none pointer-events-none"
        >
            <div className="mb-8 pl-4 border-l border-white/10">
                <h3 className="text-[12px] uppercase tracking-[0.2em] text-white/20 mb-1 font-mono">Status</h3>
                <p className="text-[14px] text-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.8)] font-mono uppercase">
                    {engineState}
                </p>
            </div>

            <MiniChart
                label="Neural Flux"
                value={telemetry.micLevel * 100}
                color="rgba(var(--accent-r),var(--accent-g),var(--accent-b),1)"
            />

            <MiniChart
                label="Signal Integrity"
                value={Math.max(0, 100 - (telemetry.latencyMs / 20))}
                color="rgba(255,255,255,0.4)"
            />

            <div className="flex flex-col gap-1 mb-6 border-l border-white/5 pl-3">
                <div className="flex justify-between items-center text-[10px] font-mono">
                    <span className="text-white/20 uppercase">Pitch</span>
                    <span className="text-white/60">{Math.round(telemetry.pitch)} Hz</span>
                </div>
                <div className="flex justify-between items-center text-[10px] font-mono">
                    <span className="text-white/20 uppercase">Spectral</span>
                    <span className="text-white/60">{Math.round(telemetry.spectralCentroid)} Hz</span>
                </div>
            </div>

            <div className="mt-8 text-[9px] font-mono text-white/10 uppercase tracking-tighter leading-tight">
                AetherOS Node: 0x710<br />
                Latency: {telemetry.latencyMs.toFixed(1)}ms<br />
                Frequency: {(telemetry.pitch / 1000).toFixed(2)} kHz
            </div>
        </motion.div>
    );
}
