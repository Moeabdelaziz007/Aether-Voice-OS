"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Eye, CheckCircle2 } from 'lucide-react';
import { useForgeStore, AVAILABLE_LENSES } from '@/store/useForgeStore';

const CATEGORY_COLORS: Record<string, string> = {
    code: 'cyan',
    security: 'red',
    design: 'purple',
    data: 'amber',
};

export default function VisualLenses() {
    const { dna, selectLens } = useForgeStore();

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                    <Eye className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                    <h3 className="text-sm font-black text-white/80 uppercase tracking-wider">Visual Lenses</h3>
                    <p className="text-[9px] text-white/30 uppercase tracking-widest">Proactive Perception</p>
                </div>
            </div>

            <p className="text-[10px] text-white/30 leading-relaxed">
                Equip your agent with a visual lens so it can proactively observe and speak up without being asked. The AI watches and reacts.
            </p>

            {/* Lens Grid */}
            <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_LENSES.map((lens) => {
                    const isSelected = dna.selectedLens === lens.id;
                    const color = CATEGORY_COLORS[lens.category] || 'cyan';

                    return (
                        <motion.button
                            key={lens.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => selectLens(isSelected ? null : lens.id)}
                            className={`relative p-4 rounded-2xl border text-left transition-all ${
                                isSelected
                                    ? `bg-${color}-500/[0.08] border-${color}-500/30 shadow-[0_0_15px_rgba(245,158,11,0.1)]`
                                    : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                            }`}
                            style={isSelected ? {
                                backgroundColor: `rgba(245, 158, 11, 0.08)`,
                                borderColor: `rgba(245, 158, 11, 0.3)`,
                            } : undefined}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <span className="text-xl">{lens.icon}</span>
                                {isSelected && <CheckCircle2 className="w-4 h-4 text-amber-400" />}
                            </div>
                            <div className={`text-xs font-bold mb-1 ${isSelected ? 'text-amber-300' : 'text-white/60'}`}>
                                {lens.name}
                            </div>
                            <p className="text-[9px] text-white/25 leading-tight">{lens.description}</p>
                            <div className="mt-2">
                                <span className="text-[8px] font-mono text-white/15 uppercase tracking-widest px-1.5 py-0.5 bg-white/[0.03] rounded">
                                    {lens.category}
                                </span>
                            </div>
                        </motion.button>
                    );
                })}
            </div>

            {/* Selected Lens Info */}
            {dna.selectedLens && (
                <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 p-3 bg-amber-500/[0.05] border border-amber-500/15 rounded-xl"
                >
                    <Eye className="w-4 h-4 text-amber-400" />
                    <span className="text-[10px] font-bold text-amber-300 uppercase tracking-wider flex-1">
                        Lens Active: {AVAILABLE_LENSES.find((l) => l.id === dna.selectedLens)?.name}
                    </span>
                    <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.6)]" />
                </motion.div>
            )}
        </div>
    );
}
