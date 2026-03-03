'use client';

import { useState, useEffect } from 'react';
import { useAetherStore } from '../store/useAetherStore';
import { WidgetContainer } from '../components/WidgetContainer';
import { LiveWaveLine } from '../components/LiveWaveLine';
import { TranscriptionDrawer } from '../components/TranscriptionDrawer';
import { NeuralWeb } from '../components/NeuralWeb';
import { Mic, Activity, AlignLeft, Zap, Sparkles } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

export default function Home() {
    const [isExpanded, setIsExpanded] = useState(false);

    const status = useAetherStore(state => state.status);
    const engineState = useAetherStore(state => state.engineState);
    const transcript = useAetherStore(state => state.transcript);
    const neuralEvents = useAetherStore(state => state.neuralEvents);
    const lastMutation = useAetherStore(state => state.lastMutation);
    const valence = useAetherStore(state => state.valence);
    const arousal = useAetherStore(state => state.arousal);
    const setStatus = useAetherStore(state => state.setStatus);
    const lastVisionPulse = useAetherStore(state => state.lastVisionPulse);

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [visionActive, setVisionActive] = useState(false);
    const [showMutationAlert, setShowMutationAlert] = useState(false);

    // Map global status to local audioState for the visualizer components
    const audioState = (() => {
        if (status === 'disconnected') return 'idle';
        if (status === 'connecting') return 'thinking';
        if (engineState === 'LISTENING') return 'listening';
        if (engineState === 'THINKING') return 'thinking';
        if (engineState === 'SPEAKING') return 'speaking';
        return 'idle';
    })();

    // Toggle real connection
    const toggleListening = () => {
        if (status === 'disconnected') {
            setStatus('connecting'); // This will trigger AetherBrain to connect
        } else {
            setStatus('disconnected'); // This will trigger AetherBrain to disconnect
        }
    };


    // Auto-clear mutation alert
    useEffect(() => {
        if (lastMutation) {
            setShowMutationAlert(true);
            const timer = setTimeout(() => setShowMutationAlert(false), 5000);
            return () => clearTimeout(timer);
        }
    }, [lastMutation]);

    // Vision Pulse Feedback
    useEffect(() => {
        if (lastVisionPulse) {
            setVisionActive(true);
            const timer = setTimeout(() => setVisionActive(false), 1500);
            return () => clearTimeout(timer);
        }
    }, [lastVisionPulse]);

    return (
        <main className="min-h-screen p-8 flex items-center justify-center bg-transparent selection:bg-[#00f3ff]/30">
            {/* Mutation Alert Overlay */}
            <AnimatePresence>
                {
                    showMutationAlert && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8, y: -20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.8, y: -20 }}
                            className="fixed top-24 left-1/2 -translate-x-1/2 z-50 pointer-events-none"
                        >
                            <div className="bg-[#bc13fe]/10 backdrop-blur-md border border-[#bc13fe]/30 px-6 py-2 rounded-full flex items-center gap-3 shadow-[0_0_30px_rgba(188,19,254,0.2)]">
                                <Sparkles size={16} className="text-[#bc13fe] animate-pulse" />
                                <span className="text-[10px] font-mono text-white tracking-[0.4em] uppercase font-bold">Evolutionary Leap Detected</span>
                            </div>
                        </motion.div>
                    )
                }
            </AnimatePresence >

            <WidgetContainer isExpanded={isExpanded}>
                {/* Top Header Bar */}
                <div className="flex items-center justify-between mb-4 z-20 relative">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className={`relative flex h-2 w-2 rounded-full ${audioState === 'idle' ? 'bg-white/10' : 'bg-[#00f3ff] shadow-[0_0_8px_#00f3ff]'}`}>
                                {audioState !== 'idle' && (
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00f3ff] opacity-75"></span>
                                )}
                            </div>
                            <span className="font-mono text-[9px] tracking-[0.2em] uppercase text-white/40 font-bold">
                                {audioState}
                            </span>
                        </div>

                        {/* Neural Integrity Indicator */}
                        <div className="flex items-center gap-2 ml-2 border-l border-white/5 pl-4">
                            <Zap size={10} className={status === 'connected' ? "text-[#00f3ff]" : "text-white/10"} />
                            <div className="flex flex-col">
                                <span className="text-[7px] font-mono text-white/20 uppercase tracking-tighter">Integrity</span>
                                <span className="text-[9px] font-mono text-white/60 tracking-tighter uppercase font-bold">
                                    {status === 'connected' ? '98.4%' : '0.0%'}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        {/* Handover Latency Mock */}
                        {isExpanded && (
                            <motion.div
                                initial={{ opacity: 0, x: 10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-center gap-2 border-r border-white/5 pr-4"
                            >
                                <Activity size={10} className="text-[#bc13fe]" />
                                <div className="flex flex-col items-end">
                                    <span className="text-[7px] font-mono text-white/20 uppercase tracking-tighter">Latency</span>
                                    <span className="text-[9px] font-mono text-[#bc13fe]/80 tracking-tighter uppercase font-bold">284ms</span>
                                </div>
                            </motion.div>
                        )}
                        <button
                            title="Expand Menu"
                            aria-label="Expand Menu"
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="p-1.5 rounded-lg hover:bg-white/5 transition-colors text-white/20 hover:text-[#00f3ff]"
                        >
                            <AlignLeft size={16} />
                        </button>
                    </div>
                </div>

                {/* Central Audio Visualizer */}
                <div className="flex-1 flex flex-col justify-center relative z-10">
                    <div className="relative h-24 mb-2 shrink-0">
                        <LiveWaveLine state={audioState} valence={valence} arousal={arousal} />
                    </div>

                    {/* ADK Visualization (Only when expanded to save space) */}
                    <AnimatePresence>
                        {isExpanded && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mt-2"
                            >
                                <NeuralWeb events={neuralEvents.length > 0 ? neuralEvents : []} />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Control Hub Overlay */}
                    <div className="absolute inset-x-0 -bottom-8 flex justify-center z-30 pointer-events-none">
                        <button
                            onClick={toggleListening}
                            className={`pointer-events-auto p-5 rounded-2xl transition-all duration-500 border group ${audioState !== 'idle'
                                ? 'bg-[#00f3ff]/10 border-[#00f3ff]/40 text-[#00f3ff] shadow-[0_0_30px_rgba(0,243,255,0.2)]'
                                : 'bg-[#050505]/80 border-white/10 text-white/20 hover:border-white/30 hover:text-white backdrop-blur-md'
                                }`}
                        >
                            {audioState === 'thinking' ?
                                <Activity size={24} className="animate-pulse" /> :
                                <Mic size={24} className="group-hover:scale-110 transition-transform" />
                            }

                            {/* Inner Ring */}
                            {audioState !== 'idle' && (
                                <div className="absolute inset-0 rounded-2xl border border-[#00f3ff]/20 animate-ping opacity-20" />
                            )}
                        </button>
                    </div>
                </div>

                {/* Expanding Drawer for Transcripts */}
                <TranscriptionDrawer
                    isOpen={isExpanded}
                    messages={transcript.length > 0 ? transcript : [{ role: 'agent', content: 'Neural link established. Awaiting cerebral input.' }]}
                />
            </WidgetContainer>
        </main>
    );
}
