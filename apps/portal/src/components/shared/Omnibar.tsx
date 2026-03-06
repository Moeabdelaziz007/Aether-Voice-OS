"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Command, Zap, MessageSquare, Bot, Cpu } from "lucide-react";
import { useAetherGateway } from "@/hooks/useAetherGateway";
import { useAetherStore } from "@/store/useAetherStore";

/**
 * Omnibar — The 3-Level Intent Entry Point.
 * Level 1: Quick Intent (Zap)
 * Level 2: Conversation (Message)
 * Level 3: Agent Mode (Bot)
 */
export default function Omnibar() {
    const [isOpen, setIsOpen] = useState(false);
    const [inputValue, setInputValue] = useState("");
    const [level, setLevel] = useState<1 | 2 | 3>(1);
    const inputRef = useRef<HTMLInputElement>(null);

    const { sendIntent, status } = useAetherGateway();
    const activeSoul = useAetherStore((s) => s.activeSoul);

    const soulColor = activeSoul === "Architect" ? "text-cyan-400" : "text-emerald-400";
    const soulBg = activeSoul === "Architect" ? "bg-cyan-500/10" : "bg-emerald-500/10";
    const soulBorder = activeSoul === "Architect" ? "border-cyan-500/20" : "border-emerald-500/20";

    // Toggle logic
    const toggle = useCallback(() => {
        setIsOpen((prev) => !prev);
    }, []);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "k") {
                e.preventDefault();
                toggle();
            }
            if (e.key === "Escape" && isOpen) {
                setIsOpen(false);
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [isOpen, toggle]);

    useEffect(() => {
        if (isOpen) {
            inputRef.current?.focus();
        }
    }, [isOpen]);

    const handleExecute = async () => {
        if (!inputValue.trim()) return;

        // Level detection logic (Quick heuristics)
        let targetLevel: 1 | 2 | 3 = level;
        if (inputValue.toLowerCase().startsWith("why") || inputValue.endsWith("?")) {
            targetLevel = 2;
        } else if (inputValue.toLowerCase().includes("fix") || inputValue.toLowerCase().includes("deploy")) {
            targetLevel = 3;
        }

        await sendIntent(inputValue, targetLevel);

        // Feedback & Cleanup
        setInputValue("");
        if (targetLevel === 1) {
            setIsOpen(false); // Snap back for Level 1
        }
    };

    return (
        <div className="fixed inset-x-0 bottom-12 flex justify-center z-50 pointer-events-none">
            <AnimatePresence>
                {isOpen ? (
                    <motion.div
                        initial={{ y: 20, opacity: 0, scale: 0.98 }}
                        animate={{ y: 0, opacity: 1, scale: 1 }}
                        exit={{ y: 10, opacity: 0, scale: 0.98 }}
                        transition={{ duration: 0.15, ease: "easeOut" }}
                        className="w-full max-w-[640px] pointer-events-auto mx-4"
                    >
                        <div className="relative group">
                            {/* Main Input Container */}
                            <div className="bg-[#0a0a0c]/90 backdrop-blur-3xl border border-white/[0.08] rounded-xl shadow-[0_32px_64px_rgba(0,0,0,0.8),0_0_0_1px_rgba(255,255,255,0.02)] overflow-hidden">
                                <div className="flex items-center px-4 py-3.5 gap-3">
                                    <Command className="w-4 h-4 text-white/30" />

                                    <input
                                        ref={inputRef}
                                        value={inputValue}
                                        onChange={(e) => {
                                            setInputValue(e.target.value);
                                            // Clear prediction when typing a new query
                                            if (useAetherStore.getState().predictedGoal) {
                                                useAetherStore.getState().setPredictedGoal(null);
                                            }
                                        }}
                                        onKeyDown={(e) => e.key === "Enter" && handleExecute()}
                                        placeholder="Command or intent..."
                                        className="flex-1 bg-transparent border-none outline-none text-white/90 font-sans text-base placeholder:text-white/20"
                                    />

                                    {/* Expert Soul Badge */}
                                    <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md border ${soulBg} ${soulBorder} ${soulColor} transition-all duration-300`}>
                                        <Cpu className="w-3 h-3" />
                                        <span className="text-[10px] font-mono tracking-widest uppercase">
                                            {activeSoul || "Core"}
                                        </span>
                                    </div>
                                </div>

                                {/* Footer / Actions */}
                                <div className="flex items-center justify-between px-4 py-2 bg-white/[0.02] border-t border-white/[0.05]">
                                    <div className="flex items-center gap-4">
                                        {useAetherStore((s) => s.predictedGoal) ? (
                                            <div className="flex items-center gap-2 animate-in fade-in slide-in-from-left-2 duration-300">
                                                <span className="text-[9px] text-white/20 uppercase font-mono">Suggested:</span>
                                                <button
                                                    onClick={() => {
                                                        const goal = useAetherStore.getState().predictedGoal;
                                                        if (goal) setInputValue(goal);
                                                    }}
                                                    className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[10px] font-mono hover:bg-cyan-500/20 transition-colors"
                                                >
                                                    <Zap className="w-3 h-3" />
                                                    {useAetherStore((s) => s.predictedGoal)}
                                                </button>
                                            </div>
                                        ) : (
                                            <>
                                                <div className={`flex items-center gap-1 text-[10px] font-mono ${level === 1 ? "text-amber-400" : "text-white/30"}`}>
                                                    <Zap className="w-3 h-3" /> Quick
                                                </div>
                                                <div className={`flex items-center gap-1 text-[10px] font-mono ${level === 2 ? "text-cyan-400" : "text-white/30"}`}>
                                                    <MessageSquare className="w-3 h-3" /> Discuss
                                                </div>
                                                <div className={`flex items-center gap-1 text-[10px] font-mono ${level === 3 ? "text-emerald-400" : "text-white/30"}`}>
                                                    <Bot className="w-3 h-3" /> Agent
                                                </div>
                                            </>
                                        )}
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] text-white/20 font-mono">↵ to execute</span>
                                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded border border-white/10 bg-white/5 text-white/40 text-[9px] font-mono">
                                            ESC
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Status Indicator */}
                            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2">
                                <div className={`w-1 h-1 rounded-full ${status === "connected" ? "bg-emerald-500 shadow-[0_0_8px_#10b981]" : "bg-white/10"}`} />
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <motion.button
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        onClick={toggle}
                        className="group flex items-center gap-3 px-4 py-2.5 bg-[#0a0a0c]/40 backdrop-blur-xl border border-white/[0.05] rounded-full hover:bg-white/[0.08] hover:border-white/10 transition-all pointer-events-auto"
                    >
                        <Search className="w-4 h-4 text-white/30 group-hover:text-white/60 transition-colors" />
                        <span className="text-sm text-white/20 group-hover:text-white/40 transition-colors font-sans">
                            Command...
                        </span>
                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded border border-white/10 bg-white/5 text-white/20 text-[9px] font-mono group-hover:text-white/40 transition-colors">
                            ⌘K
                        </div>
                    </motion.button>
                )}
            </AnimatePresence>
        </div>
    );
}
