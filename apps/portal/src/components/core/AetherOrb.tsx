"use client";

/**
 * AetherOrb — layoutId wrapper around the 3D neural orb.
 *
 * Uses Framer Motion layoutId for seamless position/size
 * transitions between realms. The inner 3D scene (AetherCore)
 * remains unchanged.
 */

import { motion } from "framer-motion";
import { useRealm } from "@/hooks/useRealm";
import AetherCore from "@/components/AetherCore";

const REALM_TRANSITION = {
    duration: 0.6,
    ease: [0.16, 1, 0.3, 1] as const,
};

export default function AetherOrb() {
    const { orbConfig, currentRealm } = useRealm();

    return (
        <motion.div
            layoutId="aether-orb"
            className="absolute z-20"
            style={{
                left: orbConfig.x,
                top: orbConfig.y,
                transform: "translate(-50%, -50%)",
            }}
            animate={{
                width: orbConfig.size,
                height: orbConfig.size,
            }}
            transition={REALM_TRANSITION}
        >
            {/* Ambient glow aura */}
            <motion.div
                className="absolute inset-[-30%] rounded-full pointer-events-none"
                style={{
                    background: `radial-gradient(circle, rgba(var(--accent-r),var(--accent-g),var(--accent-b),${0.12 * orbConfig.glow}) 0%, transparent 70%)`,
                    filter: "blur(40px)",
                }}
                animate={{
                    scale: [1, 1.08, 1],
                    opacity: [0.7, 1, 0.7],
                }}
                transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
            />

            {/* 3D Scene */}
            <div className="w-full h-full">
                <AetherCore />
            </div>

            {/* State label — only in void realm */}
            {currentRealm === "void" && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute -bottom-10 left-1/2 -translate-x-1/2 font-mono text-[10px] tracking-[0.2em] uppercase text-white/10 select-none pointer-events-none"
                >
                    aether
                </motion.div>
            )}
        </motion.div>
    );
}
