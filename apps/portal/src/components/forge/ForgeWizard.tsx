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

// Smart Widgets
import VocalDNA from './widgets/VocalDNA';
import NeuralPlugs from './widgets/NeuralPlugs';
import VisualLenses from './widgets/VisualLenses';
import SoulBlueprints from './widgets/SoulBlueprints';
import ClawHubWidget from './widgets/ClawHubWidget';

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

    const goToDashboard = () => {
        // useAetherStore.getState().setActiveHubView?.(.discovery.);
    };

    return (
        <div className="relative w-full max-w-6xl mx-auto min-h-[700px] flex flex-col items-center justify-center p-4 md:p-8">
            {/* Background Quantum Orb */}
            <div className="absolute inset-0 z-0 opacity-30 pointer-events-none">
                <QuantumNeuralAvatar size="fullscreen" variant="immersive" />
            </div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/5 blur-[120px] rounded-full pointer-events-none" />

            {/* Main Glass Container */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="relative z-10 w-full h-full bg-white/[0.01] backdrop-blur-[40px] border border-white/10 rounded-[36px] md:rounded-[48px] shadow-[0_32px_128px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col"
            >
                {/* Inner glow border */}
                <div className="absolute inset-0 rounded-[36px] md:rounded-[48px] border border-white/5 pointer-events-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]" />

                {/* ─── Status Bar ─── */}
                <div className="px-6 md:px-10 py-3 border-b border-white/[0.04] flex items-center justify-between text-[10px] font-black uppercase tracking-[0.2em]">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-white/40">STATUS:</span>
                            <span className="text-green-400">STABLE</span>
                        </div>
                        <div className="hidden md:block w-[1px] h-3 bg-white/10" />
                        <div className="hidden md:block text-white/40">MATRIX: <span className="text-cyan-400">98%</span></div>
                    </div>
                    <div className="hidden sm:flex items-center gap-2 text-white/20">
                        AETHER FORGE <span className="text-cyan-400/60">ACTIVE</span>
                    </div>
                </div>

                {/* ─── Step Indicator ─── */}
                <ForgeStepIndicator steps={steps} activeStep={activeStep} />

                {/* ─── Dynamic Header ─── */}
                <div className="px-6 md:px-10 py-4 flex items-center justify-between border-b border-white/[0.04]">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-cyan-400" />
                            <h2 className="text-lg md:text-xl font-bold tracking-tight text-white/90 uppercase">
                                {STEP_TITLES[activeStep] || 'Forge'}
                            </h2>
                        </div>
                        <p className="text-[10px] text-white/30 uppercase tracking-[0.2em]">
                            {isListening ? 'Listening to your voice...' : 'Awaiting initialization command'}
                        </p>
                    </div>
                    <div className="hidden lg:flex items-center gap-6 px-4 py-2 bg-white/5 rounded-2xl border border-white/5">
                        <div className="text-right">
                            <div className="text-[8px] text-white/20 uppercase tracking-[0.2em] mb-1">DNA Integrity</div>
                            <div className="h-1 w-24 bg-white/5 rounded-full overflow-hidden">
                                <motion.div
                                    animate={{ width: `${(steps.findIndex((s) => s.id === activeStep) + 1) * (100 / steps.length)}%` }}
                                    className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* ─── Smart Widget Tabs (Floating Orbs) ─── */}
                <div className="px-6 md:px-10 py-3 border-b border-white/[0.04] flex items-center gap-2 overflow-x-auto scrollbar-hidden">
                    {SMART_TABS.map((tab) => {
                        const active = smartTab === tab.id;
                        const Icon = tab.icon;
                        return (
                            <motion.button
                                key={tab.id}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => setSmartTab(active ? null : tab.id)}
                                className={`flex items-center gap-2 px-4 py-2 rounded-full text-[9px] font-black uppercase tracking-widest whitespace-nowrap transition-all border ${
                                    active
                                        ? `bg-${tab.color}-500/10 border-${tab.color}-500/30 text-${tab.color}-400 shadow-[0_0_12px_rgba(168,85,247,0.15)]`
                                        : 'bg-white/[0.02] border-white/[0.06] text-white/30 hover:text-white/50 hover:border-white/10'
                                }`}
                                style={active ? {
                                    backgroundColor: tab.color === 'purple' ? 'rgba(168,85,247,0.1)' :
                                        tab.color === 'green' ? 'rgba(74,222,128,0.1)' :
                                        tab.color === 'amber' ? 'rgba(245,158,11,0.1)' :
                                        'rgba(236,72,153,0.1)',
                                    borderColor: tab.color === 'purple' ? 'rgba(168,85,247,0.3)' :
                                        tab.color === 'green' ? 'rgba(74,222,128,0.3)' :
                                        tab.color === 'amber' ? 'rgba(245,158,11,0.3)' :
                                        'rgba(236,72,153,0.3)',
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
                    {/* Interaction Zone */}
                    <div className="flex-1 flex flex-col p-6 md:p-10 overflow-y-auto custom-scrollbar">
                        {/* Smart Widget Panel (slides in) */}
                        <AnimatePresence mode="wait">
                            {smartTab && (
                                <motion.div
                                    key={`smart-${smartTab}`}
                                    initial={{ opacity: 0, y: -10, height: 0 }}
                                    animate={{ opacity: 1, y: 0, height: 'auto' }}
                                    exit={{ opacity: 0, y: -10, height: 0 }}
                                    transition={{ duration: 0.3 }}
                                    className="mb-6 overflow-hidden"
                                >
                                    <div className="bg-white/[0.01] border border-white/[0.06] rounded-3xl p-6">
                                        {smartTab === 'vocal-dna' && <VocalDNA />}
                                        {smartTab === 'neural-plugs' && <NeuralPlugs />}
                                        {smartTab === 'visual-lenses' && <VisualLenses />}
                                        {smartTab === 'soul-blueprints' && <SoulBlueprints />}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Protocol Prompt */}
                        <div className="mb-6">
                            <motion.div
                                key={activeStep}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="bg-cyan-500/10 border-l-2 border-cyan-500 p-4 rounded-r-xl"
                            >
                                <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
                                    Aether Assistant // Protocol Q
                                </div>
                                <p className="text-sm text-white/80 leading-relaxed font-medium italic">
                                    {STEP_PROMPTS[activeStep] || ''}
                                </p>
                            </motion.div>
                        </div>

                        {/* Step Content */}
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeStep}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="flex-1 flex flex-col"
                            >
                                {/* ── Step 1: Genesis ── */}
                                {activeStep === 'genesis' && (
                                    <div className="space-y-8 text-center mt-6">
                                        <div className="space-y-4">
                                            <h2 className="text-3xl md:text-4xl font-black tracking-tighter">Persona Genesis</h2>
                                            <p className="text-white/40 text-sm max-w-sm mx-auto">
                                                Tell me, voice to voice: What shall we name this new consciousness?
                                            </p>
                                        </div>
                                        <div className="flex flex-col items-center gap-8">
                                            <VoiceOrb size="lg" onTap={handleVoiceOrbTap} />
                                            <div className="w-full max-w-md h-32 bg-black/40 rounded-2xl border border-white/5 p-6 text-left mt-4">
                                                <p className="text-[10px] font-mono text-cyan-400/40 mb-2 uppercase tracking-widest">
                                                    Acoustic Signal Processing_
                                                </p>
                                                <p className="text-sm text-white/60 italic">
                                                    {transcript || '"I want to create a security expert named Aegis specializing in firewall breach detection."'}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* ── Step 2: Brain ── */}
                                {activeStep === 'brain' && (
                                    <div className="space-y-8">
                                        <h2 className="text-3xl font-black tracking-tighter">Brain Selection</h2>
                                        <div className="grid grid-cols-2 gap-4">
                                            {['Google Gemini 2.5', 'OpenAI GPT-4o', 'Anthropic Claude 3.5', 'Local Llama 3'].map((brain) => (
                                                <button
                                                    key={brain}
                                                    onClick={() => updateDNA({ model: brain })}
                                                    className={`p-6 rounded-3xl border text-left transition-all ${
                                                        dna.model === brain
                                                            ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400'
                                                            : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                                                    }`}
                                                >
                                                    <Cpu className="w-6 h-6 mb-4" />
                                                    <div className="font-bold">{brain}</div>
                                                    <div className="text-[10px] opacity-60">High-Performance Neural Backbone</div>
                                                </button>
                                            ))}
                                        </div>
                                        <div className="space-y-4">
                                            <label className="text-xs font-bold text-white/30 uppercase tracking-widest">
                                                Secure API Key Entry
                                            </label>
                                            <input
                                                type="password"
                                                placeholder="Paste Key Here..."
                                                value={dna.apiKey}
                                                onChange={(e) => updateDNA({ apiKey: e.target.value })}
                                                className="w-full bg-black/40 border border-white/10 rounded-2xl py-4 px-6 focus:border-cyan-500/50 focus:outline-none transition-all text-white/80"
                                            />
                                        </div>
                                    </div>
                                )}

                                {/* ── Step 3: Memory ── */}
                                {activeStep === 'memory' && (
                                    <div className="space-y-8 text-center mt-10">
                                        <h2 className="text-3xl font-black tracking-tighter">Memory Storage</h2>
                                        <div className="flex justify-center gap-6">
                                            {[
                                                { id: 'firebase' as const, label: 'Cloud Sync (Firebase)', icon: Database, desc: 'Sub-100ms cross-device recall' },
                                                { id: 'local' as const, label: 'Local Core', icon: Box, desc: 'Privacy-focused on-device storage' },
                                            ].map((mem) => (
                                                <button
                                                    key={mem.id}
                                                    onClick={() => updateDNA({ memoryType: mem.id })}
                                                    className={`w-48 p-6 rounded-[32px] border transition-all flex flex-col items-center gap-4 ${
                                                        dna.memoryType === mem.id
                                                            ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400'
                                                            : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                                                    }`}
                                                >
                                                    <div className={`p-4 rounded-2xl ${dna.memoryType === mem.id ? 'bg-cyan-500/20' : 'bg-white/5'}`}>
                                                        <mem.icon className="w-8 h-8" />
                                                    </div>
                                                    <div className="space-y-1">
                                                        <div className="font-bold text-xs">{mem.label}</div>
                                                        <div className="text-[9px] opacity-60 leading-tight">{mem.desc}</div>
                                                    </div>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* ── Step 4: Skills ── */}
                                {activeStep === 'skills' && (
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between">
                                            <h2 className="text-3xl font-black tracking-tighter">Skill Acquisition</h2>
                                            <div className="flex items-center gap-2">
                                                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                                                <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.15em]">
                                                    ClawHub Connected
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-xs text-white/40 leading-relaxed">
                                            Inject specialized capabilities from the ClawHub skill repository.
                                        </p>
                                        <ClawHubWidget />
                                        {dna.skills.length > 0 && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                className="bg-cyan-500/[0.05] border border-cyan-500/20 rounded-2xl p-4"
                                            >
                                                <div className="text-[9px] font-mono text-cyan-400/60 uppercase tracking-widest mb-2">
                                                    Injected Neural Payload
                                                </div>
                                                <div className="flex flex-wrap gap-1.5">
                                                    {dna.skills.map((s) => (
                                                        <span key={s} className="px-2.5 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-[9px] font-bold text-cyan-300 uppercase tracking-wider">
                                                            {s}
                                                        </span>
                                                    ))}
                                                </div>
                                            </motion.div>
                                        )}
                                    </div>
                                )}

                                {/* ── Step 5: Visual ── */}
                                {activeStep === 'visual' && (
                                    <div className="space-y-8 text-center mt-10">
                                        <h2 className="text-3xl font-black tracking-tighter">Visual Identity</h2>
                                        <p className="text-xs text-white/40 max-w-sm mx-auto italic">
                                            Synthesizing a unique neural avatar for {dna.name || 'your agent'}...
                                        </p>
                                        <div className="relative w-48 h-48 mx-auto">
                                            <motion.div
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                                                className="absolute inset-0 border-2 border-dashed border-cyan-500/30 rounded-full"
                                            />
                                            <div className="absolute inset-4 rounded-full bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden border border-white/10">
                                                {dna.avatarUrl ? (
                                                    <img src={dna.avatarUrl} className="w-full h-full object-cover" alt="Avatar" />
                                                ) : (
                                                    <Sparkles className="w-12 h-12 text-cyan-400 animate-pulse" />
                                                )}
                                            </div>
                                        </div>
                                        <button className="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-cyan-500/20 transition-all">
                                            Generate Agent Avatar
                                        </button>
                                    </div>
                                )}

                                {/* ── Step 6: Review ── */}
                                {activeStep === 'review' && !dna.isForged && (
                                    <div className="space-y-6">
                                        <h2 className="text-3xl font-black tracking-tighter">Neural Review</h2>
                                        <div className="bg-black/30 rounded-3xl p-6 border border-white/5 space-y-4">
                                            {[
                                                { label: 'Agent Core', value: `${dna.name || '---'} (${dna.role || '---'})`, color: 'text-cyan-400' },
                                                { label: 'Neural Backbone', value: dna.model, color: 'text-white/80' },
                                                { label: 'Memory Storage', value: `${dna.memoryType.toUpperCase()} SYNC`, color: 'text-green-400' },
                                                { label: 'Skill Payload', value: `${dna.skills.length} SKILLS LOADED`, color: 'text-purple-400' },
                                                { label: 'Voice Resonator', value: dna.vocalDNA.voiceId || 'Default', color: 'text-purple-300' },
                                                { label: 'Neural Plugs', value: `${dna.neuralPlugs.length} CONNECTED`, color: 'text-green-300' },
                                                { label: 'Visual Lens', value: AVAILABLE_LENSES.find((l) => l.id === dna.selectedLens)?.name || 'None', color: 'text-amber-400' },
                                                { label: 'Soul Blueprint', value: AVAILABLE_SOULS.find((s) => s.id === dna.selectedSoul)?.name || 'None', color: 'text-pink-400' },
                                            ].map((row, i, arr) => (
                                                <div key={row.label} className={`flex justify-between items-center ${i < arr.length - 1 ? 'border-b border-white/5 pb-3' : ''}`}>
                                                    <span className="text-[10px] font-mono text-white/30 uppercase">{row.label}</span>
                                                    <span className={`text-sm font-bold ${row.color}`}>{row.value}</span>
                                                </div>
                                            ))}
                                        </div>
                                        <p className="text-[10px] text-white/40 text-center italic">
                                            Finalizing will commit the agent&apos;s DNA to the Gemigram Neural Fabric.
                                        </p>
                                    </div>
                                )}

                                {/* ── Synthesizing ── */}
                                {activeStep === 'synthesizing' && (
                                    <div className="space-y-12 text-center mt-10">
                                        <div className="space-y-4">
                                            <h2 className="text-4xl font-black tracking-tighter">Synthesizing Protocol</h2>
                                            <p className="text-white/40 text-sm">Assembling neural weights and compiling .ath manifest...</p>
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
                                )}

                                {/* ── Success State ── */}
                                {dna.isForged && (
                                    <div className="space-y-8 text-center mt-10">
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                                            className="w-20 h-20 bg-green-500/20 border border-green-500/40 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(34,197,94,0.3)]"
                                        >
                                            <CheckCircle2 className="w-10 h-10 text-green-400" />
                                        </motion.div>
                                        <h2 className="text-4xl font-black tracking-tighter">Agent Primed</h2>
                                        <p className="text-white/40 text-sm max-w-sm mx-auto">
                                            Consciousness successfully forged. Your agent is now live on the Gemigram Platform.
                                        </p>
                                        <div className="flex gap-4 justify-center mt-8 flex-wrap">
                                            <button className="flex items-center gap-2 bg-white/5 border border-white/10 px-6 py-3 rounded-full text-xs font-bold hover:bg-white/10 transition-all">
                                                <Download className="w-4 h-4" />
                                                .ath Package
                                            </button>
                                            <button className="flex items-center gap-2 bg-white/5 border border-white/10 px-6 py-3 rounded-full text-xs font-bold hover:bg-white/10 transition-all">
                                                <Share2 className="w-4 h-4" />
                                                Share to Hub
                                            </button>
                                            <button
                                                onClick={goToDashboard}
                                                className="flex items-center gap-2 bg-cyan-500 text-black px-6 py-3 rounded-full text-xs font-black hover:bg-cyan-400 transition-all shadow-[0_8px_24px_rgba(34,211,238,0.3)]"
                                            >
                                                <Home className="w-4 h-4" />
                                                Enter Workspace
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* ─── Blueprint Side Panel ─── */}
                    <DNABlueprintPanel />
                </div>

                {/* ─── Footer: Audio Wave + Controls ─── */}
                <div className="px-6 md:px-10 py-5 border-t border-white/[0.04] bg-black/20 relative">
                    <div className="absolute top-0 left-0 right-0 -translate-y-full px-6 md:px-10 pb-3">
                        <AudioWaveVisualizer />
                    </div>

                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => useForgeStore.getState().resetForge()}
                            className="text-[10px] font-bold text-white/20 hover:text-white/40 transition-colors uppercase tracking-[0.2em]"
                        >
                            Reset Protocol
                        </button>

                        <div className="flex items-center gap-6">
                            <div className="hidden md:flex flex-col items-center">
                                <span className="text-[10px] font-black text-white/10 uppercase tracking-[0.3em]">
                                    {isListening ? 'Receiving Bio-Signal' : 'Awaiting Input'}
                                </span>
                                <div className="w-32 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent mt-1" />
                            </div>

                            <button
                                onClick={() => {
                                    if (activeStep === 'review') {
                                        setStep('synthesizing');
                                        setTimeout(() => {
                                            useForgeStore.getState().completeForge();
                                        }, 5000);
                                    } else {
                                        nextStep();
                                    }
                                }}
                                disabled={activeStep === 'synthesizing' || !!dna.isForged}
                                className="flex items-center gap-2 bg-white text-black px-8 py-3 rounded-full font-black text-xs hover:bg-cyan-400 transition-all hover:scale-105 active:scale-95 shadow-[0_8px_24px_rgba(255,255,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed border border-white/20"
                            >
                                {dna.isForged
                                    ? 'CONSCIOUSNESS PRIMED'
                                    : activeStep === 'review'
                                        ? 'FORGE CONSCIOUSNESS'
                                        : activeStep === 'synthesizing'
                                            ? 'SYNTHESIZING...'
                                            : 'NEXT SEQUENCE'}
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
