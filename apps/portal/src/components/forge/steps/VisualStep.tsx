"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface Props {
    avatarUrl?: string;
    agentName: string;
}

export default function VisualStep({ avatarUrl, agentName }: Props) {
    return (
        <div className="space-y-8 text-center mt-10">
            <h2 className="text-3xl font-black tracking-tighter uppercase text-white/90">Visual Matrix</h2>
            <p className="text-[10px] text-white/40 max-w-sm mx-auto italic uppercase tracking-[0.15em]">
                Synthesizing a unique neural avatar for {agentName || 'your agent'}...
            </p>
            <div className="relative w-48 h-48 mx-auto">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-0 border-2 border-dashed border-cyan-500/30 rounded-full"
                />
                <div className="absolute inset-4 rounded-full bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden border border-white/10 shadow-[0_0_50px_rgba(34,211,238,0.1)]">
                    {avatarUrl ? (
                        <img src={avatarUrl} className="w-full h-full object-cover" alt="Avatar" />
                    ) : (
                        <Sparkles className="w-12 h-12 text-cyan-400 animate-pulse" />
                    )}
                </div>
            </div>
            <button className="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 px-8 py-2.5 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-cyan-500/20 transition-all shadow-lg active:scale-95">
                Generate Agent Avatar
            </button>
        </div>
    );
}
