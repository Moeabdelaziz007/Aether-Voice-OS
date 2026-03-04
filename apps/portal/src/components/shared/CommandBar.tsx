"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff } from "lucide-react";
import { useAetherStore } from "@/store/useAetherStore";
import { useRealm, REALM_LABELS, type RealmType } from "@/hooks/useRealm";

const REALM_ORDER: RealmType[] = ["void", "skills", "memory", "identity", "neural"];

/**
 * CommandBar — Floating glassmorphism pill at the bottom.
 * Shows mic icon, state label, soul badge, latency, and realm indicator dots.
 */
export default function CommandBar() {
    const status = useAetherStore((s) => s.status);
    const engineState = useAetherStore((s) => s.engineState);
    const activeSoul = useAetherStore((s) => s.activeSoul);
    const latencyMs = useAetherStore((s) => s.latencyMs);
    const setStatus = useAetherStore((s) => s.setStatus);
    const { currentRealm, navigateTo } = useRealm();

    const isActive = status !== "disconnected";

    const stateLabel = useMemo(() => {
        switch (engineState) {
            case "LISTENING": return "Listening";
            case "THINKING": return "Thinking";
            case "SPEAKING": return "Speaking";
            case "INTERRUPTING": return "Interrupted";
            default: return "Idle";
        }
    }, [engineState]);

    const handleMicClick = () => {
        if (isActive) {
            setStatus("disconnected");
        } else {
            setStatus("connecting");
        }
    };

    return (
        <motion.div
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1 px-3 py-2 bg-[rgba(8,8,12,0.65)] border border-white/[0.08] rounded-full backdrop-blur-3xl shadow-[0_8px_32px_rgba(0,0,0,0.8),inset_0_1px_1px_rgba(255,255,255,0.1)]"
        >
            {/* Mic Button */}
            <button
                onClick={handleMicClick}
                className={`flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 shadow-sm ${isActive
                    ? "bg-[rgba(0,243,255,0.15)] text-cyan-300 shadow-[inset_0_0_12px_rgba(0,243,255,0.3)] border border-cyan-500/30"
                    : "bg-transparent text-white/30 hover:bg-white/[0.05] hover:text-white/60 border border-transparent"
                    }`}
                aria-label={isActive ? "Stop" : "Start"}
            >
                {isActive ? <Mic size={16} /> : <MicOff size={16} />}
            </button>

            {/* State Label */}
            <span className="font-mono text-[11px] tracking-wider text-white/40 px-2 min-w-[70px] text-center uppercase">
                {stateLabel}
            </span>

            {/* Soul Name Badge — shown when a multi-agent soul is active */}
            <AnimatePresence>
                {activeSoul && (
                    <motion.span
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="font-mono text-[9px] tracking-widest text-emerald-400/60 bg-emerald-400/[0.06] px-2 py-0.5 rounded-full border border-emerald-400/10"
                    >
                        {activeSoul}
                    </motion.span>
                )}
            </AnimatePresence>

            {/* Latency indicator — only when connected */}
            {isActive && latencyMs > 0 && (
                <span className="font-mono text-[9px] tracking-wider text-white/20 px-1">
                    {latencyMs}ms
                </span>
            )}

            {/* Divider */}
            <div className="w-px h-5 bg-white/5 mx-1" />

            {/* Realm Indicator Dots */}
            <div className="flex items-center gap-2.5 px-3">
                {REALM_ORDER.map((realm) => (
                    <button
                        key={realm}
                        onClick={() => navigateTo(realm)}
                        title={REALM_LABELS[realm]}
                        aria-label={`Switch to ${REALM_LABELS[realm]} realm`}
                        className={`w-2 h-2 rounded-full transition-all duration-500 hover:scale-150 ${currentRealm === realm
                            ? "bg-cyan-400 shadow-[0_0_12px_rgba(0,243,255,0.8)] scale-125"
                            : "bg-white/10 hover:bg-white/30"
                            }`}
                    />
                ))}
            </div>

            {/* Connection Heartbeat */}
            <div
                className={`w-[6px] h-[6px] rounded-full ml-2 transition-all duration-300 ${status === "error"
                    ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)] animate-pulse"
                    : status === "connecting"
                        ? "bg-amber-400 animate-pulse"
                        : isActive
                            ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]"
                            : "bg-white/10"
                    }`}
            />
        </motion.div>
    );
}
