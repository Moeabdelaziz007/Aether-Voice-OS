"use client";

import { cn } from "@/lib/utils";
import { Activity, Mic, Brain, MessageSquare, AlertTriangle } from "lucide-react";

type StateType = "IDLE" | "LISTENING" | "THINKING" | "SPEAKING" | "INTERRUPTING";

const STATES: { id: StateType; label: string; icon: React.ElementType }[] = [
    { id: "IDLE", label: "Standby", icon: Activity },
    { id: "LISTENING", label: "Acoustic Input", icon: Mic },
    { id: "THINKING", label: "Cognitive Load", icon: Brain },
    { id: "SPEAKING", label: "Synthesis Output", icon: MessageSquare },
    { id: "INTERRUPTING", label: "Thalamic Override", icon: AlertTriangle },
];

export function StateVisualizer({ currentState = "LISTENING", className }: { currentState?: StateType, className?: string }) {
    return (
        <div className={cn("glass-panel rounded-2xl p-6 flex flex-col justify-between", className)}>
            <h3 className="text-sm font-mono tracking-widest text-[#9d4edd] uppercase mb-8">
                System State Machine
            </h3>

            <div className="flex items-center justify-between relative">
                {/* Connecting line */}
                <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-gray-800 -z-10 -translate-y-1/2" />

                {STATES.map((state) => {
                    const isActive = state.id === currentState;
                    const isInterrupt = state.id === "INTERRUPTING";

                    return (
                        <div key={state.id} className="flex flex-col items-center gap-3">
                            <div
                                className={cn(
                                    "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-500",
                                    isActive
                                        ? isInterrupt
                                            ? "bg-[#ff3333] shadow-[0_0_20px_rgba(255,51,51,0.6)] animate-pulse"
                                            : "bg-[#00f0ff] shadow-[0_0_20px_rgba(0,240,255,0.5)]"
                                        : "bg-[#18181b] border border-[#27272a]"
                                )}
                            >
                                <state.icon
                                    className={cn(
                                        "w-5 h-5",
                                        isActive ? (isInterrupt ? "text-white" : "text-black") : "text-gray-500"
                                    )}
                                />
                            </div>
                            <span
                                className={cn(
                                    "text-[10px] uppercase tracking-wider font-mono text-center max-w-[80px]",
                                    isActive
                                        ? isInterrupt ? "text-[#ff3333] glow-text-red font-bold" : "text-[#00f0ff] glow-text-blue"
                                        : "text-gray-500"
                                )}
                            >
                                {state.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
