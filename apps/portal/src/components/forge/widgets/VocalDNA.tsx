"use client";

import React, { useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Volume2, Dna, CheckCircle2, Loader2 } from 'lucide-react';
import { useForgeStore, VOICE_RESONATORS } from '@/store/useForgeStore';

export default function VocalDNA() {
    const { dna, updateVocalDNA, startVoiceCloning } = useForgeStore();
    const { vocalDNA } = dna;
    
    const handleVoiceSelect = useCallback((voiceId: string, provider: string, isCloneOption: boolean) => {
        if (isCloneOption) {
            startVoiceCloning();
        } else {
            updateVocalDNA({ voiceId, provider: provider as 'elevenlabs' | 'google' | 'custom' });
        }
    }, [updateVocalDNA, startVoiceCloning]);
    
    const selectedVoice = useMemo(() => {
        return VOICE_RESONATORS.find((v) => v.id === vocalDNA.voiceId);
    }, [vocalDNA.voiceId]);

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                    <Dna className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                    <h3 className="text-sm font-black text-white/80 uppercase tracking-wider">Vocal DNA</h3>
                    <p className="text-[9px] text-white/30 uppercase tracking-widest">The Resonator Library</p>
                </div>
            </div>

            {/* Voice Resonator Grid */}
            <div className="grid grid-cols-2 gap-2.5">
                {VOICE_RESONATORS.map((voice) => {
                    const isSelected = vocalDNA.voiceId === voice.id;
                    const isCloneOption = voice.provider === 'custom';

                    return (
                        <motion.button
                            key={voice.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleVoiceSelect(voice.id, voice.provider, isCloneOption)}
                            className={`relative p-4 rounded-2xl border text-left transition-all overflow-hidden ${
                                isSelected
                                    ? 'bg-purple-500/10 border-purple-500/30 shadow-[0_0_20px_rgba(168,85,247,0.15)]'
                                    : isCloneOption
                                        ? 'bg-gradient-to-br from-cyan-500/[0.05] to-purple-500/[0.05] border-dashed border-white/10 hover:border-cyan-500/30'
                                        : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                            }`}
                        >
                            {/* Clone Progress Overlay */}
                            {isCloneOption && vocalDNA.isCloning && (
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${vocalDNA.cloneProgress}%` }}
                                    className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full"
                                />
                            )}

                            <div className="flex items-start justify-between mb-2">
                                <span className="text-lg">{voice.preview}</span>
                                {isSelected && <CheckCircle2 className="w-4 h-4 text-purple-400" />}
                                {isCloneOption && vocalDNA.isCloning && (
                                    <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                                )}
                            </div>
                            <div className={`text-xs font-bold mb-0.5 ${isSelected ? 'text-purple-300' : 'text-white/60'}`}>
                                {voice.name}
                            </div>
                            <div className="text-[9px] text-white/30 leading-tight">{voice.desc}</div>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="text-[8px] font-mono text-white/20 uppercase">{voice.gender}</span>
                                <span className="text-[8px] font-mono text-purple-400/40 uppercase">{voice.provider}</span>
                            </div>
                        </motion.button>
                    );
                })}
            </div>

            {/* Voice Cloning Shield */}
            <AnimatePresence>
                {vocalDNA.isCloning && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="bg-cyan-500/[0.05] border border-cyan-500/20 rounded-2xl p-4 overflow-hidden"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <motion.div
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ repeat: Infinity, duration: 1 }}
                                className="p-2 bg-cyan-500/20 rounded-full"
                            >
                                <Mic className="w-4 h-4 text-cyan-400" />
                            </motion.div>
                            <div>
                                <div className="text-[10px] font-black text-cyan-400 uppercase tracking-widest">
                                    Voice Cloning Shield Active
                                </div>
                                <div className="text-[9px] text-white/30">
                                    Speak naturally for 10 seconds... Harvesting vocal DNA
                                </div>
                            </div>
                        </div>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                                animate={{ width: `${vocalDNA.cloneProgress}%` }}
                                className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_10px_rgba(34,211,238,0.5)] rounded-full"
                            />
                        </div>
                        <div className="text-[9px] text-right text-cyan-400/60 mt-1 font-mono">
                            {vocalDNA.cloneProgress}% Complete
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Selected Voice Preview */}
            {selectedVoice && !vocalDNA.isCloning && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-3 p-3 bg-purple-500/[0.05] border border-purple-500/20 rounded-xl"
                >
                    <Volume2 className="w-4 h-4 text-purple-400" />
                    <div className="flex-1">
                        <span className="text-[10px] font-bold text-purple-300 uppercase tracking-wider">
                            Active Resonator: {selectedVoice.name}
                        </span>
                    </div>
                    <button className="px-3 py-1 bg-purple-500/10 rounded-lg text-[9px] font-bold text-purple-400 uppercase hover:bg-purple-500/20 transition-colors">
                        Preview
                    </button>
                </motion.div>
            )}
        </div>
    );
}
