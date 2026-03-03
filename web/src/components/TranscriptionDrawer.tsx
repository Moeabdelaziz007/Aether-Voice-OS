'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { Terminal, Cpu } from 'lucide-react';

const TypewriterText = ({ text, delay = 0 }: { text: string; delay?: number }) => {
    const [displayedText, setDisplayedText] = useState('');

    useEffect(() => {
        let i = 0;
        setDisplayedText('');
        const timer = setInterval(() => {
            if (i < text.length) {
                setDisplayedText((prev) => prev + text.charAt(i));
                i++;
            } else {
                clearInterval(timer);
            }
        }, 15); // Fast typing speed
        return () => clearInterval(timer);
    }, [text]);

    return <span>{displayedText}</span>;
};

const MarkdownRenderer = ({ text, isNew }: { text: string; isNew: boolean }) => {
    return (
        <div className="text-[11px] font-mono leading-relaxed overflow-hidden text-cyan-50">
            {isNew ? <TypewriterText text={text} /> : text}
        </div>
    );
};

interface TranscriptionDrawerProps {
    isOpen: boolean;
    messages: Array<{ role: 'user' | 'agent'; content: string }>;
}

export function TranscriptionDrawer({ isOpen, messages }: TranscriptionDrawerProps) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const prevLength = useRef(messages.length);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
        prevLength.current = messages.length;
    }, [messages, isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0, height: 0, marginTop: 0 }}
                    animate={{ opacity: 1, height: 380, marginTop: 16 }}
                    exit={{ opacity: 0, height: 0, marginTop: 0 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    className="w-full bg-[#050505] rounded-2xl border border-[#00f3ff]/20 overflow-hidden flex flex-col relative shadow-[0_0_40px_rgba(0,243,255,0.05)]"
                >
                    {/* CRTs & Scanlines */}
                    <div className="absolute inset-0 pointer-events-none opacity-10 mix-blend-overlay z-0"
                        style={{
                            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #fff 2px, #fff 4px)'
                        }}
                    />
                    <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_60px_rgba(0,0,0,0.8)] z-0" />

                    {/* Header */}
                    <div className="relative z-10 flex items-center justify-between px-4 py-2 border-b border-[#00f3ff]/20 bg-[#00f3ff]/5">
                        <div className="flex items-center gap-2">
                            <Terminal size={12} className="text-[#00f3ff]" />
                            <span className="font-mono text-[9px] text-[#00f3ff] uppercase tracking-[0.3em] font-bold">Secure Neural Link</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#00f3ff] animate-pulse shadow-[0_0_8px_#00f3ff]" />
                            <span className="font-mono text-[9px] text-white/40 uppercase tracking-widest">Live</span>
                        </div>
                    </div>

                    <div
                        ref={scrollRef}
                        className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth relative z-10 scrollbar-thin"
                    >
                        {messages.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-[#00f3ff]/40 text-[10px] uppercase tracking-widest font-mono">
                                Awaiting cognitive input...
                            </div>
                        ) : (
                            messages.map((msg, i) => {
                                const isNew = i >= prevLength.current;
                                const isAgent = msg.role === 'agent';

                                return (
                                    <motion.div
                                        initial={{ opacity: 0, x: isAgent ? -10 : 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        key={i}
                                        className={`flex flex-col ${isAgent ? 'items-start' : 'items-end'}`}
                                    >
                                        <div className="flex items-center gap-2 mb-1 opacity-60">
                                            {isAgent && <Cpu size={10} className="text-[#bc13fe]" />}
                                            <span className={`text-[9px] uppercase font-bold tracking-[0.2em] ${isAgent ? 'text-[#bc13fe]' : 'text-[#00f3ff]'}`}>
                                                {msg.role}
                                            </span>
                                        </div>
                                        <div className={`px-4 py-3 max-w-[85%] border backdrop-blur-md relative group ${isAgent
                                                ? 'bg-[#bc13fe]/5 border-[#bc13fe]/30 rounded-r-xl rounded-bl-xl shadow-[0_0_15px_rgba(188,19,254,0.1)]'
                                                : 'bg-[#00f3ff]/5 border-[#00f3ff]/30 rounded-l-xl rounded-br-xl shadow-[0_0_15px_rgba(0,243,255,0.1)]'
                                            }`}
                                        >
                                            {/* Corner Accents */}
                                            <div className={`absolute w-1.5 h-1.5 border-t border-l -top-px -left-px ${isAgent ? 'border-[#bc13fe]' : 'border-[#00f3ff]'}`} />
                                            <div className={`absolute w-1.5 h-1.5 border-b border-r -bottom-px -right-px ${isAgent ? 'border-[#bc13fe]' : 'border-[#00f3ff]'}`} />

                                            <MarkdownRenderer text={msg.content} isNew={isNew} />
                                        </div>
                                    </motion.div>
                                );
                            })
                        )}
                    </div>

                    <div className="h-8 bg-gradient-to-t from-[#050505] to-transparent w-full absolute bottom-0 pointer-events-none z-20" />
                </motion.div>
            )}
        </AnimatePresence>
    );
}
