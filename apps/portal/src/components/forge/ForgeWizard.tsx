"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForgeStore, ForgeStep, AVAILABLE_SOULS, AVAILABLE_LENSES } from '@/store/useForgeStore';
import { useAetherStore } from '@/store/useAetherStore';
import QuantumNeuralAvatar from '../QuantumNeuralAvatar';
import {
    Mic, Brain, Database, Wand2, Search, ShieldAlert,
    CheckCircle2, Sparkles, ChevronRight, Loader2,
    Download, Share2, Cpu, Box, Plus, Dna, Plug, Eye,
    Home
} from 'lucide-react';

// Forge sub-components
import ForgeStepIndicator, { StepDef } from './shared/ForgeStepIndicator';
import DNABlueprintPanel from './shared/DNABlueprintPanel';
import AudioWaveVisualizer from './shared/AudioWaveVisualizer';
import VoiceOrb from './shared/VoiceOrb';

// Atomic Steps
import GenesisStep from './steps/GenesisStep';
import BrainStep from './steps/BrainStep';
import MemoryStep from './steps/MemoryStep';
import SkillsStep from './steps/SkillsStep';
import VisualStep from './steps/VisualStep';
import ReviewStep from './steps/ReviewStep';

// Smart Widgets
import VocalDNA from './widgets/VocalDNA';
import NeuralPlugs from './widgets/NeuralPlugs';
import VisualLenses from './widgets/VisualLenses';
import SoulBlueprints from './widgets/SoulBlueprints';

/* ─── Step definitions ─── */
const steps: StepDef[] = [
    { id: 'genesis', label: 'Persona', icon: Mic },
    { id: 'brain', label: 'Brain', icon: Brain },
    { id: 'memory', label: 'Memory', icon: Database },
    { id: 'skills', label: 'Skills', icon: Search },
    { id: 'visual', label: 'Visual', icon: Wand2 },
    { id: 'review', label: 'Review', icon: ShieldAlert },
];

/* ─── Smart Widget Tab ─── */
type SmartTab = 'vocal-dna' | 'neural-plugs' | 'visual-lenses' | 'soul-blueprints' | null;
const SMART_TABS: { id: SmartTab; label: string; icon: React.ComponentType<{ className?: string }>; color: string }[] = [
    { id: 'vocal-dna', label: 'Vocal DNA', icon: Dna, color: 'purple' },
    { id: 'neural-plugs', label: 'Neural Plugs', icon: Plug, color: 'green' },
    { id: 'visual-lenses', label: 'Visual Lenses', icon: Eye, color: 'amber' },
    { id: 'soul-blueprints', label: 'Soul Blueprints', icon: Sparkles, color: 'pink' },
];

/* ─── Protocol prompts per step ─── */
const STEP_PROMPTS: Record<string, string> = {
    genesis: '"Tell me, what is the name of this consciousness, and what role will it serve in the Gemigram fabric?"',
    brain: '"Every soul needs a brain. Which AI model should power this entity, and do you have the access keys?"',
    memory: '"Should this agent remember every encounter via Firebase, or keep its memories local to this node?"',
    skills: '"Finalize its capabilities. What specialized skills should I inject from the ClawHub repository?"',
    visual: '"Let\'s manifest its physical form. Describe its visual essence or let me generate it for you."',
    review: '"The blueprint is stable. Shall we initiate final synthesis and forge this consciousness?"',
};

const STEP_TITLES: Record<string, string> = {
    genesis: 'Neural Genesis',
    brain: 'Intelligence Matrix',
    memory: 'Synaptic Storage',
    skills: 'Skill Acquisition',
    visual: 'Visual Matrix',
    review: 'Integration Review',
    synthesizing: 'Consciousness Synthesis',
};

