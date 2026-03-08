"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Plus } from 'lucide-react';
import { useForgeStore, AVAILABLE_SOULS, AVAILABLE_LENSES } from '@/store/useForgeStore';

function BlueprintItem({ label, value, active, color = 'white' }: { label: string; value: string; active: boolean; color?: string }) {
    return (
        <div className="space-y-1">
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">{label}</span>
            <motion.div
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                className={`text-xs font-bold transition-colors ${active ? `text-${color}/80` : 'text-white/10'}`}
                style={active ? { color: color === 'white' ? 'rgba(255,255,255,0.8)' : undefined } : undefined}
            >
                {value}
            </motion.div>
        </div>
    );
}

export default function DNABlueprintPanel() {
    const dna = useForgeStore((s) => s.dna);
    const selectedSoul = AVAILABLE_SOULS.find((s) => s.id === dna.selectedSoul);
    const selectedLens = AVAILABLE_LENSES.find((l) => l.id === dna.selectedLens);

    return (
        <div className="w-80 border-l border-white/[0.04] bg-white/[0.01] p-6 hidden xl:flex flex-col">
            {/* Header */}
            <div className="flex items-center gap-2 mb-8">
                <Cpu className="w-4 h-4 text-purple-400" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40">
                    Neural Blueprint
                </span>
            </div>

            {/* DNA Fields */}
            <div className="space-y-5">
                <BlueprintItem label="Designation" value={dna.name || '---'} active={!!dna.name} />
                <BlueprintItem label="Archetype" value={dna.role || '---'} active={!!dna.role} />
                <BlueprintItem label="Synapse" value={dna.model || '---'} active={!!dna.model} />
                <BlueprintItem label="Memory" value={dna.memoryType?.toUpperCase() || '---'} active={true} />

                {/* Voice */}
                <BlueprintItem
                    label="Voice Resonator"
                    value={dna.vocalDNA.voiceId || '---'}
                    active={!!dna.vocalDNA.voiceId}
                />

                {/* Soul */}
                <BlueprintItem
                    label="Soul Blueprint"
                    value={selectedSoul?.name || '---'}
                    active={!!selectedSoul}
                />

                {/* Lens */}
                <BlueprintItem
                    label="Visual Lens"
                    value={selectedLens?.name || '---'}
                    active={!!selectedLens}
                />

                {/* Neural Plugs */}
                <div className="space-y-2">
                    <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">
                        Neural Plugs ({dna.neuralPlugs.length})
                    </span>
                    <div className="flex flex-wrap gap-1">
                        {dna.neuralPlugs.length > 0 ? (
                            dna.neuralPlugs.map((p) => (
                                <div key={p} className="px-2 py-0.5 bg-green-500/10 border border-green-500/20 rounded-md text-[8px] text-green-300 uppercase">
                                    {p}
                                </div>
                            ))
                        ) : (
                            <span className="text-[10px] text-white/10 italic">No plugs connected</span>
                        )}
                    </div>
                </div>

                {/* Skills */}
                <div className="space-y-2">
                    <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">
                        Skills ({dna.skills.length})
                    </span>
                    <div className="flex flex-wrap gap-1">
                        {dna.skills.length > 0 ? (
                            dna.skills.map((s) => (
                                <div key={s} className="px-2 py-0.5 bg-purple-500/10 border border-purple-500/20 rounded-md text-[8px] text-purple-300 uppercase">
                                    {s}
                                </div>
                            ))
                        ) : (
                            <span className="text-[10px] text-white/10 italic">No skills injected</span>
                        )}
                    </div>
                </div>
            </div>

            {/* Avatar Preview */}
            <div className="mt-auto pt-8">
                <div className="relative aspect-square w-full rounded-2xl bg-black/40 border border-white/5 overflow-hidden flex items-center justify-center">
                    {dna.avatarUrl ? (
                        <img src={dna.avatarUrl} className="w-full h-full object-cover" alt="Agent Avatar" />
                    ) : (
                        <div className="flex flex-col items-center gap-2 text-white/10">
                            <Plus className="w-8 h-8" />
                            <span className="text-[8px] uppercase tracking-widest">Pending Image</span>
                        </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                    <div className="absolute bottom-3 left-3">
                        <div className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">
                            {dna.name || 'Visual Core'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
