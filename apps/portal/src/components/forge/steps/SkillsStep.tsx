"use client";

import React from 'react';
import { motion } from 'framer-motion';
import ClawHubWidget from '../widgets/ClawHubWidget';

interface Props {
    skills: string[];
}

export default function SkillsStep({ skills }: Props) {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-black tracking-tighter uppercase text-white/90">Skill Acquisition</h2>
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                    <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.15em]">
                        ClawHub Connected
                    </span>
                </div>
            </div>
            <p className="text-[10px] text-white/40 leading-relaxed uppercase tracking-[0.1em]">
                Inject specialized capabilities from the ClawHub skill repository.
            </p>
            <ClawHubWidget />
            {skills.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-cyan-500/[0.05] border border-cyan-500/20 rounded-2xl p-4"
                >
                    <div className="text-[9px] font-mono text-cyan-400/60 uppercase tracking-widest mb-2">
                        Injected Neural Payload
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                        {skills.map((s) => (
                            <span key={s} className="px-2.5 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-[8px] font-black text-cyan-300 uppercase tracking-widest">
                                {s}
                            </span>
                        ))}
                    </div>
                </motion.div>
            )}
        </div>
    );
}