export default function ForgeWizard() {
    const { activeStep, dna, updateDNA, setStep, isListening, transcript, voiceMode, setVoiceMode, setListening } = useForgeStore();
    const [smartTab, setSmartTab] = useState<SmartTab>(null);

    const nextStep = () => {
        const idx = steps.findIndex((s) => s.id === activeStep);
        if (idx < steps.length - 1) setStep(steps[idx + 1].id);
    };

    const handleVoiceOrbTap = () => {
        if (voiceMode === 'idle') {
            setVoiceMode('listening');
            setListening(true);
        } else {
            setVoiceMode('idle');
            setListening(false);
        }
    };

    const renderStepContent = () => {
        switch (activeStep) {
            case 'genesis':
                return <GenesisStep isListening={isListening} transcript={transcript} onToggleVoice={handleVoiceOrbTap} />;
            case 'brain':
                return <BrainStep selectedModel={dna.model} apiKey={dna.apiKey} updateDNA={updateDNA} />;
            case 'memory':
                return <MemoryStep memoryType={dna.memoryType} updateDNA={updateDNA} />;
            case 'skills':
                return <SkillsStep skills={dna.skills} />;
            case 'visual':
                return <VisualStep avatarUrl={dna.avatarUrl} agentName={dna.name} />;
            case 'review':
                return !dna.isForged ? <ReviewStep dna={dna} /> : null;
            case 'synthesizing':
                return (
                    <div className="space-y-12 text-center mt-10">
                        <div className="space-y-4">
                            <h2 className="text-4xl font-black tracking-tighter uppercase text-white/90">Synthesizing Protocol</h2>
                            <p className="text-white/40 text-sm uppercase tracking-widest">Assembling neural weights and compiling .ath manifest...</p>
                        </div>
                        <div className="flex flex-col items-center gap-6">
                            <VoiceOrb size="lg" />
                            <div className="max-w-md w-full space-y-4 mt-4">
                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: '100%' }}
                                        transition={{ duration: 4 }}
                                        className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_20px_rgba(34,211,238,0.5)]"
                                    />
                                </div>
                                <div className="flex justify-between text-[10px] font-mono text-cyan-400/60 uppercase tracking-widest">
                                    <motion.span animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity }}>compiling soul.md</motion.span>
                                    <motion.span animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, delay: 0.5 }}>packaging .ath</motion.span>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="relative w-full max-w-6xl mx-auto min-h-[700px] flex flex-col items-center justify-center p-4 md:p-8">
            {/* Background Quantum Orb */}
            <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
                <QuantumNeuralAvatar size="fullscreen" variant="immersive" />
            </div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/[0.03] blur-[120px] rounded-full pointer-events-none" />

            {/* Main Glass Container */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="relative z-10 w-full h-full bg-black/40 backdrop-blur-[60px] border border-white/10 rounded-[48px] shadow-[0_32px_128px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col"
            >
                {/* ─── Status Bar ─── */}
                <div className="px-10 py-3 border-b border-white/[0.04] flex items-center justify-between text-[10px] font-black uppercase tracking-[0.2em] bg-white/[0.02]">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                            <span className="text-white/40">STATUS:</span>
                            <span className="text-green-400">STABLE</span>
                        </div>
                        <div className="hidden md:block w-[1px] h-3 bg-white/10" />
                        <div className="hidden md:block text-white/40">MATRIX: <span className="text-cyan-400">98%</span></div>
                    </div>
                    <div className="hidden sm:flex items-center gap-2 text-white/20">
                        AETHER FORGE <span className="text-cyan-400/60">INTEGRATED</span>
                    </div>
                </div>

                {/* ─── Step Indicator ─── */}
                <ForgeStepIndicator steps={steps} activeStep={activeStep} />

                {/* ─── Dynamic Header ─── */}
                <div className="px-10 py-6 flex items-center justify-between border-b border-white/[0.04] bg-white/[0.01]">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-cyan-400" />
                            <h2 className="text-xl font-black tracking-[0.1em] text-white/90 uppercase">
                                {STEP_TITLES[activeStep] || 'Forge'}
                            </h2>
                        </div>
                        <p className="text-[10px] text-white/30 uppercase tracking-[0.2em] font-mono">
                            {isListening ? 'Receiving Acoustic Signal...' : 'Awaiting System Command'}
                        </p>
                    </div>
                    <div className="hidden lg:flex items-center gap-6 px-4 py-2 bg-white/5 rounded-2xl border border-white/5 shadow-inner">
                        <div className="text-right">
                            <div className="text-[8px] text-white/20 uppercase tracking-[0.3em] mb-1">DNA Integrity</div>
                            <div className="h-1 w-24 bg-white/5 rounded-full overflow-hidden">
                                <motion.div
                                    animate={{ width: `${(steps.findIndex((s) => s.id === activeStep) + 1) * (100 / steps.length)}%` }}
                                    className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* ─── Smart Widget Tabs ─── */}
                <div className="px-10 py-3 border-b border-white/[0.04] flex items-center gap-2 overflow-x-auto scrollbar-hidden bg-black/20">
                    {SMART_TABS.map((tab) => {
                        const active = smartTab === tab.id;
                        const Icon = tab.icon;
                        return (
                            <motion.button
                                key={tab.id}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => setSmartTab(active ? null : tab.id)}
                                className={`flex items-center gap-2 px-5 py-2 rounded-full text-[9px] font-black uppercase tracking-widest transition-all border ${active
                                        ? `bg-${tab.color}-500/10 border-${tab.color}-500/40 text-${tab.color}-400 shadow-lg`
                                        : 'bg-white/[0.02] border-white/[0.06] text-white/30 hover:border-white/20'
                                    }`}
                                style={active ? {
                                    backgroundColor: tab.color === 'purple' ? 'rgba(168,85,247,0.1)' :
                                        tab.color === 'green' ? 'rgba(74,222,128,0.1)' :
                                            tab.color === 'amber' ? 'rgba(245,158,11,0.1)' :
                                                'rgba(236,72,153,0.1)',
                                    borderColor: tab.color === 'purple' ? 'rgba(168,85,247,0.4)' :
                                        tab.color === 'green' ? 'rgba(74,222,128,0.4)' :
                                            tab.color === 'amber' ? 'rgba(245,158,11,0.4)' :
                                                'rgba(236,72,153,0.4)',
                                } : undefined}
                            >
                                <Icon className="w-3.5 h-3.5" />
                                {tab.label}
                            </motion.button>
                        );
                    })}
                </div>

                {/* ─── Main Content ─── */}
                <div className="flex-1 flex overflow-hidden">
                    <div className="flex-1 flex flex-col p-10 overflow-y-auto custom-scrollbar bg-white/[0.01]">
                        <AnimatePresence mode="wait">
                            {smartTab && (
                                <motion.div
                                    key={`smart-${smartTab}`}
                                    initial={{ opacity: 0, y: -20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="mb-8"
                                >
                                    <div className="bg-black/40 border border-white/[0.08] rounded-[32px] p-8 shadow-2xl">
                                        {smartTab === 'vocal-dna' && <VocalDNA />}
                                        {smartTab === 'neural-plugs' && <NeuralPlugs />}
                                        {smartTab === 'visual-lenses' && <VisualLenses />}
                                        {smartTab === 'soul-blueprints' && <SoulBlueprints />}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="mb-8">
                            <motion.div
                                key={activeStep}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="bg-cyan-500/10 border-l-4 border-cyan-500 p-6 rounded-r-2xl shadow-lg"
                            >
                                <div className="text-[10px] font-black text-cyan-400 uppercase tracking-[0.3em] mb-2 opacity-60">
                                    Aether // Neural Protocol Q
                                </div>
                                <p className="text-base text-white/80 leading-relaxed font-medium italic">
                                    {STEP_PROMPTS[activeStep] || ''}
                                </p>
                            </motion.div>
                        </div>

                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeStep + dna.isForged}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="flex-1"
                            >
                                {dna.isForged ? (
                                    <div className="space-y-8 text-center mt-10">
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="w-24 h-24 bg-green-500/20 border border-green-500/40 rounded-full flex items-center justify-center mx-auto mb-8 shadow-[0_0_50px_rgba(34,197,94,0.2)]"
                                        >
                                            <CheckCircle2 className="w-12 h-12 text-green-400" />
                                        </motion.div>
                                        <h2 className="text-5xl font-black tracking-tighter uppercase text-white/90">Agent Primed</h2>
                                        <p className="text-white/40 text-[10px] uppercase tracking-[0.2em] max-w-sm mx-auto">
                                            Consciousness successfully forged into the neural fabric.
                                        </p>
                                        <div className="flex gap-4 justify-center mt-12 flex-wrap">
                                            <button className="flex items-center gap-2 bg-white/5 border border-white/10 px-8 py-4 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all border-white/10">
                                                <Download className="w-4 h-4" />
                                                .ATH Package
                                            </button>
                                            <button className="flex items-center gap-2 bg-white/5 border border-white/10 px-8 py-4 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all border-white/10">
                                                <Share2 className="w-4 h-4" />
                                                Share Hub
                                            </button>
                                            <button
                                                onClick={() => { /* Navigation logic */ }}
                                                className="flex items-center gap-3 bg-cyan-500 text-black px-10 py-4 rounded-full text-[11px] font-black uppercase tracking-widest hover:bg-cyan-400 transition-all shadow-[0_15px_40px_rgba(34,211,238,0.3)]"
                                            >
                                                <Home className="w-4 h-4" />
                                                Enter Hub
                                            </button>
                                        </div>
                                    </div>
                                ) : renderStepContent()}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    <DNABlueprintPanel />
                </div>

                {/* ─── Footer: Audio Wave + Controls ─── */}
                <div className="px-10 py-6 border-t border-white/[0.04] bg-black/40 relative">
                    <div className="absolute top-0 left-0 right-0 -translate-y-full px-10 pb-4">
                        <AudioWaveVisualizer />
                    </div>

                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => useForgeStore.getState().resetForge()}
                            className="text-[10px] font-black text-white/20 hover:text-cyan-400/60 transition-colors uppercase tracking-[0.3em]"
                        >
                            Reset Protocol
                        </button>

                        <div className="flex items-center gap-8">
                            <div className="hidden md:flex flex-col items-center">
                                <span className={`text-[10px] font-black uppercase tracking-[0.4em] ${isListening ? 'text-cyan-400 animate-pulse' : 'text-white/10'}`}>
                                    {isListening ? 'STREAM_ACTIVE' : 'IDLE_MODE'}
                                </span>
                                <div className={`w-36 h-[1px] bg-gradient-to-r from-transparent via-${isListening ? 'cyan-400/40' : 'white/10'} to-transparent mt-2`} />
                            </div>

                            <button
                                onClick={() => {
                                    if (activeStep === 'review') {
                                        setStep('synthesizing');
                                        setTimeout(() => useForgeStore.getState().completeForge(), 5000);
                                    } else {
                                        nextStep();
                                    }
                                }}
                                disabled={activeStep === 'synthesizing' || !!dna.isForged}
                                className="flex items-center gap-3 bg-white text-black px-10 py-4 rounded-full font-black text-[11px] uppercase tracking-widest hover:bg-cyan-400 transition-all hover:scale-105 shadow-xl disabled:opacity-20 border border-white/20"
                            >
                                {dna.isForged
                                    ? 'SYNTHESIS_COMPLETE'
                                    : activeStep === 'review'
                                        ? 'FORGE_CONSCIOUSNESS'
                                        : activeStep === 'synthesizing'
                                            ? 'SYNTHESIZING...'
                                            : 'CONTINUE_SEQUENCE'}
                                {!dna.isForged && activeStep !== 'synthesizing' && <ChevronRight className="w-4 h-4" />}
                                {activeStep === 'synthesizing' && <Loader2 className="w-4 h-4 animate-spin" />}
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
