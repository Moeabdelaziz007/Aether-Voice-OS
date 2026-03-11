
import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Sparkles, Zap, Box } from 'lucide-react';

interface ForgePersonalityProps {
    dna: {
        role: string;
        skills: string[];
        personality_quarks: string[];
        visual_grounding?: string;
    };
    micLevel: number;
    variants: any;
}

export default function ForgePersonality({ dna, micLevel, variants }: ForgePersonalityProps) {
    return (
        <div className="flex-1 space-y-12 relative z-10">
            <motion.div variants={variants} custom={1} className="space-y-4">
                <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                    <Terminal className="w-3 h-3 text-cyan-500" /> Core_Role
                </label>
                <div className="text-xl text-white/70 font-medium leading-relaxed italic border-l-4 border-cyan-500/40 pl-8 bg-white/[0.02] py-4 pr-4 rounded-r-lg">
                    {dna.role || 'Awaiting vocal definition...'}
                </div>
            </motion.div>

            <motion.div variants={variants} custom={2} className="space-y-4">
                <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                    <Sparkles className="w-3 h-3 text-emerald-500" /> Skill_Injection
                </label>
                <div className="flex flex-wrap gap-4">
                    {dna.skills.length > 0 ? dna.skills.map((s, i) => (
                        <motion.div
                            key={s}
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.8 + i * 0.1 }}
                            className="px-5 py-2.5 bg-cyan-500/5 border border-cyan-500/20 rounded-sm text-[10px] font-black uppercase tracking-widest text-cyan-400 flex items-center gap-2"
                        >
                            <div className="w-1 h-1 bg-cyan-400 rounded-full" />
                            {s}
                        </motion.div>
                    )) : (
                        <div className="text-[10px] text-white/10 uppercase font-black tracking-[0.3em] italic">...Analyzing stream for capabilities</div>
                    )}
                </div>
            </motion.div>

            <motion.div variants={variants} custom={3} className="space-y-4">
                <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                    <Zap className="w-3 h-3 text-cyan-400" /> Personality_Quarks
                </label>
                <div className="text-[11px] font-mono text-cyan-400/60 flex flex-col gap-1.5 pl-4 border-l border-white/5">
                    {dna.personality_quarks.length > 0 ? dna.personality_quarks.map((q, i) => (
                        <div key={i} className="flex gap-2">
                            <span className="text-cyan-500/40">{`>>`}</span>
                            {q}
                        </div>
                    )) : (
                        <div className="italic text-white/10 uppercase tracking-[0.2em]">...Synthesizing character traits</div>
                    )}
                </div>
            </motion.div>

            <motion.div variants={variants} custom={4} className="space-y-6 pt-4">
                <div className="flex justify-between items-end">
                    <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                        <Box className="w-3 h-3 text-purple-500" /> Neural_Density
                    </label>
                    <span className="text-[10px] font-mono text-cyan-400">{Math.floor(micLevel)}%</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5 p-[1px]">
                    <motion.div
                        animate={{ width: `${micLevel}%` }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="h-full bg-gradient-to-r from-cyan-500 via-emerald-500 to-purple-500 rounded-full shadow-[0_0_15px_rgba(34,211,238,0.5)]"
                    />
                </div>
                {dna.visual_grounding && (
                    <div className="mt-4 p-3 bg-white/[0.02] border border-white/5 rounded flex items-center gap-3">
                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                        <span className="text-[9px] font-mono text-white/40 uppercase tracking-widest">{dna.visual_grounding}</span>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
