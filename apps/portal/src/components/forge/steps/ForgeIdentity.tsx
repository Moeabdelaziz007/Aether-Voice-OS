
import React from 'react';
import { motion } from 'framer-motion';
import { Fingerprint, Cpu } from 'lucide-react';

interface ForgeIdentityProps {
    name: string;
    scramble: string;
    variants: any;
}

export default function ForgeIdentity({ name, scramble, variants }: ForgeIdentityProps) {
    return (
        <div className="flex justify-between items-start mb-16 relative z-10">
            <motion.div variants={variants} custom={0} className="space-y-3">
                <div className="flex items-center gap-3 text-cyan-400">
                    <Fingerprint className="w-5 h-5" />
                    <span className="text-[10px] font-black uppercase tracking-[0.5em]">Identity_Matrix</span>
                </div>
                <h3 className="text-5xl font-black tracking-tighter uppercase text-white leading-tight">
                    {scramble ? (
                        <span className="text-cyan-400/80 animate-pulse">{scramble}</span>
                    ) : (
                        name || 'UNNAMED_ENTITY'
                    )}
                </h3>
                <div className="text-[9px] font-mono text-white/20 uppercase tracking-[0.2em]">Hash: 0x${Math.random().toString(16).slice(2, 10)}</div>
            </motion.div>
            <div className="bg-white/5 p-5 rounded-xl border border-white/10 shadow-inner">
                <Cpu className="w-8 h-8 text-cyan-500/40" />
            </div>
        </div>
    );
}
