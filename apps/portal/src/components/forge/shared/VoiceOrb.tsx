"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Mic, AudioLines, Loader2 } from 'lucide-react';
import { useForgeStore } from '@/store/useForgeStore';

interface Props {
    size?: 'sm' | 'md' | 'lg';
    onTap?: () => void;
}

const sizeMap = {
    sm: { outer: 'w-16 h-16', inner: 'w-12 h-12', icon: 'w-6 h-6', glow: 'w-24 h-24' },
    md: { outer: 'w-24 h-24', inner: 'w-20 h-20', icon: 'w-8 h-8', glow: 'w-36 h-36' },
    lg: { outer: 'w-32 h-32', inner: 'w-28 h-28', icon: 'w-12 h-12', glow: 'w-48 h-48' },
};

export default function VoiceOrb({ size = 'md', onTap }: Props) {
    const voiceMode = useForgeStore((s) => s.voiceMode);
    const isListening = useForgeStore((s) => s.isListening);
    const active = voiceMode === 'listening' || isListening;
    const processing = voiceMode === 'processing';
    const responding = voiceMode === 'responding';
    const s = sizeMap[size];

    return (
        <motion.button
            onClick={onTap}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative flex items-center justify-center"
        >
            {/* Outer Glow Ring */}
            <motion.div
                animate={{
                    scale: active ? [1, 1.2, 1] : 1,
                    opacity: active ? [0.3, 0.6, 0.3] : 0.1,
                }}
                transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
                className={`absolute ${s.glow} rounded-full ${
                    active
                        ? 'bg-cyan-500/20 shadow-[0_0_60px_rgba(34,211,238,0.3)]'
                        : responding
                            ? 'bg-purple-500/20 shadow-[0_0_60px_rgba(168,85,247,0.3)]'
                            : 'bg-white/5'
                }`}
            />

            {/* Secondary Pulse Ring */}
            {active && (
                <motion.div
                    animate={{ scale: [1, 1.5], opacity: [0.4, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    className={`absolute ${s.outer} rounded-full border-2 border-cyan-400/40`}
                />
            )}

            {/* Main Orb */}
            <motion.div
                animate={{
                    boxShadow: active
                        ? ['0 0 30px rgba(34,211,238,0.4)', '0 0 60px rgba(34,211,238,0.6)', '0 0 30px rgba(34,211,238,0.4)']
                        : '0 0 10px rgba(255,255,255,0.05)',
                }}
                transition={{ repeat: Infinity, duration: 1.5 }}
                className={`relative ${s.outer} rounded-full flex items-center justify-center border-2 transition-colors ${
                    active
                        ? 'bg-cyan-500/20 border-cyan-400'
                        : responding
                            ? 'bg-purple-500/20 border-purple-400'
                            : processing
                                ? 'bg-amber-500/20 border-amber-400'
                                : 'bg-white/5 border-white/10 hover:border-white/20'
                }`}
            >
                {/* Inner Core */}
                <div className={`${s.inner} rounded-full bg-gradient-to-br ${
                    active ? 'from-cyan-500/30 to-cyan-700/30' :
                    responding ? 'from-purple-500/30 to-purple-700/30' :
                    'from-white/5 to-white/[0.02]'
                } flex items-center justify-center backdrop-blur-sm`}>
                    {processing ? (
                        <Loader2 className={`${s.icon} text-amber-400 animate-spin`} />
                    ) : active ? (
                        <AudioLines className={`${s.icon} text-cyan-400`} />
                    ) : (
                        <Mic className={`${s.icon} ${responding ? 'text-purple-400' : 'text-white/30'}`} />
                    )}
                </div>
            </motion.div>

            {/* Status Label */}
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2">
                <span className={`text-[8px] font-black uppercase tracking-[0.3em] whitespace-nowrap ${
                    active ? 'text-cyan-400' : responding ? 'text-purple-400' : 'text-white/20'
                }`}>
                    {active ? 'Listening' : responding ? 'Speaking' : processing ? 'Processing' : 'Tap to Speak'}
                </span>
            </div>
        </motion.button>
    );
}
