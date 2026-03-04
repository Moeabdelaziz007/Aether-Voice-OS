"use client";

/**
 * SkillsRealm — Neural Capabilities grid.
 * Orb is at 120px top-center (handled by RealmController/AetherOrb).
 * Shows a responsive grid of skill cards below.
 */

import { useState } from "react";
import { motion } from "framer-motion";
import GlassPanel from "@/components/shared/GlassPanel";
import { MOCK_SKILLS, type SkillItem } from "@/lib/mockData";

function SkillCard({ skill, index, onToggle }: { skill: SkillItem; index: number; onToggle: () => void }) {
    return (
        <GlassPanel
            hover
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
                delay: index * 0.08,
                type: "spring",
                stiffness: 260,
                damping: 20,
            }}
            className="relative cursor-default"
        >
            {/* Toggle Switch */}
            <button
                onClick={onToggle}
                className="absolute top-4 right-4 w-10 h-5 rounded-full transition-colors duration-200 flex items-center"
                style={{
                    backgroundColor: skill.enabled ? "rgba(0,243,255,0.3)" : "rgba(255,255,255,0.08)",
                }}
                aria-label={`Toggle ${skill.name}`}
            >
                <motion.div
                    className="w-4 h-4 rounded-full bg-white shadow-sm"
                    animate={{ x: skill.enabled ? 22 : 2 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
            </button>

            {/* Icon */}
            <div className="text-3xl mb-3 select-none">{skill.icon}</div>

            {/* Name */}
            <h3 className="text-white/90 font-semibold text-sm mb-1">{skill.name}</h3>

            {/* Description */}
            <p className="text-white/50 text-xs leading-relaxed">{skill.description}</p>
        </GlassPanel>
    );
}

export default function SkillsRealm() {
    const [skills, setSkills] = useState<SkillItem[]>(MOCK_SKILLS);

    const toggleSkill = (id: string) => {
        setSkills((prev) =>
            prev.map((s) => (s.id === id ? { ...s, enabled: !s.enabled } : s))
        );
    };

    return (
        <div className="w-full h-full flex flex-col items-center pt-[22%] px-6 overflow-y-auto no-scrollbar">
            {/* Section Title */}
            <motion.h2
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-white/30 text-xs uppercase tracking-[0.2em] font-mono mb-6"
            >
                Neural Capabilities
            </motion.h2>

            {/* Skills Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 w-full max-w-4xl pb-24">
                {skills.map((skill, i) => (
                    <SkillCard
                        key={skill.id}
                        skill={skill}
                        index={i}
                        onToggle={() => toggleSkill(skill.id)}
                    />
                ))}
            </div>
        </div>
    );
}
