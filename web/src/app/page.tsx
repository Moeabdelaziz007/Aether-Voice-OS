'use client';

import { useState } from 'react';
import { WidgetContainer } from '../components/WidgetContainer';
import { LiveWaveLine } from '../components/LiveWaveLine';
import { TranscriptionDrawer } from '../components/TranscriptionDrawer';
import { Mic, Activity, AlignLeft } from 'lucide-react';

export default function Home() {
    const [isExpanded, setIsExpanded] = useState(false);
    const [audioState, setAudioState] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');

    // Mock messages for UI development
    const [messages, setMessages] = useState([
        { role: 'agent' as const, content: 'Aether initialized. Ready for voice input.' }
    ]);

    // Mock connecting state toggle
    const toggleListening = () => {
        setAudioState(prev => prev === 'idle' ? 'listening' : 'idle');
        if (audioState === 'idle') {
            setTimeout(() => {
                setAudioState('thinking');
                setTimeout(() => {
                    setMessages(prev => [...prev, { role: 'user', content: 'What is the weather today?' }]);
                    setAudioState('speaking');
                    setTimeout(() => {
                        setMessages(prev => [...prev, { role: 'agent', content: 'The weather is optimal. Clear skies and 24 degrees Celsius.' }]);
                        setAudioState('idle');
                    }, 3000);
                }, 1500);
            }, 2000);
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

                    <div className="absolute inset-x-0 bottom-0 flex justify-center -mb-2">
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
                <TranscriptionDrawer isOpen={isExpanded} messages={messages} />

            </WidgetContainer>
        </main>
    );
}
