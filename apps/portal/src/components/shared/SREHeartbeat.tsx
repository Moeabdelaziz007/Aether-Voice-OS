"use client";
 
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAetherStore } from '../../store/useAetherStore';
import { Activity, Signal, Zap, ShieldCheck, Clock, BarChart3 } from 'lucide-react';
 
interface Metrics {
    p50: number;
    p95: number;
    vad: number;
    frustration: number;
}
 
export default function SREHeartbeat() {
    const showTelemetry = useAetherStore((s) => s.showTelemetry);
    const setShowTelemetry = useAetherStore((s) => s.setShowTelemetry);
    const [metrics, setMetrics] = useState<Metrics>({
        p50: 320,
        p95: 450,
        vad: 0.8,
        frustration: 0.1
    });
 
    useEffect(() => {
        const interval = setInterval(() => {
            setMetrics(prev => ({
                p50: 250 + Math.random() * 100,
                p95: 400 + Math.random() * 150,
                vad: Math.random(),
                frustration: Math.min(1, Math.max(0, prev.frustration + (Math.random() - 0.5) * 0.1))
            }));
        }, 1500);
        return () => clearInterval(interval);
    }, []);
 
    return (
        <div className="fixed top-24 left-8 z-[100]">
            <button
                onClick={() => setShowTelemetry(!showTelemetry)}
                className="flex items-center gap-3 px-4 py-2 bg-carbon-950/40 backdrop-blur-xl border border-white/10 rounded-xl hover:bg-white/5 transition-all group overflow-hidden"
            >
                <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <BarChart3 className="w-4 h-4 text-neon-cyan" />
                <span className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] group-hover:text-white transition-colors">Neural HUD</span>
                <div className={`w-1.5 h-1.5 rounded-full ${metrics.p50 < 400 ? 'bg-neon-emerald' : 'bg-neon-pink'} animate-pulse shadow-[0_0_10px_currentcolor]`} />
            </button>
 
            <AnimatePresence>
                {showTelemetry && (
                    <motion.div
                        initial={{ opacity: 0, x: -20, scale: 0.95 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: -20, scale: 0.95 }}
                        className="absolute top-14 left-0 w-80 bg-carbon-950/80 backdrop-blur-[60px] border border-white/10 rounded-2xl p-6 shadow-2xl overflow-hidden"
                    >
                        {/* Matrix Header */}
                        <div className="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
                            <div className="flex items-center gap-3">
                                <Activity className="w-4 h-4 text-neon-purple" />
                                <span className="text-xs font-black text-white uppercase tracking-widest">SRE Telemetry</span>
                            </div>
                            <div className="px-2 py-0.5 bg-neon-purple/20 border border-neon-purple/30 rounded text-[8px] font-mono text-neon-purple uppercase">p95 Stable</div>
                        </div>
 
                        <div className="space-y-6">
                            {/* Latency Cluster */}
                            <div className="space-y-3">
                                <div className="flex justify-between text-[9px] font-mono text-white/30 uppercase tracking-widest">
                                    <span>Engine Latency</span>
                                    <Signal className="w-3 h-3" />
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <MetricCard label="p50" value={`${metrics.p50.toFixed(0)}ms`} color="text-neon-cyan" />
                                    <MetricCard label="p95" value={`${metrics.p95.toFixed(0)}ms`} color="text-neon-purple" />
                                </div>
                            </div>
 
                            {/* Resonance Cluster */}
                            <div className="space-y-3">
                                <div className="flex justify-between text-[9px] font-mono text-white/30 uppercase tracking-widest">
                                    <span>Signal Integrity</span>
                                    <Zap className="w-3 h-3" />
                                </div>
                                <HUDProgressBar label="VAD Energy" value={metrics.vad} color="bg-neon-cyan shadow-[0_0_10px_#00F3FF]" />
                                <HUDProgressBar label="Frustration Index" value={metrics.frustration} color="bg-neon-pink shadow-[0_0_10px_#FF1CF7]" />
                            </div>
 
                            {/* System Status */}
                            <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="w-4 h-4 text-neon-emerald" />
                                    <span className="text-[10px] font-black text-neon-emerald/80 uppercase tracking-widest">Consciousness Verified</span>
                                </div>
                                <span className="text-[10px] font-mono text-white/20">LIVE_MAPPING</span>
                            </div>
                        </div>
 
                        {/* Animated Grid Background */}
                        <div className="absolute inset-0 z-[-1] opacity-10">
                            <div className="w-full h-full bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:20px_20px]" />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
 
function MetricCard({ label, value, color }: { label: string, value: string, color: string }) {
    return (
        <div className="bg-white/5 rounded-xl p-3 border border-white/10 group hover:border-white/20 transition-colors">
            <div className="text-[8px] text-white/30 uppercase font-black mb-1">{label}</div>
            <div className={`text-sm font-black tracking-tight ${color}`}>{value}</div>
        </div>
    );
}
 
function HUDProgressBar({ label, value, color }: { label: string, value: number, color: string }) {
    return (
        <div className="space-y-1.5">
            <div className="flex justify-between text-[8px] font-black text-white/40 uppercase">
                <span>{label}</span>
                <span>{(value * 100).toFixed(0)}%</span>
            </div>
            <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <motion.div
                    initial={false}
                    animate={{ width: `${value * 100}%` }}
                    className={`h-full ${color}`}
                />
            </div>
        </div>
    );
}
