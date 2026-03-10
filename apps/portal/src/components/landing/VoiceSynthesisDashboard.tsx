'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Activity, Sliders, Volume2 } from 'lucide-react';

export default function VoiceSynthesisDashboard() {
    const [params, setParams] = useState({
        tone: 65,
        resonance: 40,
        style: 80,
        pitch: 50
    });

    return (
        <section className="w-full max-w-7xl mx-auto px-10 py-24 bg-black/20 rounded-[3rem] border border-white/5 backdrop-blur-md overflow-hidden relative">
            {/* Background Decorative Grid */}
            <div className="absolute inset-0 opacity-10 pointer-events-none"
                style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '40px 40px' }} />

            <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                <div className="space-y-8">
                    <div>
                        <h2 className="text-[10px] font-black uppercase tracking-[0.4em] text-purple-500/60 mb-2">Audio Engineering</h2>
                        <h3 className="text-4xl font-black text-white italic uppercase tracking-tighter">Voice Synthesis</h3>
                    </div>

                    <div className="space-y-6">
                        {Object.entries(params).map(([key, value]) => (
                            <div key={key} className="space-y-3">
                                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                    <span className="text-white/40">{key}</span>
                                    <span className="text-cyan-400">{value}%</span>
                                </div>
                                <div className="h-1 bg-white/5 rounded-full overflow-hidden relative">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-purple-500 to-cyan-400"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${value}%` }}
                                    />
                                    <input
                                        type="range"
                                        min="0" max="100"
                                        value={value}
                                        onChange={(e) => setParams(prev => ({ ...prev, [key]: parseInt(e.target.value) }))}
                                        className="absolute inset-0 opacity-0 cursor-pointer"
                                    />
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="p-4 bg-black/40 border border-white/5 rounded-2xl flex items-center justify-between group">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                                <Activity className="w-5 h-5 text-purple-400 group-hover:rotate-12 transition-transform" />
                            </div>
                            <div className="space-y-0.5">
                                <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Processing Logic</p>
                                <p className="text-xs font-mono text-cyan-300">Hyper-realistic Output...</p>
                            </div>
                        </div>
                        <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="w-12 h-12 rounded-full bg-cyan-500 shadow-[0_0_20px_rgba(34,211,238,0.4)] flex items-center justify-center text-black"
                        >
                            <Play className="fill-current w-5 h-5 ml-1" />
                        </motion.button>
                    </div>
                </div>

                {/* Animated Waveform Visualization */}
                <div className="h-[300px] bg-black/60 border border-white/10 rounded-3xl p-8 flex items-center justify-center relative group overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-cyan-500/5" />
                    <div className="flex items-end gap-1.5 h-32">
                        {[...Array(24)].map((_, i) => (
                            <motion.div
                                key={i}
                                initial={{ height: 10 }}
                                animate={{
                                    height: [10, Math.random() * 100 + 20, 10],
                                }}
                                transition={{
                                    duration: 0.8 + Math.random() * 0.5,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                    delay: i * 0.05
                                }}
                                className="w-2 rounded-full bg-gradient-to-t from-cyan-500 to-purple-500 opacity-60 group-hover:opacity-100 transition-opacity"
                            />
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
