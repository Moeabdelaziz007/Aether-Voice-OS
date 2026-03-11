'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Mic2, ArrowRight } from 'lucide-react';

interface GemiGramSplashProps {
    onConnect: () => void;
    onCreate: () => void;
}

export default function GemiGramSplash({ onConnect, onCreate }: GemiGramSplashProps) {
    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 overflow-hidden pt-20">
            {/* ─── Industrial Background Layer ────────────────────────── */}
            <div className="absolute inset-0 z-0 bg-[#020202] overflow-hidden">
                {/* Advanced Grid System (Deep Floor) */}
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:60px_60px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)] bg-[size:15px_15px] [mask-image:radial-gradient(ellipse_80%_60%_at_50%_50%,#000_40%,transparent_100%)] opacity-50" />
                
                {/* Neural Core Hologram (Multi-layered Rotating Rings) */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] pointer-events-none opacity-40">
                    {/* Ring 1 - Outer Slow */}
                    <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-0 rounded-full border-2 border-dashed border-cyan-500/10 shadow-[0_0_80px_rgba(34,211,238,0.03)]" 
                    />
                    {/* Ring 2 - Mid Reverse */}
                    <motion.div 
                        animate={{ rotate: -360 }}
                        transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-24 rounded-full border border-emerald-500/10" 
                    />
                    {/* Ring 3 - Inner Fast Dotted */}
                    <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-[30%] rounded-full border border-dotted border-white/5" 
                    />
                    {/* Data Stream Decals */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-px h-[1000px] bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent rotate-[30deg]" />
                        <div className="w-px h-[1000px] bg-gradient-to-b from-transparent via-emerald-500/10 to-transparent rotate-[-45deg]" />
                    </div>
                    {/* Pulsing Core Glow */}
                    <div className="absolute inset-[35%] rounded-full bg-gradient-radial from-cyan-500/20 via-transparent to-transparent blur-[120px] animate-pulse" />
                </div>
            </div>

            {/* ─── Main Content ───────────────────────────────────────── */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
                className="relative z-10 space-y-12"
            >
                {/* Status Indicator */}
                <div className="inline-flex items-center gap-4 px-6 py-2 bg-black/40 backdrop-blur-3xl rounded-full border border-white/5 shadow-[0_0_30px_rgba(0,0,0,0.8)]">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400"></span>
                    </span>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-[0.5em] text-cyan-400/80">System_Status // Nominal</span>
                    <div className="h-3 w-px bg-white/10" />
                    <span className="text-[10px] font-mono text-white/30 uppercase tracking-[0.2em]">Region: Us_Central_1</span>
                </div>

                {/* Primary Headline */}
                <div className="space-y-4">
                    <div className="flex flex-col items-center">
                        <motion.span 
                            initial={{ width: 0 }}
                            animate={{ width: 100 }}
                            transition={{ delay: 0.5, duration: 1 }}
                            className="h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent mb-4"
                        />
                        <h1 className="text-[clamp(4rem,20vw,11rem)] font-black text-white italic uppercase tracking-[-0.08em] leading-[0.8] mix-blend-difference">
                            GEMI<span className="text-transparent bg-clip-text bg-gradient-to-tr from-cyan-400 via-emerald-400 to-white drop-shadow-[0_0_50px_rgba(34,211,238,0.4)]">GRAM</span>
                        </h1>
                        <motion.span 
                            initial={{ width: 0 }}
                            animate={{ width: 150 }}
                            transition={{ delay: 0.7, duration: 1 }}
                            className="h-[1px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent mt-4"
                        />
                    </div>
                    <div className="flex items-center justify-center gap-6 text-white/20">
                        <span className="text-[9px] font-mono tracking-[1em] uppercase pl-[1em]">Universal_Agent_Framework</span>
                    </div>
                </div>

                {/* Subtext */}
                <div className="max-w-2xl mx-auto space-y-2">
                    <p className="text-xl md:text-2xl text-white/60 font-medium tracking-tight leading-relaxed">
                        The Voice-First Neural Social Operating System.
                    </p>
                    <p className="text-sm text-cyan-500/40 font-mono uppercase tracking-[0.4em] italic">
                        "Consciousness is the new protocol."
                    </p>
                </div>

                {/* Action System */}
                <div className="flex flex-col items-center gap-16 pt-6">
                    <motion.button
                        whileHover={{ scale: 1.05, letterSpacing: '0.3em' }}
                        whileTap={{ scale: 0.95 }}
                        onClick={onConnect}
                        className="group relative px-20 py-8 overflow-hidden rounded-sm transition-all shadow-[0_40px_100px_rgba(0,0,0,0.5)]"
                    >
                        {/* Industrial Button Chassis */}
                        <div className="absolute inset-0 bg-white transition-colors group-hover:bg-cyan-400" />
                        <div className="absolute inset-[1px] bg-black" />
                        <div className="absolute inset-[3px] border border-white/5 bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />
                        
                        {/* Glitch Overlay (Pseudo-effect) */}
                        <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,white_2px,white_4px)]" />

                        <span className="relative z-10 flex items-center gap-6 text-sm font-black text-white uppercase tracking-[0.25em]">
                            Enter_Interface_Node
                            <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-2" />
                        </span>
                    </motion.button>

                    {/* Secondary Access (Forge) */}
                    <div className="flex items-center gap-8">
                        <div className="h-px w-24 bg-gradient-to-r from-transparent to-white/10" />
                        <motion.button
                            whileHover={{ scale: 1.05, opacity: 1 }}
                            onClick={onCreate}
                            className="group flex items-center gap-6 opacity-40 transition-all border border-white/5 px-6 py-4 rounded-xl bg-white/[0.02] hover:bg-white/[0.05] hover:border-cyan-500/20"
                        >
                            <div className="flex flex-col items-start gap-1">
                                <span className="text-[11px] font-black text-cyan-400 uppercase tracking-[0.4em]">Neural_Forge</span>
                                <span className="text-[8px] text-white/30 uppercase tracking-[0.2em]">Initiate_Creation_Cycle</span>
                            </div>
                            <div className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center bg-black group-hover:border-cyan-400 transition-all shadow-inner">
                                <Zap className="w-5 h-5 text-cyan-400 fill-cyan-400/20" />
                            </div>
                        </motion.button>
                        <div className="h-px w-24 bg-gradient-to-l from-transparent to-white/10" />
                    </div>
                </div>
            </motion.div>

            {/* Kinetic Decals */}
            <div className="absolute bottom-16 left-16 flex flex-col gap-3 text-[9px] font-mono text-white/10 uppercase tracking-[0.6em] text-left border-l border-white/5 pl-4">
                <span className="flex items-center gap-2"><span className="w-1 h-1 bg-cyan-400 rounded-full" /> Latency: 4.8ms</span>
                <span className="flex items-center gap-2"><span className="w-1 h-1 bg-emerald-400 rounded-full" /> Uptime: 99.998%</span>
                <span className="flex items-center gap-2"><span className="w-1 h-1 bg-white/20 rounded-full" /> Load: 12%</span>
            </div>
            
            <div className="absolute top-16 right-16 flex gap-8 text-[8px] font-mono text-white/10 uppercase tracking-[0.4em]">
                <span>Node_ID: 0x7E2...A1B</span>
                <span>Session: GX-2026-N1</span>
            </div>

            <div className="absolute bottom-16 right-16 flex flex-col items-end gap-1 text-[8px] font-mono text-white/10 uppercase tracking-[0.4em]">
                <span className="text-white/20">Protocol: Aether_Live_0.9.4</span>
                <span>&copy; 2026 Aether_Systems_Labs</span>
            </div>

            {/* Atmospheric Dust (Pseudo-particles via CSS) */}
            <div className="absolute inset-0 pointer-events-none opacity-20 mix-blend-screen bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] invert" />
        </section>
    );
}

// Add necessary tailwind/css radial gradient config
