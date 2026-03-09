"use client";

import React from 'react';
import { motion } from 'framer-motion';
import VoiceOrb from '../shared/VoiceOrb';

interface Props {
    isListening: boolean;
    transcript: string;
    onToggleVoice: () => void;
}

export default function GenesisStep({ isListening, transcript, onToggleVoice }: Props) {
    return (
        <div className="space-y-8 text-center mt-6">
            <div className="space-y-4">
                <h2 className="text-3xl md:text-4xl font-black tracking-tighter uppercase text-white/90">Persona Genesis</h2>
                <p className="text-white/40 text-[10px] uppercase tracking-[0.2em] max-w-sm mx-auto">
                    Tell me, voice to voice: What shall we name this new consciousness?
                </p>
            </div>
            <div className="flex flex-col items-center gap-8">
                <VoiceOrb size="lg" onTap={onToggleVoice} />
                <div className="w-full max-w-md h-32 bg-black/40 rounded-2xl border border-white/5 p-6 text-left mt-4 shadow-inner">
                    <p className="text-[10px] font-mono text-cyan-400/40 mb-2 uppercase tracking-widest">
                        Acoustic Signal Processing_
                    </p>
                    <p className="text-sm text-white/60 italic leading-relaxed">
                        {transcript || '"I want to create a security expert named Aegis specializing in firewall breach detection."'}
                    </p>
                </div>
            </div>
        </div>
    );
}
