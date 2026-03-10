"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Zap, Loader2, Play, Circle, Terminal } from 'lucide-react';
import { useAetherGateway } from '@/hooks/useAetherGateway';
import { useAetherStore } from '@/store/useAetherStore';

/**
 * VoiceIntentBar — The Zero-UI Neural Interface.
 * Replaces the Omnibar. Purely voice-driven.
 */
export default function VoiceIntentBar() {
    const { status, isConnected } = useAetherGateway();
    const { transcript, isListening, avatarState } = useAetherStore();
    const [interimText, setInterimText] = useState("");

    // Detect if we are in "Forge Mode" or "Hub Mode"
    const isForgeMode = typeof window !== 'undefined' && window.location.pathname.includes('/forge');

    return (
        <div className="fixed inset-x-0 bottom-12 flex flex-col items-center justify-center z-50 pointer-events-none px-4">

            {/* Real-time Streaming Transcript */}
            <AnimatePresence>
                {(isListening || transcript.length > 0) && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="mb-6 max-w-2xl w-full text-center"
                    >
                        <div className="bg-black/60 backdrop-blur-3xl border border-white/5 p-6 rounded-3xl shadow-2xl">
                            <div className="flex items-center justify-center gap-2 mb-3">
                                {isListening ? (
                                    <div className="flex gap-1">
                                        {[1, 2, 3].map(i => (
                                            <motion.div
                                                key={i}
                                                animate={{ height: [4, 12, 4] }}
                                                transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
                                                className="w-[2px] bg-cyan-400"
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    <Terminal className="w-3 h-3 text-white/20" />
                                )}
                                <span className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-400/60">
                                    {isListening ? 'Streaming_Input' : 'Neural_Buffer'}
                                </span>
                            </div>

                            <p className="text-lg md:text-xl font-medium tracking-tight leading-relaxed">
                                <span className="text-white/80">{transcript[transcript.length - 1]?.content || ""}</span>
                                <motion.span
                                    animate={{ opacity: [1, 0, 1] }}
                                    transition={{ repeat: Infinity, duration: 0.8 }}
                                    className="inline-block w-1.5 h-5 bg-cyan-500 ml-1 translate-y-1"
                                />
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Neural Control Bar */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="pointer-events-auto"
            >
                <div className="flex items-center gap-4 bg-[#0a0a0c]/80 backdrop-blur-2xl px-6 py-4 rounded-full border border-white/5 shadow-[0_0_50px_rgba(0,0,0,0.5)]">

                    {/* Status Signal */}
                    <div className="flex items-center gap-3 pr-6 border-r border-white/10 font-mono">
                        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-cyan-500 shadow-[0_0_10px_#22d3ee]' : 'bg-red-500'} animate-pulse`} />
                        <span className="text-[10px] uppercase font-black tracking-widest text-white/40">
                            {isConnected ? 'NODE_ACTIVE' : 'OFFLINE'}
                        </span>
                    </div>

                    {/* VAD Visualization */}
                    <div className="flex items-center gap-6 px-4">
                        <div className="flex flex-col items-center">
                            <span className={`text-[8px] font-black uppercase tracking-[0.3em] mb-1.5 ${isListening ? 'text-cyan-400' : 'text-white/10'}`}>
                                Acoustic_Field
                            </span>
                            <div className="flex gap-1 h-3 items-center">
                                {Array.from({ length: 12 }).map((_, i) => (
                                    <motion.div
                                        key={i}
                                        animate={{
                                            height: isListening ? [2, Math.random() * 12 + 2, 2] : 2,
                                            backgroundColor: isListening ? '#22d3ee' : 'rgba(255,255,255,0.05)'
                                        }}
                                        transition={{ duration: 0.2, repeat: Infinity }}
                                        className="w-[3px] rounded-full"
                                    />
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Action Hub (Indicator) */}
                    <div className="flex items-center gap-3 pl-6 border-l border-white/10">
                        <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/5 bg-white/5 text-[9px] font-black uppercase tracking-widest text-white/30`}>
                            {isListening ? (
                                <><Loader2 className="w-3 h-3 animate-spin" /> Recording</>
                            ) : (
                                <><Mic className="w-3 h-3" /> Voice Ready</>
                            )}
                        </div>
                    </div>

                </div>
            </motion.div>

        </div>
    );
}
