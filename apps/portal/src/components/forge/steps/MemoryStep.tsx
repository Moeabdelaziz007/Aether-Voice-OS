"use client";

import React from 'react';
import { Database, Box } from 'lucide-react';

interface Props {
    memoryType: 'firebase' | 'local';
    updateDNA: (data: any) => void;
}

const MEM_OPTIONS = [
    { id: 'firebase' as const, label: 'Cloud Sync (Firebase)', icon: Database, desc: 'Sub-100ms cross-device recall' },
    { id: 'local' as const, label: 'Local Core', icon: Box, desc: 'Privacy-focused on-device storage' },
];

export default function MemoryStep({ memoryType, updateDNA }: Props) {
    return (
        <div className="space-y-8 text-center mt-10">
            <h2 className="text-3xl font-black tracking-tighter uppercase text-white/90">Synaptic Storage</h2>
            <div className="flex justify-center gap-6">
                {MEM_OPTIONS.map((mem) => (
                    <button
                        key={mem.id}
                        onClick={() => updateDNA({ memoryType: mem.id })}
                        className={`w-56 p-6 rounded-[32px] border transition-all flex flex-col items-center gap-4 ${memoryType === mem.id
                                ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400 shadow-[0_0_30px_rgba(34,211,238,0.1)]'
                                : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                            }`}
                    >
                        <div className={`p-4 rounded-2xl ${memoryType === mem.id ? 'bg-cyan-500/20' : 'bg-white/5'}`}>
                            <mem.icon className="w-8 h-8" />
                        </div>
                        <div className="space-y-1">
                            <div className="font-bold text-[11px] uppercase tracking-widest">{mem.label}</div>
                            <div className="text-[9px] opacity-60 leading-tight uppercase tracking-wide">{mem.desc}</div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
