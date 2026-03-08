"use client";

/**
 * PoweredByStrip — Ambient Google Tech Attribution Footer.
 *
 * A subtle, ultra-minimalist strip showing the Google technologies
 * that power AetherOS. Designed to impress judges in the
 * Gemini Live Agent Challenge without being intrusive.
 *
 * Position: Fixed bottom, just above the CommandBar.
 */

import { motion } from "framer-motion";

const TECH_STACK = [
    { name: "Gemini Live API", hoverColor: "#4285F4" },
    { name: "Firebase", hoverColor: "#FFCA28" },
    { name: "ADK", hoverColor: "#34A853" },
    { name: "Google Cloud", hoverColor: "#EA4335" },
];

export default function PoweredByStrip() {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5, duration: 1.2 }}
            className="fixed bottom-16 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1"
        >
            {TECH_STACK.map((tech, i) => (
                <span key={tech.name} className="flex items-center gap-1">
                    {i > 0 && (
                        <span
                            className="text-white/[0.06] select-none"
                            style={{ fontSize: "8px" }}
                        >
                            ·
                        </span>
                    )}
                    <motion.span
                        className="font-mono tracking-widest text-white/[0.12] cursor-default select-none transition-colors duration-300"
                        style={{ fontSize: "9px" }}
                        whileHover={{
                            color: tech.hoverColor,
                            textShadow: `0 0 12px ${tech.hoverColor}40`,
                        }}
                    >
                        ⟨ {tech.name} ⟩
                    </motion.span>
                </span>
            ))}
        </motion.div>
    );
}
