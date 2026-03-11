"use client";

import React, { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { useAgentForgeFSM } from '@/hooks/useAgentForgeFSM';
import { useAetherStore } from '@/store/useAetherStore';
import QuantumNeuralAvatar from '../QuantumNeuralAvatar';
import VoiceOrb from './shared/VoiceOrb';
import {
    Dna, Cpu, Sparkles, ShieldAlert, CheckCircle2,
    ArrowRight, Loader2, Zap, Terminal, Box, Play, Fingerprint
} from 'lucide-react';

export default function ForgeWizard() {
    const fsm = useAgentForgeFSM();
    const transcriptStream = useAetherStore((s) => s.transcriptStream);
    const micLevel = useAetherStore((s) => s.micLevel);
    
    // Scrambling effect for the name field
    const [nameScramble, setNameScramble] = useState('');
    
    useEffect(() => {
        if (fsm.state === 'LISTENING_SPEC' && transcriptStream.interim) {
            // Take the last 3 words for the "scramble" preview
            const words = transcriptStream.interim.split(' ').slice(-3).join('_').toUpperCase();
            setNameScramble(words);
        } else {
            setNameScramble('');
        }
        
        // Voice Actuation for Confirmation
        if (fsm.state === 'AWAITING_CONFIRMATION' && (transcriptStream.final || transcriptStream.interim)) {
            const textToCheck = `${transcriptStream.final} ${transcriptStream.interim}`.toLowerCase();
            if (textToCheck.includes('confirm') || textToCheck.includes('proceed') || textToCheck.includes('yes') || textToCheck.includes('تأكيد')) {
                console.log("🎙️ Voice confirmation detected! Synthesizing DNA...");
                fsm.confirmForge();
            }
        }
    }, [transcriptStream.interim, transcriptStream.final, fsm.state, fsm.confirmForge]);

    const cardVariants: Variants = {
        hidden: { opacity: 0, x: 100, filter: 'blur(20px)' },
        visible: { 
            opacity: 1, 
            x: 0, 
            filter: 'blur(0px)',
            transition: { duration: 1, ease: [0.16, 1, 0.3, 1] }
        }
    };

    const fieldVariants: Variants = {
        hidden: { opacity: 0, scale: 0.95, y: 10 },
        visible: (i: number) => ({
            opacity: 1,
            scale: 1,
            y: 0,
            transition: { delay: 0.5 + i * 0.1, duration: 0.8, ease: "easeOut" }
        })
    };

    return (
        <div className="relative w-full max-w-7xl mx-auto min-h-screen flex flex-col items-center justify-center p-8 overflow-hidden">
            {/* Background Neural Matrix */}
            <div className="absolute inset-0 z-0 opacity-10 pointer-events-none">
                <QuantumNeuralAvatar size="fullscreen" variant="immersive" />
            </div>

            {/* Glassmorphic Grid Overlay */}
            <div className="absolute inset-0 z-1 bg-[radial-gradient(circle_at_50%_50%,transparent_0%,rgba(0,0,0,0.8)_100%)] pointer-events-none" />

            {/* Main Holographic Plate */}
            <div className="relative z-10 w-full grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">

                {/* Left: The Neural Ear & Control Orb */}
                <div className="flex flex-col items-center justify-center space-y-16">
                    <motion.div 
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 1.5 }}
                        className="relative"
                    >
                        <div className="absolute inset-0 bg-cyan-500/10 blur-[120px] rounded-full animate-pulse" />
                        <VoiceOrb
                            size="lg"
                            onTap={() => fsm.state === 'IDLE' ? fsm.initiateForge() : null}
                        />

                        {/* Kinetic Audio Ring */}
                        <motion.div 
                            animate={{ 
                                scale: 1 + (micLevel / 100) * 0.5,
                                opacity: fsm.isListening ? 0.3 : 0
                            }}
                            className="absolute inset-[-32px] rounded-full border border-cyan-500/30 pointer-events-none"
                        />
                    </motion.div>

                    <div className="text-center space-y-6 max-w-sm">
                        <motion.h2 
                            key={fsm.state}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-4xl font-black tracking-tighter uppercase text-white/90 italic"
                        >
                            {fsm.state === 'IDLE' ? 'Neural_Genesis' :
                                fsm.state === 'LISTENING_SPEC' ? 'Soul_Ingestion' :
                                    fsm.state === 'AWAITING_CONFIRMATION' ? 'Validation_Lock' :
                                        'Synthesizing...'}
                        </motion.h2>
                        <p className="text-white/40 text-[10px] uppercase tracking-[0.4em] leading-relaxed font-mono">
                            {fsm.state === 'IDLE' ? '// INITIATE_V_GENESIS_PROTOCOL' :
                                fsm.state === 'LISTENING_SPEC' ? '// DECODING_AUDIO_VECTOR_STREAM' :
                                    fsm.state === 'AWAITING_CONFIRMATION' ? '// BLUEPRINT_STABILIZED_PENDING_COMMIT' :
                                        '// COMMITTING_NEURAL_WEIGHTS_TO_GRID'}
                        </p>
                    </div>

                    {/* FSM Progress Track */}
                    <div className="flex items-center gap-6 text-[9px] font-black uppercase tracking-widest text-white/10 italic">
                        {['IDLE', 'DECODE', 'BLUEPRINT', 'COMMIT'].map((s, i) => {
                            const isActive = (i === 0 && fsm.state === 'IDLE') ||
                                         (i === 1 && fsm.state === 'LISTENING_SPEC') ||
                                         (i === 2 && fsm.state === 'AWAITING_CONFIRMATION') ||
                                         (i === 3 && fsm.state === 'COMMITTING_TO_FIRESTORE');
                            return (
                                <React.Fragment key={s}>
                                    <span className={isActive ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]' : ''}>{s}</span>
                                    {i < 3 && <div className={`h-px w-4 ${isActive ? 'bg-cyan-400' : 'bg-white/10'}`} />}
                                </React.Fragment>
                            );
                        })}
                    </div>
                </div>

                {/* Right: The Holographic DNA Card */}
                <motion.div
                    variants={cardVariants}
                    initial="hidden"
                    animate="visible"
                    className="relative group h-[650px]"
                >
                    {/* Industrial Chassis Decor */}
                    <div className="absolute -top-4 -left-4 w-12 h-12 border-t-2 border-l-2 border-cyan-500/40" />
                    <div className="absolute -bottom-4 -right-4 w-12 h-12 border-b-2 border-r-2 border-cyan-500/40" />

                    <div className="absolute inset-0 bg-black/60 backdrop-blur-3xl border border-white/10 rounded-[20px] shadow-2xl overflow-hidden flex flex-col p-12">
                        
                        {/* Holographic Scanline Effect */}
                        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.02),rgba(0,255,0,0.01),rgba(0,0,255,0.02))] z-10 pointer-events-none bg-[length:100%_4px,3px_100%]" />

                        {/* Header: Blueprint ID */}
                        <div className="flex justify-between items-start mb-16 relative z-10">
                            <motion.div variants={fieldVariants} custom={0} className="space-y-3">
                                <div className="flex items-center gap-3 text-cyan-400">
                                    <Fingerprint className="w-5 h-5" />
                                    <span className="text-[10px] font-black uppercase tracking-[0.5em]">Identity_Matrix</span>
                                </div>
                                <h3 className="text-5xl font-black tracking-tighter uppercase text-white leading-tight">
                                    {nameScramble ? (
                                        <span className="text-cyan-400/80 animate-pulse">{nameScramble}</span>
                                    ) : (
                                        fsm.currentDNA.name || 'UNNAMED_ENTITY'
                                    )}
                                </h3>
                                <div className="text-[9px] font-mono text-white/20 uppercase tracking-[0.2em]">Hash: 0x${Math.random().toString(16).slice(2, 10)}</div>
                            </motion.div>
                            <div className="bg-white/5 p-5 rounded-xl border border-white/10 shadow-inner">
                                <Cpu className="w-8 h-8 text-cyan-500/40" />
                            </div>
                        </div>

                        {/* Body: Personality Matrix */}
                        <div className="flex-1 space-y-12 relative z-10">
                            <motion.div variants={fieldVariants} custom={1} className="space-y-4">
                                <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                                    <Terminal className="w-3 h-3 text-cyan-500" /> Core_Role
                                </label>
                                <div className="text-xl text-white/70 font-medium leading-relaxed italic border-l-4 border-cyan-500/40 pl-8 bg-white/[0.02] py-4 pr-4 rounded-r-lg">
                                    {fsm.currentDNA.role || 'Awaiting vocal definition...'}
                                </div>
                            </motion.div>

                            <motion.div variants={fieldVariants} custom={2} className="space-y-4">
                                <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                                    <Sparkles className="w-3 h-3 text-emerald-500" /> Skill_Injection
                                </label>
                                <div className="flex flex-wrap gap-4">
                                    {fsm.currentDNA.skills.length > 0 ? fsm.currentDNA.skills.map((s, i) => (
                                        <motion.div
                                            key={s}
                                            initial={{ x: -20, opacity: 0 }}
                                            animate={{ x: 0, opacity: 1 }}
                                            transition={{ delay: 0.8 + i * 0.1 }}
                                            className="px-5 py-2.5 bg-cyan-500/5 border border-cyan-500/20 rounded-sm text-[10px] font-black uppercase tracking-widest text-cyan-400 flex items-center gap-2"
                                        >
                                            <div className="w-1 h-1 bg-cyan-400 rounded-full" />
                                            {s}
                                        </motion.div>
                                    )) : (
                                        <div className="text-[10px] text-white/10 uppercase font-black tracking-[0.3em] italic">...Analyzing stream for capabilities</div>
                                    )}
                                </div>
                            </motion.div>

                            <motion.div variants={fieldVariants} custom={3} className="space-y-6 pt-4">
                                <div className="flex justify-between items-end">
                                    <label className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em] flex items-center gap-2">
                                        <Box className="w-3 h-3 text-purple-500" /> Neural_Density
                                    </label>
                                    <span className="text-[10px] font-mono text-cyan-400">{Math.floor(micLevel)}%</span>
                                </div>
                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5 p-[1px]">
                                    <motion.div
                                        animate={{ width: `${micLevel}%` }}
                                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                        className="h-full bg-gradient-to-r from-cyan-500 via-emerald-500 to-purple-500 rounded-full shadow-[0_0_15px_rgba(34,211,238,0.5)]"
                                    />
                                </div>
                            </motion.div>
                        </div>

                        {/* Footer Overlay */}
                        <AnimatePresence>
                            {(fsm.state === 'AWAITING_CONFIRMATION' || fsm.state === 'COMMITTING_TO_FIRESTORE') && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="absolute inset-0 flex items-center justify-center bg-black/95 backdrop-blur-xl z-30 p-12 text-center"
                                >
                                    <motion.div 
                                        initial={{ scale: 0.9, y: 20 }}
                                        animate={{ scale: 1, y: 0 }}
                                        className="space-y-10"
                                    >
                                        <div className="w-24 h-24 bg-cyan-500/10 border-2 border-cyan-500/40 rounded-full flex items-center justify-center mx-auto shadow-[0_0_80px_rgba(34,211,238,0.3)]">
                                            {fsm.state === 'COMMITTING_TO_FIRESTORE' ? 
                                                <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" /> : 
                                                <motion.div animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
                                                    <Zap className="w-10 h-10 text-cyan-400 fill-cyan-400" />
                                                </motion.div>
                                            }
                                        </div>
                                        <div className="space-y-4">
                                            <h4 className="text-3xl font-black uppercase tracking-tighter text-white">Commit_Required</h4>
                                            <p className="text-white/40 text-[10px] uppercase tracking-[0.4em] font-mono leading-relaxed">
                                                Neural_Weight_Stabilization_Complete. <br />
                                                Say "Confirm" or execute manual override.
                                            </p>
                                        </div>
                                        <motion.button
                                            whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(34,211,238,0.6)' }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={fsm.confirmForge}
                                            disabled={fsm.state === 'COMMITTING_TO_FIRESTORE'}
                                            className="px-16 py-6 bg-cyan-500 text-black rounded-[4px] text-xs font-black uppercase tracking-[0.3em] shadow-2xl transition-all disabled:opacity-50"
                                        >
                                            {fsm.state === 'COMMITTING_TO_FIRESTORE' ? 'SYNTHESIZING_DNA...' : 'INITIATE_FORGE_SEQUENCE'}
                                        </motion.button>
                                    </motion.div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Industrial Decals */}
                    <div className="absolute top-6 right-16 text-[8px] font-mono text-cyan-400/20 uppercase tracking-[0.5em] origin-right rotate-90 transform translate-x-full">
                        Secure_Protocol_X99
                    </div>
                </motion.div>

            </div>

            {/* Bottom Status Layer */}
            <div className="absolute bottom-12 flex justify-between w-full px-20">
                <div className="text-[9px] font-mono text-white/10 uppercase tracking-[0.5em]">
                    System_Load: 14.8% // Entropy_Check: Optimal
                </div>
                <div className="text-[9px] font-mono text-white/10 uppercase tracking-[0.5em]">
                    (C) 2026 Aether_Labs // Neural_Forge_V2.0
                </div>
            </div>
        </div>
    );
}
