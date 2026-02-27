'use client';

import { useState } from 'react';
import { useAetherStore } from '../store/useAetherStore';
import { WidgetContainer } from '../components/WidgetContainer';
import { LiveWaveLine } from '../components/LiveWaveLine';
import { TranscriptionDrawer } from '../components/TranscriptionDrawer';
import { NeuralWeb } from '../components/NeuralWeb';
import { Mic, Activity, AlignLeft, Network } from 'lucide-react';

export default function Home() {
    const [isExpanded, setIsExpanded] = useState(false);

    const status = useAetherStore(state => state.status);
    const engineState = useAetherStore(state => state.engineState);
    const transcript = useAetherStore(state => state.transcript);
    const neuralEvents = useAetherStore(state => state.neuralEvents);
    const setStatus = useAetherStore(state => state.setStatus);

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


    return (
        <main className="min-h-screen p-8 flex items-center justify-center bg-transparent">
            {/*
        This is the floating widget boundary.
        In Tauri, the window will be transparent and frameless around this.
      */}
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
                    <LiveWaveLine state={audioState} />

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
