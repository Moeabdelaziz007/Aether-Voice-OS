'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useRef } from 'react';

// Basic markdown-like token renderer for streaming text
const MarkdownRenderer = ({ text }: { text: string }) => {
    return (
        <div className="text-sm font-mono text-cyan-50/80 leading-relaxed overflow-hidden">
            {text}
        </div>
    );
};

interface TranscriptionDrawerProps {
    isOpen: boolean;
    messages: Array<{ role: 'user' | 'agent'; content: string }>;
}

export function TranscriptionDrawer({ isOpen, messages }: TranscriptionDrawerProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0, height: 0, marginTop: 0 }}
                    animate={{ opacity: 1, height: 350, marginTop: 16 }}
                    exit={{ opacity: 0, height: 0, marginTop: 0 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    className="w-full bg-black/40 rounded-2xl border border-white/5 overflow-hidden flex flex-col"
                >
                    <div
                        ref={scrollRef}
                        className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
                    >
                        {messages.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-white/20 text-xs uppercase tracking-widest font-mono">
                                No active transcript...
                            </div>
                        ) : (
                            messages.map((msg, i) => (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    key={i}
                                    className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                                >
                                    <span className="text-[10px] uppercase font-bold tracking-wider mb-1 opacity-40">
                                        {msg.role}
                                    </span>
                                    <div className={`p-3 rounded-2xl max-w-[85%] ${msg.role === 'user'
                                            ? 'bg-white/10 rounded-tr-sm backdrop-blur-md'
                                            : 'bg-cyan-950/40 border border-cyan-500/20 rounded-tl-sm backdrop-blur-md'
                                        }`}>
                                        <MarkdownRenderer text={msg.content} />
                                    </div>
                                </motion.div>
                            ))
                        )}
                    </div>

                    <div className="h-8 bg-gradient-to-t from-black/80 to-transparent w-full absolute bottom-0 pointer-events-none" />
                </motion.div>
            )}
        </AnimatePresence>
    );
}
