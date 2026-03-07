'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Mic, MicOff } from 'lucide-react';
import { useAetherStore } from '@/store/useAetherStore';

interface VoiceOrbMiniProps {
    onActivate: () => void;
}

/**
 * VoiceOrbMini — A compact voice activation button for the dashboard view.
 * Shows engine state and mic level. Click to enter full voice agent mode.
 */
export default function VoiceOrbMini({ onActivate }: VoiceOrbMiniProps) {
    const engineState = useAetherStore((s) => s.engineState);
    const status = useAetherStore((s) => s.status);
    const micLevel = useAetherStore((s) => s.micLevel);

    const isActive = status === 'connected' || status === 'listening' || status === 'speaking';
    const isListening = engineState === 'LISTENING';
    const isSpeaking = engineState === 'SPEAKING';

    const stateColor = {
        IDLE: 'rgba(75, 85, 99, 0.5)',
        LISTENING: 'rgba(57, 255, 20, 0.6)',
        THINKING: 'rgba(255, 215, 0, 0.6)',
        SPEAKING: 'rgba(0, 255, 136, 0.6)',
        INTERRUPTING: 'rgba(255, 23, 68, 0.6)',
    }[engineState] || 'rgba(75, 85, 99, 0.5)';

    return (
        <motion.button
            onClick={onActivate}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="fixed bottom-6 right-6 z-40 group"
        >
            <div className="relative">
                {/* Outer glow ring */}
                <motion.div
                    className="absolute -inset-2 rounded-full opacity-50"
                    style={{ backgroundColor: stateColor }}
                    animate={{
                        scale: isListening ? [1, 1.2 + micLevel * 0.5, 1] : isSpeaking ? [1, 1.15, 1] : 1,
                        opacity: isActive ? [0.3, 0.6, 0.3] : 0.1,
                    }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                />

                {/* Main button */}
                <div className={`
                    relative w-14 h-14 rounded-full flex items-center justify-center
                    backdrop-blur-xl border transition-all duration-300
                    ${isActive
                        ? 'bg-white/[0.08] border-white/20 shadow-[0_0_20px_rgba(0,243,255,0.2)]'
                        : 'bg-white/[0.04] border-white/[0.08] hover:bg-white/[0.08] hover:border-white/15'
                    }
                `}>
                    {isActive ? (
                        <Mic className="w-5 h-5 text-cyan-400" />
                    ) : (
                        <MicOff className="w-5 h-5 text-white/30 group-hover:text-white/50 transition-colors" />
                    )}
                </div>

                {/* State label */}
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
                    <span className="text-[8px] font-mono text-white/20 uppercase tracking-wider">
                        {isActive ? engineState : 'Voice'}
                    </span>
                </div>
            </div>
        </motion.button>
    );
}
