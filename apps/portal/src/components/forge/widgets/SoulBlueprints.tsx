"use client";

import React, { useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, CheckCircle2, Star } from 'lucide-react';
import { useForgeStore, AVAILABLE_SOULS } from '@/store/useForgeStore';

export default function SoulBlueprints() {
    const { dna, selectSoul } = useForgeStore();
    
    const handleSelectSoul = useCallback((soulId: string | null) => {
        selectSoul(soulId);
    }, [selectSoul]);
    
    const selectedSoulDetail = useMemo(() => {
        return AVAILABLE_SOULS.find((s) => s.id === dna.selectedSoul);
    }, [dna.selectedSoul]);

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 bg-pink-500/10 border border-pink-500/20 rounded-xl">
                    <Sparkles className="w-5 h-5 text-pink-400" />
                </div>
                <div>
                    <h3 className="text-sm font-black text-white/80 uppercase tracking-wider">Soul Blueprints</h3>
                    <p className="text-[9px] text-white/30 uppercase tracking-widest">Expert Prompt Library</p>
                </div>
            </div>

            <p className="text-[10px] text-white/30 leading-relaxed">
                Don&apos;t write prompts from scratch. Pick an Expert Soul as a base, then season it with your voice to create a unique personality.
            </p>

            {/* Soul Grid */}
            <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_SOULS.map((soul) => {
                    const isSelected = dna.selectedSoul === soul.id;

                    return (
                        <motion.button
                            key={soul.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleSelectSoul(isSelected ? null : soul.id)}
                            className={`relative p-4 rounded-2xl border text-left transition-all ${
                                isSelected
                                    ? 'bg-pink-500/[0.08] border-pink-500/30 shadow-[0_0_15px_rgba(236,72,153,0.1)]'
                                    : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                            }`}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <span className="text-xl">{soul.icon}</span>
                                {isSelected ? (
                                    <CheckCircle2 className="w-4 h-4 text-pink-400" />
                                ) : (
                                    <div className="flex items-center gap-0.5">
                                        <Star className="w-3 h-3 text-amber-400/40" />
                                        <span className="text-[9px] font-mono text-amber-400/40">{soul.auraLevel}</span>
                                    </div>
                                )}
                            </div>
                            <div className={`text-xs font-bold mb-1 ${isSelected ? 'text-pink-300' : 'text-white/60'}`}>
                                {soul.name}
                            </div>
                            <p className="text-[9px] text-white/25 leading-tight line-clamp-2">{soul.basePrompt}</p>
                            <div className="mt-2">
                                <span className="text-[8px] font-mono text-white/15 uppercase tracking-widest px-1.5 py-0.5 bg-white/[0.03] rounded">
                                    {soul.category}
                                </span>
                            </div>
                        </motion.button>
                    );
                })}
            </div>

            {/* Selected Soul Detail */}
            {selectedSoulDetail && (
                <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-pink-500/[0.04] border border-pink-500/15 rounded-2xl space-y-3"
                >
                    <div className="flex items-center gap-2">
                        <span className="text-lg">{selectedSoulDetail.icon}</span>
                        <span className="text-[10px] font-black text-pink-300 uppercase tracking-wider">
                            {selectedSoulDetail.name} — Active Soul
                        </span>
                    </div>
                    <div className="bg-black/30 rounded-xl p-3 border border-white/5">
                        <p className="text-[10px] text-white/40 italic leading-relaxed">
                            &quot;{selectedSoulDetail.basePrompt}&quot;
                        </p>
                    </div>
                    <p className="text-[9px] text-white/20">
                        💡 Speak to the Forge to season this soul with your unique personality and preferences.
                    </p>
                </motion.div>
            )}
        </div>
    );
}
