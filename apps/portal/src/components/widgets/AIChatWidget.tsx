'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

export default function AIChatWidget() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        { id: '1', role: 'assistant', content: 'Hey! Ask me anything. I\'m Aether, your AI co-pilot. 🧠', timestamp: Date.now() },
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (!input.trim()) return;

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: Date.now(),
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        // Simulate AI response
        setTimeout(() => {
            const aiMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: getQuickResponse(input),
                timestamp: Date.now(),
            };
            setMessages(prev => [...prev, aiMsg]);
            setIsTyping(false);
        }, 800 + Math.random() * 1200);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">AI Chat</span>
                <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[9px] font-mono text-emerald-400/60">Online</span>
                </div>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto flex flex-col gap-2 mb-2 max-h-[160px]">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex items-start gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                            msg.role === 'user' ? 'bg-cyan-500/20' : 'bg-purple-500/20'
                        }`}>
                            {msg.role === 'user' ? <User className="w-2.5 h-2.5 text-cyan-400" /> : <Bot className="w-2.5 h-2.5 text-purple-400" />}
                        </div>
                        <div className={`text-xs px-3 py-2 rounded-xl max-w-[80%] ${
                            msg.role === 'user'
                                ? 'bg-cyan-500/10 text-white/70 border border-cyan-500/10'
                                : 'bg-white/[0.04] text-white/60 border border-white/5'
                        }`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="flex items-center gap-2">
                        <div className="w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center">
                            <Bot className="w-2.5 h-2.5 text-purple-400" />
                        </div>
                        <div className="flex gap-1 px-3 py-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-white/20 animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-1.5 h-1.5 rounded-full bg-white/20 animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-1.5 h-1.5 rounded-full bg-white/20 animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type a message..."
                    className="flex-1 bg-transparent text-xs text-white/60 placeholder:text-white/15 outline-none"
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim()}
                    className="p-1.5 hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30"
                >
                    <Send className="w-3.5 h-3.5 text-cyan-400/60" />
                </button>
            </div>
        </div>
    );
}

function getQuickResponse(input: string): string {
    const lower = input.toLowerCase();
    if (lower.includes('hello') || lower.includes('hi') || lower.includes('مرحبا')) {
        return 'مرحباً! كيف أقدر أساعدك اليوم؟ 😊';
    }
    if (lower.includes('weather') || lower.includes('طقس')) {
        return 'The weather widget shows real-time data. Check it on your dashboard!';
    }
    if (lower.includes('help') || lower.includes('مساعدة')) {
        return 'I can help with coding, debugging, architecture, and more. Try voice mode for a richer experience!';
    }
    return 'Got it! For complex tasks, try activating voice mode by clicking the orb. I work best in conversation. 🎤';
}
