"use client";

import React, { useEffect, useState } from 'react';
import { motion, Variants } from 'framer-motion';
import { useAgentForgeFSM } from '@/hooks/useAgentForgeFSM';
import { useAetherStore } from '@/store/useAetherStore';
import QuantumNeuralAvatar from '../QuantumNeuralAvatar';

// Atomic Step Components
import ForgeStatus from './steps/ForgeStatus';
import ForgeIdentity from './steps/ForgeIdentity';
import ForgePersonality from './steps/ForgePersonality';
import ForgeConfirmation from './steps/ForgeConfirmation';

export default function ForgeWizard() {
    const fsm = useAgentForgeFSM();
    const transcriptStream = useAetherStore((s) => s.transcriptStream);
    const micLevel = useAetherStore((s) => s.micLevel);
    
    // Scrambling effect for the name field
    const [nameScramble, setNameScramble] = useState('');
    
    useEffect(() => {
        if (fsm.state === 'LISTENING_SPEC' && transcriptStream.interim) {
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
                <ForgeStatus 
                    state={fsm.state} 
                    micLevel={micLevel} 
                    isListening={fsm.isListening}
                    onInitiate={fsm.initiateForge}
                />

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

                        {/* Card Sections */}
                        <ForgeIdentity 
                            name={fsm.currentDNA.name} 
                            scramble={nameScramble} 
                            variants={fieldVariants} 
                        />
                        
                        <ForgePersonality 
                            dna={fsm.currentDNA} 
                            micLevel={micLevel} 
                            variants={fieldVariants} 
                        />

                        {/* Overlay Actions */}
                        <ForgeConfirmation 
                            state={fsm.state} 
                            onConfirm={fsm.confirmForge} 
                        />

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
