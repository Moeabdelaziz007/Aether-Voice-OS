"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { Mic, MicOff } from "lucide-react";
import { useAetherStore } from "@/store/useAetherStore";
import { useRealm, REALM_LABELS, type RealmType } from "@/hooks/useRealm";

const REALM_ORDER: RealmType[] = ["void", "skills", "memory", "identity", "neural"];

/**
 * CommandBar — Floating glassmorphism pill at the bottom.
 * Shows mic icon, state label, and realm indicator dots.
 */
export default function CommandBar() {
    const status = useAetherStore((s) => s.status);
    const engineState = useAetherStore((s) => s.engineState);
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
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1 px-2 py-1.5 bg-[rgba(12,12,20,0.7)] border border-white/[0.06] rounded-full backdrop-blur-2xl shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
        >
            {/* Mic Button */}
            <button
                onClick={handleMicClick}
                className={`flex items-center justify-center w-9 h-9 rounded-full transition-all duration-150 ${
                    isActive
                        ? "bg-[rgba(0,243,255,0.1)] text-white"
                        : "bg-transparent text-white/20 hover:bg-white/[0.03] hover:text-white/40"
                }`}
                aria-label={isActive ? "Stop" : "Start"}
            >
                {isActive ? <Mic size={16} /> : <MicOff size={16} />}
            </button>

            {/* State Label */}
            <span className="font-mono text-[11px] tracking-wider text-white/40 px-2 min-w-[70px] text-center uppercase">
                {stateLabel}
            </span>

            {/* Divider */}
            <div className="w-px h-5 bg-white/5 mx-1" />

            {/* Realm Indicator Dots */}
            <div className="flex items-center gap-2 px-2">
                {REALM_ORDER.map((realm) => (
                    <button
                        key={realm}
                        onClick={() => navigateTo(realm)}
                        title={REALM_LABELS[realm]}
                        aria-label={`Switch to ${REALM_LABELS[realm]} realm`}
                        className={`w-[6px] h-[6px] rounded-full transition-all duration-300 ${
                            currentRealm === realm
                                ? "bg-cyan-400 shadow-[0_0_8px_rgba(0,243,255,0.5)] scale-125"
                                : "bg-white/10 hover:bg-white/20"
                        }`}
                    />
                ))}
            </div>

            {/* Connection Heartbeat */}
            <div
                className={`w-[6px] h-[6px] rounded-full ml-2 transition-all duration-300 ${
                    status === "error"
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
