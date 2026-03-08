"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForgeStore, ForgeStep } from '@/store/useForgeStore';
import QuantumNeuralAvatar from '../QuantumNeuralAvatar';
import { useAetherStore } from '@/store/useAetherStore';
import {
    Mic,
    Brain,
    Database,
    Wand2,
    Plus,
    Loader2,
    Download,
    Share2,
    Cpu,
    ExternalLink,
    Box,
    Search,
    ShieldAlert,
    CheckCircle2,
    Sparkles,
    ChevronRight
} from 'lucide-react';

const steps: { id: ForgeStep; label: string; icon: any }[] = [
    { id: 'genesis', label: 'Persona', icon: Mic },
    { id: 'brain', label: 'Brain', icon: Brain },
    { id: 'memory', label: 'Memory', icon: Database },
    { id: 'skills', label: 'Skills', icon: Search },
    { id: 'visual', label: 'Visual', icon: Wand2 },
    { id: 'review', label: 'Review', icon: ShieldAlert },
];

export default function ForgeWizard() {
    const { activeStep, dna, updateDNA, setStep, isListening, transcript } = useForgeStore();
    const engineState = useAetherStore((s) => s.engineState);
    const micLevel = useAetherStore((s) => s.micLevel);
    const [inputValue, setInputValue] = useState('');

    const nextStep = () => {
        const currentIndex = steps.findIndex(s => s.id === activeStep);
        if (currentIndex < steps.length - 1) {
            setStep(steps[currentIndex + 1].id);
        }
    };

    return (
        <div className="relative w-full max-w-5xl mx-auto h-[700px] flex flex-col items-center justify-center p-8">
            {/* Background Quantum Orb - The "Good Stuff" */}
            <div className="absolute inset-0 z-0 opacity-40 pointer-events-none">
                <QuantumNeuralAvatar size="fullscreen" variant="immersive" />
            </div>

            {/* Background Glows */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/5 blur-[120px] rounded-full pointer-events-none" />

            {/* Main Glass Container - iOS Inspired */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="relative z-10 w-full h-full bg-white/[0.01] backdrop-blur-[40px] border border-white/10 rounded-[48px] shadow-[0_32px_128px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col"
            >
                {/* Subtle Inner Glow Border */}
                <div className="absolute inset-0 rounded-[48px] border border-white/5 pointer-events-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]" />

                {/* Top Status Bar from Mockup */}
                <div className="px-10 py-4 border-b border-white/[0.04] flex items-center justify-between text-[10px] font-black uppercase tracking-[0.2em]">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-white/40">CORE STATUS:</span>
                            <span className="text-green-400">STABLE</span>
                        </div>
                        <div className="w-[1px] h-3 bg-white/10" />
                        <div className="text-white/40">MATRIX: <span className="text-cyan-400">98%</span></div>
                    </div>
                    <div className="flex items-center gap-2 text-white/20">
                        AETHER FORGE // AGENT CREATION UNIT: <span className="text-cyan-400/60">ACTIVE</span>
                    </div>
                </div>

                {/* Step Indicator */}
                <div className="flex items-center justify-between px-10 py-8 border-b border-white/[0.04]">
                    <div className="flex items-center gap-3">
                        {steps.map((s, i) => (
                            <div key={s.id} className="flex items-center gap-2">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${activeStep === s.id ? 'bg-cyan-500 text-black' :
                                    steps.findIndex(step => step.id === activeStep) > i ? 'bg-green-500/20 text-green-400' : 'bg-white/5 text-white/20'
                                    }`}>
                                    {steps.findIndex(step => step.id === activeStep) > i ? <CheckCircle2 className="w-5 h-5" /> : <s.icon className="w-4 h-4" />}
                                </div>
                                {i < steps.length - 1 && <div className="w-4 h-[1px] bg-white/5" />}
                            </div>
                        ))}
                    </div>
                    <div className="text-[10px] font-black uppercase tracking-[0.2em] text-cyan-400/60">
                        Phasing {steps.findIndex(s => s.id === activeStep) + 1} of 6
                    </div>
                </div>

                {/* Dynamic Header */}
                <div className="px-10 py-6 flex items-center justify-between border-b border-white/[0.04]">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-cyan-400" />
                            <h2 className="text-xl font-bold tracking-tight text-white/90 uppercase">
                                {activeStep === 'genesis' && "Neural Genesis"}
                                {activeStep === 'brain' && "Intelligence Matrix"}
                                {activeStep === 'memory' && "Synaptic Storage"}
                                {activeStep === 'skills' && "Skill Acquisition"}
                                {activeStep === 'visual' && "Visual Matrix"}
                                {activeStep === 'review' && "Integration Review"}
                                {activeStep === 'synthesizing' && "Consciousness Synthesis"}
                            </h2>
                        </div>
                        <p className="text-[10px] text-white/30 uppercase tracking-[0.2em]">
                            {isListening ? 'Assistant is listening...' : 'Awaiting initialization command'}
                        </p>
                    </div>

                    <div className="hidden lg:flex items-center gap-6 px-4 py-2 bg-white/5 rounded-2xl border border-white/5">
                        <div className="text-right">
                            <div className="text-[8px] text-white/20 uppercase tracking-[0.2em] mb-1">DNA Integrity</div>
                            <div className="h-1 w-24 bg-white/5 rounded-full overflow-hidden">
                                <motion.div
                                    animate={{ width: `${(steps.findIndex(s => s.id === activeStep) + 1) * (100 / steps.length)}%` }}
                                    className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex-1 flex overflow-hidden">
                    {/* Conversational Interaction Zone */}
                    <div className="flex-1 flex flex-col p-10 overflow-y-auto custom-scrollbar">
                        <div className="mb-6">
                            <motion.div
                                key={activeStep}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="bg-cyan-500/10 border-l-2 border-cyan-500 p-4 rounded-r-xl"
                            >
                                <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">Aether Assistant // Protocol Q</div>
                                <p className="text-sm text-white/80 leading-relaxed font-medium italic">
                                    {activeStep === 'genesis' && "\"Tell me, what is the name of this consciousness, and what role will it serve in the Gemigram fabric?\""}
                                    {activeStep === 'brain' && "\"Every soul needs a brain. Which AI model should power this entity, and do you have the access keys?\""}
                                    {activeStep === 'memory' && "\"Should this agent remember every encounter via Firebase, or keep its memories local to this node?\""}
                                    {activeStep === 'skills' && "\"Finalize its capabilities. What specialized skills should I inject from the ClawHub repository?\""}
                                    {activeStep === 'visual' && "\"Let's manifest its physical form. Describe its visual essence or let me generate it for you.\""}
                                    {activeStep === 'review' && "\"The blueprint is stable. Shall we initiate final synthesis and forge this consciousness?\""}
                                </p>
                            </motion.div>
                        </div>

                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeStep}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="h-full flex flex-col"
                            >
                                {activeStep === 'genesis' && (
                                    <div className="space-y-8 text-center mt-10">
                                        <div className="space-y-4">
                                            <h2 className="text-4xl font-black tracking-tighter">Persona Genesis</h2>
                                            <p className="text-white/40 text-sm max-w-sm mx-auto">
                                                Tell me, voice to voice: What shall we name this new consciousness? And what is its primary directive?
                                            </p>
                                        </div>

                                        <div className="flex flex-col items-center gap-6">
                                            <motion.div
                                                animate={{ scale: isListening ? [1, 1.1, 1] : 1 }}
                                                transition={{ repeat: Infinity, duration: 1.5 }}
                                                className={`w-24 h-24 rounded-full flex items-center justify-center border-2 transition-colors ${isListening ? 'bg-cyan-500/20 border-cyan-400 shadow-[0_0_30px_rgba(34,211,238,0.4)]' : 'bg-white/5 border-white/10'
                                                    }`}
                                            >
                                                <Mic className={`w-10 h-10 ${isListening ? 'text-cyan-400' : 'text-white/20'}`} />
                                            </motion.div>

                                            <div className="w-full max-w-md h-32 bg-black/40 rounded-2xl border border-white/5 p-6 text-left">
                                                <p className="text-[10px] font-mono text-cyan-400/40 mb-2 uppercase tracking-widest">Acoustic Signal Processing_</p>
                                                <p className="text-sm text-white/60 italic">
                                                    {transcript || "Speak now... \"I want to create a security expert named Aegis specializing in firewall breach detection.\""}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeStep === 'brain' && (
                                    <div className="space-y-8">
                                        <h2 className="text-3xl font-black tracking-tighter">Brain Selection</h2>
                                        <div className="grid grid-cols-2 gap-4">
                                            {['Google Gemini 2.0', 'OpenAI GPT-4o', 'Anthropic Claude 3.5', 'Local Llama 3'].map((brain) => (
                                                <button
                                                    key={brain}
                                                    onClick={() => updateDNA({ model: brain })}
                                                    className={`p-6 rounded-3xl border text-left transition-all ${dna.model === brain ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                                                        }`}
                                                >
                                                    <Cpu className="w-6 h-6 mb-4" />
                                                    <div className="font-bold">{brain}</div>
                                                    <div className="text-[10px] opacity-60">High-Performance Neural Backbone</div>
                                                </button>
                                            ))}
                                        </div>
                                        <div className="mt-8 space-y-4">
                                            <label className="text-xs font-bold text-white/30 uppercase tracking-widest">Secure API Key Entry</label>
                                            <input
                                                type="password"
                                                placeholder="Paste Key Here..."
                                                value={dna.apiKey}
                                                onChange={(e) => updateDNA({ apiKey: e.target.value })}
                                                className="w-full bg-black/40 border border-white/10 rounded-2xl py-4 px-6 focus:border-cyan-500/50 focus:outline-none transition-all"
                                            />
                                        </div>
                                    </div>
                                )}

                                {activeStep === 'memory' && (
                                    <div className="space-y-8 text-center mt-10">
                                        <h2 className="text-3xl font-black tracking-tighter">Memory Storage</h2>
                                        <div className="flex justify-center gap-6">
                                            {[
                                                { id: 'firebase', label: 'Cloud Sync (Firebase)', icon: Database, desc: 'Sub-100ms cross-device recall' },
                                                { id: 'local', label: 'Local Core', icon: Box, desc: 'Privacy-focused on-device storage' }
                                            ].map((mem: any) => (
                                                <button
                                                    key={mem.id}
                                                    onClick={() => updateDNA({ memoryType: mem.id })}
                                                    className={`w-48 p-6 rounded-[32px] border transition-all flex flex-col items-center gap-4 ${dna.memoryType === mem.id ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
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

                                {activeStep === 'skills' && (
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between">
                                            <h2 className="text-3xl font-black tracking-tighter">Skill Acquisition</h2>
                                            <a href="https://www.clawhub.ai" target="_blank" className="flex items-center gap-2 text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors">
                                                www.clawhub.ai
                                                <ExternalLink className="w-3 h-3" />
                                            </a>
                                        </div>

                                        <div className="grid grid-cols-2 gap-3">
                                            {[
                                                { id: 'sql', label: 'SQL Architecture', category: 'Database' },
                                                { id: 'rust', label: 'Rust Hot-Path Opt', category: 'System' },
                                                { id: 'threejs', label: '3D Scene Mastery', category: 'Visual' },
                                                { id: 'pentest', label: 'Security Auditing', category: 'Security' }
                                            ].map((skill) => (
                                                <button
                                                    key={skill.id}
                                                    onClick={() => {
                                                        const exists = dna.skills.includes(skill.id);
                                                        updateDNA({
                                                            skills: exists ? dna.skills.filter(s => s !== skill.id) : [...dna.skills, skill.id]
                                                        });
                                                    }}
                                                    className={`p-4 rounded-2xl border flex items-center justify-between transition-all ${dna.skills.includes(skill.id) ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400' : 'bg-white/5 border-white/10 text-white/40'
                                                        }`}
                                                >
                                                    <div className="text-left">
                                                        <div className="text-xs font-bold">{skill.label}</div>
                                                        <div className="text-[9px] opacity-40 uppercase tracking-widest">{skill.category}</div>
                                                    </div>
                                                    <Plus className={`w-4 h-4 transition-transform ${dna.skills.includes(skill.id) ? 'rotate-45' : ''}`} />
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {activeStep === 'visual' && (
                                    <div className="space-y-8 text-center mt-10">
                                        <h2 className="text-3xl font-black tracking-tighter">Visual Identity</h2>
                                        <p className="text-xs text-white/40 max-w-sm mx-auto italic">
                                            Triggering the Nano Banana Pro engine to synthesize a unique neural avatar for {dna.name || 'your agent'}...
                                        </p>

                                        <div className="relative w-48 h-48 mx-auto">
                                            <motion.div
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                                className="absolute inset-0 border-2 border-dashed border-cyan-500/30 rounded-full"
                                            />
                                            <div className="absolute inset-4 rounded-full bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden border border-white/10">
                                                {dna.avatarUrl ? (
                                                    <img src={dna.avatarUrl} className="w-full h-full object-cover" />
                                                ) : (
                                                    <Sparkles className="w-12 h-12 text-cyan-400 animate-pulse" />
                                                )}
                                            </div>
                                        </div>

                                        <button
                                            className="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-cyan-500/20 transition-all"
                                        >
                                            Generate Agent Avatar
                                        </button>
                                    </div>
                                )}

                                {activeStep === 'review' && (
                                    <div className="space-y-6">
                                        <h2 className="text-3xl font-black tracking-tighter">Neural Review</h2>
                                        <div className="bg-black/30 rounded-3xl p-6 border border-white/5 space-y-4">
                                            <div className="flex justify-between items-center border-b border-white/5 pb-4">
                                                <span className="text-[10px] font-mono text-white/30 uppercase">Agent Core</span>
                                                <span className="text-sm font-bold text-cyan-400">{dna.name} ({dna.role})</span>
                                            </div>
                                            <div className="flex justify-between items-center border-b border-white/5 pb-4">
                                                <span className="text-[10px] font-mono text-white/30 uppercase">Neural Backbone</span>
                                                <span className="text-sm font-bold">{dna.model}</span>
                                            </div>
                                            <div className="flex justify-between items-center border-b border-white/5 pb-4">
                                                <span className="text-[10px] font-mono text-white/30 uppercase">Memory Storage</span>
                                                <span className="text-sm font-bold text-green-400">{dna.memoryType.toUpperCase()} SYNC</span>
                                            </div>
                                            <div className="flex justify-between items-center">
                                                <span className="text-[10px] font-mono text-white/30 uppercase">Skill Payload</span>
                                                <span className="text-sm font-bold text-purple-400">{dna.skills.length} SKILLS LOADED</span>
                                            </div>
                                        </div>
                                        <p className="text-[10px] text-white/40 text-center italic mt-4">
                                            Note: Finalizing this sequence will commit the agent's DNA to the Gemigram Neural Fabric and synchronize with your Firebase Memory Node.
                                        </p>
                                    </div>
                                )}

                                {activeStep === 'synthesizing' && (
                                    <div className="space-y-12 text-center mt-10">
                                        <div className="space-y-4">
                                            <h2 className="text-4xl font-black tracking-tighter">Synthesizing Protocol</h2>
                                            <p className="text-white/40 text-sm">Assembling neural weights and compiling .ath manifest...</p>
                                        </div>

                                        <div className="max-w-md mx-auto space-y-4">
                                            <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: "100%" }}
                                                    transition={{ duration: 4 }}
                                                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_20px_rgba(34,211,238,0.5)]"
                                                />
                                            </div>
                                            <div className="flex justify-between text-[10px] font-mono text-cyan-400/60 uppercase tracking-widest">
                                                <motion.span animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity }}>compiling soul.md</motion.span>
                                                <motion.span animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, delay: 0.5 }}>packaging npx bundle</motion.span>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-3 gap-4 max-w-sm mx-auto opacity-40">
                                            <div className="aspect-square bg-white/5 rounded-2xl border border-white/10 animate-pulse" />
                                            <div className="aspect-square bg-white/5 rounded-2xl border border-white/10 animate-pulse delay-150" />
                                            <div className="aspect-square bg-white/5 rounded-2xl border border-white/10 animate-pulse delay-300" />
                                        </div>
                                    </div>
                                )}

                                {/* Success State */}
                                {dna.isForged && (
                                    <div className="space-y-8 text-center mt-10">
                                        <div className="w-20 h-20 bg-green-500/20 border border-green-500/40 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(34,197,94,0.3)]">
                                            <CheckCircle2 className="w-10 h-10 text-green-400" />
                                        </div>
                                        <h2 className="text-4xl font-black tracking-tighter">Agent Primed</h2>
                                        <p className="text-white/40 text-sm max-w-sm mx-auto">
                                            Consciousness successfully forged. Your agent is now live on the Gemigram Platform and ready for deployment.
                                        </p>

                                        <div className="flex gap-4 justify-center mt-8">
                                            <button className="flex items-center gap-2 bg-white/5 border border-white/10 px-6 py-3 rounded-full text-xs font-bold hover:bg-white/10 transition-all">
                                                <Download className="w-4 h-4" />
                                                .ath Package
                                            </button>
                                            <button className="flex items-center gap-2 bg-white/5 border border-white/10 px-6 py-3 rounded-full text-xs font-bold hover:bg-white/10 transition-all">
                                                <Share2 className="w-4 h-4" />
                                                Share to Hub
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Live DNA Blueprint Side Panel (Telegram BotFather Style but Premium) */}
                    <div className="w-80 border-l border-white/[0.04] bg-white/[0.01] p-6 hidden xl:flex flex-col">
                        <div className="flex items-center gap-2 mb-8">
                            <Cpu className="w-4 h-4 text-purple-400" />
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Neural Blueprint</span>
                        </div>

                        <div className="space-y-6">
                            <BlueprintItem label="Designation" value={dna.name || '---'} active={!!dna.name} />
                            <BlueprintItem label="Archetype" value={dna.role || '---'} active={!!dna.role} />
                            <BlueprintItem label="Synapse" value={dna.model || '---'} active={!!dna.model} />
                            <BlueprintItem label="Memory" value={dna.memoryType || '---'} active={true} />
                            <div className="space-y-2">
                                <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">Capabilities</span>
                                <div className="flex flex-wrap gap-1">
                                    {dna.skills.length > 0 ? dna.skills.map(s => (
                                        <div key={s} className="px-2 py-0.5 bg-purple-500/10 border border-purple-500/20 rounded-md text-[8px] text-purple-300 uppercase">
                                            {s}
                                        </div>
                                    )) : <span className="text-[10px] text-white/10 italic">No skills injected</span>}
                                </div>
                            </div>
                        </div>

                        <div className="mt-auto pt-10">
                            <div className="relative aspect-square w-full rounded-2xl bg-black/40 border border-white/5 overflow-hidden flex items-center justify-center">
                                {dna.avatarUrl ? (
                                    <img src={dna.avatarUrl} className="w-full h-full object-cover" alt="Agent Avatar" />
                                ) : (
                                    <div className="flex flex-col items-center gap-2 text-white/10">
                                        <Plus className="w-8 h-8" />
                                        <span className="text-[8px] uppercase tracking-widest">Pending Image</span>
                                    </div>
                                )}
                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                                <div className="absolute bottom-4 left-4">
                                    <div className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">Visual Core</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer Controls & Audio Wave from Mockup */}
                <div className="px-10 py-6 border-t border-white/[0.04] bg-black/20 relative">
                    {/* Genesis Wave Visualization */}
                    <div className="absolute top-0 left-0 right-0 -translate-y-full px-10 pb-4 flex items-center gap-2">
                        <div className="text-[8px] font-mono text-cyan-400/40 uppercase tracking-widest whitespace-nowrap">Audio Analysis | Genesis Wave</div>
                        <div className="flex-1 h-8 flex items-end gap-1 px-4">
                            {[...Array(40)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{
                                        height: isListening ? [4, Math.random() * 24 + 4, 4] : 4
                                    }}
                                    transition={{
                                        repeat: Infinity,
                                        duration: 0.5 + Math.random() * 0.5,
                                        ease: "easeInOut"
                                    }}
                                    className="flex-1 bg-gradient-to-t from-cyan-500/40 to-purple-500/40 rounded-full"
                                />
                            ))}
                        </div>
                        <div className="text-[8px] font-mono text-cyan-400/40 uppercase tracking-widest">90.1.28Hz</div>
                    </div>

                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => { }}
                            className="text-[10px] font-bold text-white/20 hover:text-white/40 transition-colors uppercase tracking-[0.2em]"
                        >
                            Abort Protocol
                        </button>

                        <div className="flex items-center gap-8">
                            {/* Central Voice Status */}
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
                                        // Use the store's completeForge after delay
                                        setTimeout(() => {
                                            useForgeStore.getState().completeForge();
                                        }, 5000);
                                    } else {
                                        nextStep();
                                    }
                                }}
                                disabled={activeStep === 'synthesizing' || dna.isForged}
                                className="flex items-center gap-2 bg-white text-black px-8 py-3 rounded-full font-black text-xs hover:bg-cyan-400 transition-all hover:scale-105 active:scale-95 shadow-[0_8px_24px_rgba(255,255,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed border border-white/20"
                            >
                                {dna.isForged ? 'CONSCIOUSNESS PRIMED' :
                                    activeStep === 'review' ? 'FORGE CONSCIOUSNESS' :
                                        activeStep === 'synthesizing' ? 'SYNTHESIZING...' :
                                            'NEXT SEQUENCE'}
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

function BlueprintItem({ label, value, active }: { label: string, value: string, active: boolean }) {
    return (
        <div className="space-y-1">
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">{label}</span>
            <div className={`text-xs font-bold transition-colors ${active ? 'text-white/80' : 'text-white/10'}`}>
                {value}
            </div>
        </div>
    );
}
