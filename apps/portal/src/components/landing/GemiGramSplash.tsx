'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Mic2 } from 'lucide-react';
import { useAetherStore } from '@/store/useAetherStore';

interface GemiGramSplashProps {
    onConnect: () => void;
    onCreate: () => void;
}

export default function GemiGramSplash({ onConnect, onCreate }: GemiGramSplashProps) {
    return (
        <section className="relative min-h-[90vh] flex flex-col items-center justify-center text-center px-4 overflow-hidden pt-20">
            {/* Massive Hero Core (Visualized via CSS Gradients & Blurs) */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl aspect-square overflow-hidden pointer-events-none opacity-40">
                <div className="absolute inset-0 rounded-full border border-cyan-500/20 animate-[spin_20s_linear_infinite]" />
                <div className="absolute inset-8 rounded-full border border-purple-500/20 animate-[spin_15s_linear_infinite_reverse]" />
                <div className="absolute inset-16 rounded-full border-2 border-dashed border-white/5 animate-pulse" />
                <div className="absolute inset-1/4 rounded-full bg-gradient-radial from-cyan-500/10 via-purple-500/5 to-transparent blur-3xl scale-125" />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="relative z-10"
            >
                <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full border border-white/10 backdrop-blur-md shadow-2xl">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,1)] animate-pulse" />
                    <span className="text-[10px] font-black uppercase tracking-[0.3em] text-white/60">Multimodal Protocol Live</span>
                </div>

                <h1 className="text-7xl md:text-9xl font-black text-white italic uppercase tracking-[-0.05em] leading-none mb-4 selection:bg-cyan-500">
                    GEMI<span className="text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]">GRAM</span>
                </h1>

                <p className="text-lg md:text-2xl text-white/40 font-medium tracking-tight mb-12 max-w-2xl mx-auto">
                    The Voice-Native AI Social Nexus. <br />
                    <span className="text-white/20">Forge your agent. Sync your soul.</span>
                </p>

                <div className="flex flex-col items-center gap-8">
                    <motion.button
                        whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(188,19,254,0.4)' }}
                        whileTap={{ scale: 0.95 }}
                        onClick={onConnect}
                        className="group relative px-12 py-5 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl overflow-hidden shadow-[0_0_20px_rgba(188,19,254,0.2)]"
                    >
                        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <span className="relative z-10 text-lg font-black text-white uppercase tracking-[0.2em] italic">Connect Now</span>
                    </motion.button>

                    <button
                        onClick={onCreate}
                        className="group flex flex-col items-center gap-2 text-[10px] font-black text-white/30 hover:text-cyan-400 uppercase tracking-[0.4em] transition-all"
                    >
                        <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center group-hover:border-cyan-500/50 group-hover:shadow-[0_0_15px_rgba(34,211,238,0.2)] transition-all">
                            <Mic2 className="w-5 h-5" />
                        </div>
                        Create Agent
                    </button>
                </div>
            </motion.div>
        </section>
    );
}

// Add necessary tailwind/css radial gradient config
