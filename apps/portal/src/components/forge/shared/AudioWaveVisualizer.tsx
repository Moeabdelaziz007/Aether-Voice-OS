"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { useForgeStore } from '@/store/useForgeStore';

interface Props {
    barCount?: number;
}

export default function AudioWaveVisualizer({ barCount = 40 }: Props) {
    const isListening = useForgeStore((s) => s.isListening);
    const voiceMode = useForgeStore((s) => s.voiceMode);
    const active = isListening || voiceMode === 'listening';

    return (
        <div className="flex items-center gap-2">
            <div className="text-[8px] font-mono text-cyan-400/40 uppercase tracking-widest whitespace-nowrap">
                Audio Analysis | Genesis Wave
            </div>
            <div className="flex-1 h-8 flex items-end gap-[2px] px-4">
                {[...Array(barCount)].map((_, i) => (
                    <motion.div
                        key={i}
                        animate={{
                            height: active ? [4, Math.random() * 24 + 4, 4] : 4,
                        }}
                        transition={{
                            repeat: Infinity,
                            duration: 0.4 + Math.random() * 0.6,
                            ease: 'easeInOut',
                        }}
                        className="flex-1 bg-gradient-to-t from-cyan-500/40 to-purple-500/40 rounded-full"
                    />
                ))}
            </div>
            <div className="text-[8px] font-mono text-cyan-400/40 uppercase tracking-widest">
                {active ? 'LIVE' : 'STANDBY'}
            </div>
        </div>
    );
}
