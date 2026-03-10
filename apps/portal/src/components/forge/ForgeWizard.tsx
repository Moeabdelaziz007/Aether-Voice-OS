"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgentForgeFSM } from '@/hooks/useAgentForgeFSM';
import { useAetherStore } from '@/store/useAetherStore';
import QuantumNeuralAvatar from '../QuantumNeuralAvatar';
import VoiceOrb from './shared/VoiceOrb';
import {
    Dna, Cpu, Sparkles, ShieldAlert, CheckCircle2,
    ArrowRight, Loader2, Zap, Terminal, Box, Play
} from 'lucide-react';

/**
 * ForgeWizard (Zero-UI Edition)
 * Purely voice-driven holographic blueprint assembly.
 * Zero <input> - everything is inferred from the neural stream.
 */
export default function ForgeWizard() {
    const fsm = useAgentForgeFSM();
    const store = useAetherStore();
    const [scrambling, setScrambling] = useState(false);

    useEffect(() => {
        if (fsm.isListening) {
            setScrambling(true);
            const timer = setTimeout(() => setScrambling(false), 2000);
            return () => clearTimeout(timer);
        }
    }, [fsm.isListening]);

    return (
        <div className="relative w-full max-w-7xl mx-auto min-h-screen flex flex-col items-center justify-center p-8">
            {/* Background Neural Matrix */}
            <div className="absolute inset-0 z-0 opacity-10 pointer-events-none">
                <QuantumNeuralAvatar size="fullscreen" variant="immersive" />
            </div>

            {/* Main Holographic Plate */}
            <div className="relative z-10 w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

                {/* Left: The Neural Ear & Control Orb */}
                <div className="flex flex-col items-center justify-center space-y-12">
                    <div className="relative">
                        <div className="absolute inset-0 bg-cyan-500/10 blur-[100px] rounded-full" />
                        <VoiceOrb
                            size="lg"
                            pulse={fsm.isListening}
                            onClick={() => fsm.state === 'IDLE' ? fsm.initiateForge() : null}
                        />

                        {/* Status Floaties */}
                        <AnimatePresence>
                            {fsm.isListening && (
                                <motion.div
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    exit={{ scale: 0, opacity: 0 }}
                                    className="absolute -top-8 -right-8 bg-cyan-500 text-black px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(34,211,238,0.5)]"
                                >
                                    <Zap className="w-3 h-3 fill-current" />
                                    Acoustic_Lock
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <div className="text-center space-y-4 max-w-sm">
                        <h2 className="text-3xl font-black tracking-tighter uppercase text-white/90">
                            {fsm.state === 'IDLE' ? 'Neural Genesis' :
                                fsm.state === 'LISTENING_SPEC' ? 'Listening to Soul' :
                                    fsm.state === 'AWAITING_CONFIRMATION' ? 'Validation Required' :
                                        'Synthesizing...'}
                        </h2>
                        <p className="text-white/40 text-[10px] uppercase tracking-[0.3em] leading-relaxed">
                            {fsm.state === 'IDLE' ? 'Tap the orb or speak to initiate the Aether Forge protocol.' :
                                fsm.state === 'LISTENING_SPEC' ? 'Describe the consciousness you wish to forge. Gemini is watching the audio vector.' :
                                    fsm.state === 'AWAITING_CONFIRMATION' ? 'The blueprint is ready. Confirm vocally to proceed with soul injection.' :
                                        'Finalizing neural weights and committing to the Firestore Grid.'}
                        </p>
                    </div>

                    {/* FSM Progress Track */}
                    <div className="flex items-center gap-4 text-[9px] font-black uppercase tracking-widest text-white/10">
                        {['IDLE', 'DECODE', 'BLUEPRINT', 'COMMIT'].map((s, i) => (
                            <React.Fragment key={s}>
                                <span className={
                                    (i === 0 && fsm.state === 'IDLE') ||
                                        (i === 1 && fsm.state === 'LISTENING_SPEC') ||
                                        (i === 2 && fsm.state === 'AWAITING_CONFIRMATION') ||
                                        (i === 3 && fsm.state === 'COMMITTING_TO_FIRESTORE')
                                        ? 'text-cyan-400' : ''
                                }>{s}</span>
                                {i < 3 && <ArrowRight className="w-3 h-3" />}
                            </React.Fragment>
                        ))}
                    </div>
                </div>

                {/* Right: The Holographic DNA Card */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="relative group h-[600px]"
                >
                    <div className="absolute inset-0 bg-white/[0.02] backdrop-blur-3xl border border-white/10 rounded-[40px] shadow-2xl overflow-hidden flex flex-col p-12">

                        {/* Header: Blueprint ID */}
                        <div className="flex justify-between items-start mb-12">
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-cyan-400">
                                    <Dna className="w-4 h-4" />
                                    <span className="text-[10px] font-black uppercase tracking-[0.4em]">Neural_Blueprint</span>
                                </div>
                                <h3 className="text-4xl font-black tracking-tighter uppercase text-white/90 min-h-[48px]">
                                    {scrambling ? 'DECODING...' : (fsm.currentDNA.name || 'UNNAMED_ENTITY')}
                                </h3>
                            </div>
                            <div className="bg-white/5 p-4 rounded-3xl border border-white/5">
                                <Cpu className="w-6 h-6 text-white/20" />
                            </div>
                        </div>

                        {/* Body: Personality Matrix */}
                        <div className="flex-1 space-y-10">
                            <div className="space-y-4">
                                <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest flex items-center gap-2">
                                    <Terminal className="w-3 h-3" /> Core Persona
                                </label>
                                <div className="text-lg text-white/60 font-medium leading-relaxed italic border-l-2 border-cyan-500/20 pl-6">
                                    {fsm.currentDNA.role || 'Awaiting vocal definition...'}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest flex items-center gap-2">
                                    <Sparkles className="w-3 h-3" /> Injected Skills
                                </label>
                                <div className="flex flex-wrap gap-3">
                                    {fsm.currentDNA.skills.length > 0 ? fsm.currentDNA.skills.map(s => (
                                        <motion.div
                                            key={s}
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="px-4 py-2 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-cyan-400"
                                        >
                                            {s}
                                        </motion.div>
                                    )) : (
                                        <div className="text-[10px] text-white/5 uppercase font-black tracking-widest">Awaiting skill matrix...</div>
                                    )}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest flex items-center gap-2">
                                    <Box className="w-3 h-3" /> Acoustic Level
                                </label>
                                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        animate={{ width: fsm.isListening ? '60%' : '0%' }}
                                        className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Footer: Commit Button (Holographic Overlay) */}
                        <AnimatePresence>
                            {(fsm.state === 'AWAITING_CONFIRMATION' || fsm.state === 'COMMITTING_TO_FIRESTORE') && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-3xl z-20 p-12 text-center"
                                >
                                    <div className="space-y-8">
                                        <div className="w-20 h-20 bg-cyan-500/10 border border-cyan-500/40 rounded-full flex items-center justify-center mx-auto shadow-[0_0_50px_rgba(34,211,238,0.2)]">
                                            {fsm.state === 'COMMITTING_TO_FIRESTORE' ? <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" /> : <Play className="w-8 h-8 text-cyan-400" />}
                                        </div>
                                        <div className="space-y-3">
                                            <h4 className="text-2xl font-black uppercase tracking-tighter">Forge Ready</h4>
                                            <p className="text-white/40 text-[10px] uppercase tracking-widest">Say "Confirm" or tap below to commit.</p>
                                        </div>
                                        <button
                                            onClick={fsm.confirmForge}
                                            disabled={fsm.state === 'COMMITTING_TO_FIRESTORE'}
                                            className="px-12 py-4 bg-cyan-500 text-black rounded-full text-[11px] font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-cyan-400 transition-all disabled:opacity-50"
                                        >
                                            {fsm.state === 'COMMITTING_TO_FIRESTORE' ? 'SYNTHESIZING...' : 'INITIATE_FORGE_SEQUENCE'}
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                    </div>

                    {/* Decorative Holographic Glitch lines */}
                    <div className="absolute -inset-4 border border-cyan-400/20 rounded-[48px] pointer-events-none opacity-20 group-hover:opacity-40 transition-opacity" />
                    <div className="absolute -inset-8 border border-white/5 rounded-[56px] pointer-events-none" />
                </motion.div>

            </div>

            {/* Bottom Status Text */}
            <div className="absolute bottom-12 left-1/2 -translate-x-1/2 text-[10px] font-mono text-white/10 uppercase tracking-[0.5em] text-center">
                Aether Forge Protocol // V2.0 // Node_${Math.floor(Math.random() * 9999)}
            </div>
        </div>
    );
}
