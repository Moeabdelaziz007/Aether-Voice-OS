"use client";

/**
 * RealmController — Orchestrates realm transitions.
 *
 * Uses AnimatePresence to animate realm panels in/out.
 * The Orb is rendered separately (always visible).
 */

import { AnimatePresence, motion } from "framer-motion";
import { useRealm } from "@/hooks/useRealm";
import VoidRealm from "./VoidRealm";
import SkillsRealm from "./SkillsRealm";
import MemoryRealm from "./MemoryRealm";
import IdentityRealm from "./IdentityRealm";
import NeuralRealm from "./NeuralRealm";

const REALM_TRANSITION = {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
};

export default function RealmController() {
    const { currentRealm } = useRealm();

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={currentRealm}
                {...REALM_TRANSITION}
                className="absolute inset-0 z-10"
            >
                {currentRealm === "void" && <VoidRealm />}
                {currentRealm === "skills" && <SkillsRealm />}
                {currentRealm === "memory" && <MemoryRealm />}
                {currentRealm === "identity" && <IdentityRealm />}
                {currentRealm === "neural" && <NeuralRealm />}
            </motion.div>
        </AnimatePresence>
    );
}
