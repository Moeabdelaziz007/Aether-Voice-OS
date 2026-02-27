'use client';

import { useState, useEffect } from 'react';
import { useAetherStore } from '../store/useAetherStore';
import { WidgetContainer } from '../components/WidgetContainer';
import { LiveWaveLine } from '../components/LiveWaveLine';
import { TranscriptionDrawer } from '../components/TranscriptionDrawer';
import { NeuralWeb } from '../components/NeuralWeb';
import { Mic, Activity, AlignLeft, Eye, Zap, Sparkles, Shield } from 'lucide-react';
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
    const zenMode = useAetherStore(state => state.zenMode);

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
        <main className="min-h-screen p-8 flex items-center justify-center bg-transparent">
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
                            <div className="bg-[#9d4edd]/20 backdrop-blur-md border border-[#9d4edd]/50 px-4 py-2 rounded-full flex items-center gap-2 shadow-[0_0_20px_#9d4edd33]">
                                <Sparkles size={14} className="text-[#9d4edd]" />
                                <span className="text-[10px] font-mono text-white tracking-widest uppercase">Genetic Leap Detected</span>
                            </div>
                        </motion.div>
                    )
                }
            </AnimatePresence >

            <WidgetContainer isExpanded={isExpanded}>
                {/* Top Header Bar */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className={`relative flex h-3 w-3`}>
                            {audioState !== 'idle' && (
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                            )}
                            <span className={`relative inline-flex rounded-full h-3 w-3 ${audioState === 'idle' ? 'bg-white/20' : 'bg-cyan-500'}`}></span>
                        </div>
                        <span className="font-mono text-xs tracking-widest uppercase text-white/50">
                            {audioState}
                        </span>

                        {/* Vision Pulse Indicator */}
                        <div className="flex items-center gap-1.5 ml-2 border-l border-white/10 pl-3">
                            <Eye size={12} className={visionActive ? "text-cyan-400 animate-pulse" : "text-white/20"} />
                            <span className="text-[10px] font-mono text-white/30 tracking-tighter uppercase">Vision Link</span>
                        </div>

                        {/* Zen Mode / Neural Shield Indicator */}
                        {zenMode && (
                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-center gap-1.5 ml-2 border-l border-white/10 pl-3"
                            >
                                <Shield size={12} className="text-[#9d4edd] animate-pulse" />
                                <span className="text-[10px] font-mono text-[#9d4edd] tracking-tighter uppercase font-bold">Neural Shield</span>
                            </motion.div>
                        )}
                    </div>

                    <div className="flex gap-2">
                        <button
                            title="Expand Menu"
                            aria-label="Expand Menu"
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="p-2 rounded-full hover:bg-white/10 transition-colors text-white/50 hover:text-white"
                        >
                            <AlignLeft size={16} />
                        </button>
                    </div>
                </div>

                {/* Central Audio Visualizer */}
                <div className="flex-1 flex flex-col justify-center relative z-10">
                    <LiveWaveLine state={audioState} valence={valence} arousal={arousal} />

                    {/* ADK Visualization */}
                    <div className="px-4 mt-6">
                        <NeuralWeb events={neuralEvents.length > 0 ? neuralEvents : [
                            { id: '1', fromAgent: 'System', toAgent: 'Aether', task: 'Ready for inputs', status: 'completed' }
                        ]} />
                    </div>

                    <div className="absolute inset-x-0 bottom-0 flex justify-center -mb-2 mt-4">
                        <button
                            onClick={toggleListening}
                            className={`p-3 rounded-full transition-all duration-300 ${audioState !== 'idle'
                                ? 'bg-cyan-500/20 text-cyan-400 shadow-[0_0_15px_rgba(0,243,255,0.4)]'
                                : 'bg-white/5 text-white/40 hover:bg-white/10 hover:text-white'
                                }`}
                        >
                            {audioState === 'thinking' ? <Activity size={20} className="animate-pulse" /> : <Mic size={20} />}
                        </button>
                    </div>
                </div>

                {/* Expanding Drawer for Transcripts */}
                <TranscriptionDrawer isOpen={isExpanded} messages={transcript.length > 0 ? transcript : [{ role: 'agent', content: 'Aether initialized. Ready for audio link.' }]} />

            </WidgetContainer>
        </main>
    );
}
