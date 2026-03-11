"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Zap, MessageSquare, Bot, Cpu, Sparkles, Terminal } from "lucide-react";
import { useAetherGateway } from "@/hooks/useAetherGateway";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * Omnibar V5: GemiGram Edition
 * Unified entry point for Voice, Text, and Neural Intent.
 * Features a magnetic glassmorphic design and stateful expansion.
 */
export default function Omnibar() {
    const [inputValue, setInputValue] = useState("");
    const [isFocused, setIsFocused] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const { sendIntent, status } = useAetherGateway();
    const activeSoul = useAetherStore((s) => s.activeSoul);
    const engineState = useAetherStore((s) => s.engineState);
    const setListening = useAetherStore((s) => s.setListening);
    const omnibarFocused = useAetherStore((s) => s.omnibarFocused);

    useEffect(() => {
        if (omnibarFocused) {
            inputRef.current?.focus();
            setIsFocused(true);
        } else {
            inputRef.current?.blur();
            setIsFocused(false);
        }
    }, [omnibarFocused]);

    // Magnetic interaction
    const handleExecute = async () => {
        if (!inputValue.trim()) return;
        await sendIntent(inputValue, 1);
        setInputValue("");
    };

    return (
        <div className="fixed inset-x-0 bottom-12 flex justify-center z-50 px-6">
            <motion.div
                initial={false}
                animate={{
                    width: isFocused ? "640px" : "480px",
                    y: isFocused ? -8 : 0
                }}
                className="relative group w-full max-w-[640px]"
            >
                {/* Outer Neon Glow */}
                <div className="absolute -inset-[1px] bg-gradient-to-r from-neon-cyan/20 via-neon-purple/20 to-neon-pink/20 rounded-2xl blur-sm opacity-50 group-hover:opacity-100 transition-opacity" />

                {/* Main Container */}
                <div className="relative bg-carbon-950/80 backdrop-blur-[60px] border border-white/10 rounded-2xl shadow-2xl overflow-hidden">

                    {/* Visual DNA Bar (Top) */}
                    <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-30" />

                    <div className="flex items-center px-6 py-4 gap-4">
                        {/* Status Icon */}
                        <div className="flex items-center justify-center w-6 h-6">
                            {engineState === 'LISTENING' ? (
                                <motion.div
                                    animate={{ scale: [1, 1.5, 1] }}
                                    transition={{ repeat: Infinity, duration: 1 }}
                                    className="w-2 h-2 bg-neon-cyan rounded-full shadow-[0_0_10px_#00F3FF]"
                                />
                            ) : (
                                <Terminal className="w-5 h-5 text-white/20" />
                            )}
                        </div>

                        {/* Input Field */}
                        <input
                            ref={inputRef}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                            onKeyDown={(e) => e.key === "Enter" && handleExecute()}
                            placeholder={engineState === 'LISTENING' ? "Listening to neural stream..." : "Describe an intent or command..."}
                            className="flex-1 bg-transparent border-none outline-none text-white text-lg placeholder:text-white/10 font-medium tracking-tight"
                        />

                        {/* Right Actions */}
                        <div className="flex items-center gap-3">
                            <AnimatePresence>
                                {inputValue.length > 0 && (
                                    <motion.button
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 10 }}
                                        onClick={handleExecute}
                                        className="p-2 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-colors"
                                    >
                                        <Zap className="w-4 h-4 text-neon-cyan" />
                                    </motion.button>
                                )}
                            </AnimatePresence>

                            <button
                                onClick={() => setListening(engineState !== 'LISTENING')}
                                className={`p-3 rounded-xl border transition-all duration-300 ${engineState === 'LISTENING'
                                    ? "bg-neon-cyan border-neon-cyan text-black shadow-[0_0_30px_#00F3FF]"
                                    : "bg-white/5 border-white/10 text-white/40 hover:text-white"
                                    }`}
                            >
                                <Mic className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Bottom Status Grid */}
                    <div className="flex items-center justify-between px-6 py-2 bg-white/[0.02] border-t border-white/[0.05]">
                        <div className="flex gap-4">
                            <Badge icon={<Bot className="w-3 h-3" />} label={activeSoul || "Gemini"} active />
                            <Badge icon={<Sparkles className="w-3 h-3" />} label="Flash 2.0" />
                        </div>
                        <div className="text-[10px] font-mono text-white/10 tracking-widest uppercase">
                            Secure // AES-256
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}

function Badge({ icon, label, active }: { icon: React.ReactNode, label: string, active?: boolean }) {
    return (
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-colors ${active ? "text-neon-cyan bg-neon-cyan/10 border border-neon-cyan/20" : "text-white/20"
            }`}>
            {icon}
            {label}
        </div>
    );
}
