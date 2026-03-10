'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Mic2, Zap, Brain, Shield, Rocket } from 'lucide-react';

interface IdentityCardProps {
    name: string;
    role: string;
    icon: React.ElementType;
    stats: string;
    active?: boolean;
}

const identities: IdentityCardProps[] = [
    { name: 'Atlas', role: 'AI Companion', icon: Brain, stats: '5K', active: true },
    { name: 'Nova', role: 'Creative Guide', icon: Zap, stats: '179', active: true },
    { name: 'Orion', role: 'Strategic Analyst', icon: Shield, stats: '12K', active: true },
    { name: 'Lyra', role: 'Linguistic Savant', icon: Mic2, stats: '8K', active: true },
    { name: 'Kora', role: 'Neural Architect', icon: Rocket, stats: '131', active: true }
];

export default function NeuralIdentityGrid() {
    return (
        <section className="w-full max-w-7xl mx-auto px-10 py-24">
            <div className="mb-12">
                <h2 className="text-[10px] font-black uppercase tracking-[0.4em] text-cyan-500/60 mb-2">Cognitive Ecosystem</h2>
                <h3 className="text-3xl font-black text-white italic uppercase tracking-tighter">Neural Identities</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
                {identities.map((identity, i) => (
                    <motion.div
                        key={identity.name}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        whileHover={{ y: -10, scale: 1.02 }}
                        className="relative group cursor-pointer"
                    >
                        {/* Glow Background */}
                        <div className="absolute inset-0 bg-cyan-500/0 group-hover:bg-cyan-500/5 blur-2xl transition-all duration-500 rounded-2xl" />

                        {/* Card Content */}
                        <div className="relative bg-white/[0.02] border border-white/5 group-hover:border-cyan-500/30 rounded-2xl p-6 backdrop-blur-sm transition-all duration-300">
                            <div className="aspect-square rounded-xl bg-gradient-to-br from-white/5 to-transparent border border-white/5 mb-6 flex items-center justify-center relative overflow-hidden">
                                {/* Holographic Scanline Effect */}
                                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-400/10 to-transparent h-1/2 w-full animate-[scan_3s_linear_infinite] opacity-0 group-hover:opacity-100" />
                                <identity.icon className="w-12 h-12 text-white/20 group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_10px_rgba(34,211,238,0.8)] transition-all duration-500" />
                            </div>

                            <div className="flex items-start justify-between mb-1">
                                <h4 className="font-black text-lg text-white group-hover:text-cyan-400 transition-colors uppercase italic">{identity.name}</h4>
                                <div className="flex items-center gap-1 opacity-40 group-hover:opacity-100 transition-opacity">
                                    <Zap className="w-3 h-3 text-cyan-400" />
                                    <span className="text-[10px] font-bold text-white">{identity.stats}</span>
                                </div>
                            </div>

                            <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest mb-4">{identity.role}</p>

                            <div className="flex items-center gap-2 pt-4 border-t border-white/5">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)] animate-pulse" />
                                <span className="text-[9px] font-black text-cyan-400 leading-none uppercase tracking-widest">Voice Online</span>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            <style jsx>{`
                @keyframes scan {
                    0% { transform: translateY(-100%); }
                    100% { transform: translateY(200%); }
                }
            `}</style>
        </section>
    );
}
