"use client";

import React from 'react';
import { AVAILABLE_SOULS, AVAILABLE_LENSES } from '@/store/useForgeStore';

interface Props {
    dna: any;
}

export default function ReviewStep({ dna }: Props) {
    const reviews = [
        { label: 'Agent Core', value: `${dna.name || '---'} (${dna.role || '---'})`, color: 'text-cyan-400' },
        { label: 'Neural Backbone', value: dna.model, color: 'text-white/80' },
        { label: 'Memory Storage', value: `${dna.memoryType.toUpperCase()} SYNC`, color: 'text-green-400' },
        { label: 'Skill Payload', value: `${dna.skills.length} SKILLS LOADED`, color: 'text-purple-400' },
        { label: 'Voice Resonator', value: dna.vocalDNA.voiceId || 'Default', color: 'text-purple-300' },
        { label: 'Neural Plugs', value: `${dna.neuralPlugs.length} CONNECTED`, color: 'text-green-300' },
        { label: 'Visual Lens', value: AVAILABLE_LENSES.find((l) => l.id === dna.selectedLens)?.name || 'None', color: 'text-amber-400' },
        { label: 'Soul Blueprint', value: AVAILABLE_SOULS.find((s) => s.id === dna.selectedSoul)?.name || 'None', color: 'text-pink-400' },
    ];

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-black tracking-tighter uppercase text-white/90">Integration Review</h2>
            <div className="bg-black/30 rounded-3xl p-6 border border-white/5 space-y-4 shadow-inner">
                {reviews.map((row, i, arr) => (
                    <div key={row.label} className={`flex justify-between items-center ${i < arr.length - 1 ? 'border-b border-white/5 pb-3' : ''}`}>
                        <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">{row.label}</span>
                        <span className={`text-[11px] font-black uppercase tracking-wider ${row.color}`}>{row.value}</span>
                    </div>
                ))}
            </div>
            <p className="text-[9px] text-white/40 text-center italic uppercase tracking-[0.2em]">
                Finalizing will commit the agent&apos;s DNA to the Gemigram Neural Fabric.
            </p>
        </div>
    );
}
