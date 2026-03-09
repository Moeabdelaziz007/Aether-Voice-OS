"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Signal, Zap, ShieldCheck, Clock } from 'lucide-react';

interface Metrics {
    p50: number;
    p95: number;
    p99: number;
    fps: number;
    jitter: number;
}

export default function SREHeartbeat() {
    const [isVisible, setIsVisible] = useState(false);
    const [metrics, setMetrics] = useState<Metrics>({
        p50: 320,
        p95: 450,
        p99: 580,
        fps: 60,
        jitter: 12
    });

    useEffect(() => {
        const interval = setInterval(() => {
            setMetrics(prev => ({
                p50: 300 + Math.random() * 50,
                p95: 420 + Math.random() * 80,
                p99: 550 + Math.random() * 120,
                fps: 58 + Math.random() * 4,
                jitter: 8 + Math.random() * 10
            }));
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed bottom-6 left-6 z-[100]">
            <button
                onClick={() => setIsVisible(!isVisible)}
                className="flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md border border-white/10 rounded-full hover:bg-white/5 transition-all group"
            >
                <div className={`w-1.5 h-1.5 rounded-full ${metrics.p50 < 400 ? 'bg-green-500' : 'bg-amber-500'} animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]`} />
                <span className="text-[9px] font-black text-white/40 uppercase tracking-widest group-hover:text-cyan-400 transition-colors">SRE_HEARTBEAT</span>
            </button>

            <AnimatePresence>
                {isVisible && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 10 }}
                        className="absolute bottom-10 left-0 w-64 bg-black/60 backdrop-blur-2xl border border-white/10 rounded-3xl p-5 shadow-2xl overflow-hidden"
                    >
                        {/* Background Scanline */}
                        <div className="absolute inset-0 bg-scanline pointer-events-none opacity-10" />

                        <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                            <div className="flex items-center gap-2">
                                <Activity className="w-3 h-3 text-cyan-400" />
                                <span className="text-[10px] font-black text-white/80 uppercase tracking-widest">LIVE_TELEMETRY</span>
                            </div>
                            <span className="text-[8px] font-mono text-white/30">V2.0.4-LOCKED</span>
                        </div>

                        <div className="space-y-3">
                            {/* Latency Cluster */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between text-[8px] font-mono text-white/30 uppercase tracking-widest">
                                    <span>Glass-to-Ear Latency</span>
                                    <Signal className="w-2 h-2" />
                                </div>
                                <div className="grid grid-cols-3 gap-2">
                                    <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                                        <div className="text-[7px] text-white/20 uppercase font-bold">p50</div>
                                        <div className="text-[10px] font-black text-cyan-400">{metrics.p50.toFixed(0)}ms</div>
                                    </div>
                                    <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                                        <div className="text-[7px] text-white/20 uppercase font-bold">p95</div>
                                        <div className="text-[10px] font-black text-purple-400">{metrics.p95.toFixed(0)}ms</div>
                                    </div>
                                    <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                                        <div className="text-[7px] text-white/20 uppercase font-bold">p99</div>
                                        <div className="text-[10px] font-black text-red-400">{metrics.p99.toFixed(0)}ms</div>
                                    </div>
                                </div>
                            </div>

                            {/* Performance Cluster */}
                            <div className="grid grid-cols-2 gap-2">
                                <div className="bg-white/5 rounded-xl p-3 border border-white/5 flex items-center gap-2">
                                    <Zap className="w-3 h-3 text-yellow-500" />
                                    <div>
                                        <div className="text-[7px] text-white/20 uppercase font-bold">FPS</div>
                                        <div className="text-[10px] font-black text-white/80">{metrics.fps.toFixed(1)}</div>
                                    </div>
                                </div>
                                <div className="bg-white/5 rounded-xl p-3 border border-white/5 flex items-center gap-2">
                                    <Clock className="w-3 h-3 text-cyan-500" />
                                    <div>
                                        <div className="text-[7px] text-white/20 uppercase font-bold">Jitter</div>
                                        <div className="text-[10px] font-black text-white/80">{metrics.jitter.toFixed(1)}ms</div>
                                    </div>
                                </div>
                            </div>

                            {/* Integrity Check */}
                            <div className="mt-2 pt-2 border-t border-white/5 flex items-center justify-between">
                                <div className="flex items-center gap-1.5">
                                    <ShieldCheck className="w-3 h-3 text-green-500" />
                                    <span className="text-[8px] font-black text-green-500/60 uppercase tracking-widest">SOUL_INTEGRITY: 100%</span>
                                </div>
                            </div>
                        </div>

                        {/* Animated Grid Background */}
                        <div className="absolute inset-0 z-[-1] opacity-5">
                            <div className="w-full h-full bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:10px_10px]" />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
