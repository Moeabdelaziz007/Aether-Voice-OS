"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const AMBIENT_PHRASES = [
    "Listening...",
    "Ready to assist...",
    "Analyzing patterns...",
    "Processing context...",
    "Standing by...",
    "Awaiting input...",
];

interface FloatingText {
    id: number;
    text: string;
    x: number;
    y: number;
}

/**
 * AmbientText — Floating ephemeral text snippets around the orb.
 * They fade in/out randomly for an atmospheric feel.
 */
export default function AmbientText() {
    const [texts, setTexts] = useState<FloatingText[]>([]);

    useEffect(() => {
        const spawn = () => {
            const phrase = AMBIENT_PHRASES[Math.floor(Math.random() * AMBIENT_PHRASES.length)];
            const id = Date.now() + Math.random();

            // Random position around center, avoiding the orb area
            const angle = Math.random() * Math.PI * 2;
            const dist = 200 + Math.random() * 180;
            const x = 50 + (Math.cos(angle) * dist) / 10;
            const y = 45 + (Math.sin(angle) * dist) / 8;

            setTexts((prev) => [...prev.slice(-3), { id, text: phrase, x, y }]);

            // Remove after 3-5s
            setTimeout(() => {
                setTexts((prev) => prev.filter((t) => t.id !== id));
            }, 3000 + Math.random() * 2000);
        };

        // Spawn periodically
        const interval = setInterval(spawn, 2500 + Math.random() * 2000);
        spawn(); // Initial spawn

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed inset-0 pointer-events-none z-[5]">
            <AnimatePresence>
                {texts.map((t) => (
                    <motion.span
                        key={t.id}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        transition={{ duration: 0.8 }}
                        className="absolute text-white/15 text-sm font-light tracking-wide select-none"
                        style={{ left: `${t.x}%`, top: `${t.y}%`, transform: "translate(-50%, -50%)" }}
                    >
                        {t.text}
                    </motion.span>
                ))}
            </AnimatePresence>
        </div>
    );
}
