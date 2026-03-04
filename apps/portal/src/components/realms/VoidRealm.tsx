"use client";

/**
 * VoidRealm — Home / Default state.
 * Full-screen void with the large orb centered, floating ambient text,
 * and whisper transcripts above/below.
 */

import { useMemo } from "react";
import { motion } from "framer-motion";
import { useAetherStore } from "@/store/useAetherStore";
import AmbientText from "@/components/shared/AmbientText";

export default function VoidRealm() {
    const transcript = useAetherStore((s) => s.transcript);
    const preferences = useAetherStore((s) => s.preferences);

    const lastUser = useMemo(() => {
        if (preferences.transcriptMode === "hidden") return null;
        return [...transcript].reverse().find((m) => m.role === "user");
    }, [transcript, preferences.transcriptMode]);

    const lastAgent = useMemo(() => {
        if (preferences.transcriptMode === "hidden") return null;
        return [...transcript].reverse().find((m) => m.role === "agent");
    }, [transcript, preferences.transcriptMode]);

    return (
        <div className="w-full h-full relative">
            {/* Floating ambient text snippets */}
            <AmbientText />

            {/* User's last words — ghost text above orb */}
            {lastUser && (
                <motion.div
                    key={lastUser.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-[15%] left-1/2 -translate-x-1/2 max-w-[60vw] text-center text-white/20 text-sm italic pointer-events-none z-10"
                >
                    &ldquo;{lastUser.content}&rdquo;
                </motion.div>
            )}

            {/* Agent's response — elegant text below orb */}
            {lastAgent && (
                <motion.div
                    key={lastAgent.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="absolute bottom-[22%] left-1/2 -translate-x-1/2 max-w-[65vw] text-center text-white/70 text-lg font-light tracking-tight pointer-events-none z-10"
                    style={{
                        textShadow: "0 0 40px rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.15)",
                    }}
                >
                    {lastAgent.content}
                </motion.div>
            )}
        </div>
    );
}
