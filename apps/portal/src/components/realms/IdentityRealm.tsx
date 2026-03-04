"use client";

/**
 * IdentityRealm — Agent persona customization.
 * Orb stays center, PersonaPanel slides up from the bottom.
 * Wired to Zustand store for persona/preferences persistence.
 */

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import GlassPanel from "@/components/shared/GlassPanel";
import { useAetherStore } from "@/store/useAetherStore";
import {
    VOICE_TONES,
    EXPERIENCE_LEVELS,
    ACCENT_COLOR_SWATCHES,
    MOCK_SUPERPOWERS,
    type VoiceToneOption,
    type ExperienceLevelOption,
    type SuperpowerItem,
} from "@/lib/mockData";

function SegmentedControl<T extends string>({
    options,
    value,
    onChange,
}: {
    options: readonly T[];
    value: T;
    onChange: (val: T) => void;
}) {
    return (
        <div className="flex gap-1 bg-white/[0.03] rounded-lg p-1">
            {options.map((opt) => (
                <button
                    key={opt}
                    onClick={() => onChange(opt)}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${value === opt
                        ? "bg-cyan-400/15 text-cyan-400 shadow-[0_0_12px_rgba(0,243,255,0.1)]"
                        : "text-white/40 hover:text-white/60 hover:bg-white/[0.03]"
                        }`}
                >
                    {opt}
                </button>
            ))}
        </div>
    );
}

function SuperpowerCard({
    item,
    index,
    onToggle,
}: {
    item: SuperpowerItem;
    index: number;
    onToggle: () => void;
}) {
    return (
        <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 + index * 0.06 }}
            onClick={onToggle}
            className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-200 text-left ${item.enabled
                ? "bg-cyan-400/10 border-cyan-400/20 shadow-[0_0_15px_rgba(0,243,255,0.08)]"
                : "bg-white/[0.03] border-white/[0.06] hover:bg-white/[0.05]"
                }`}
        >
            <span className="text-xl select-none">{item.icon}</span>
            <span
                className={`text-xs font-medium ${item.enabled ? "text-white/90" : "text-white/40"
                    }`}
            >
                {item.name}
            </span>
        </motion.button>
    );
}

export default function IdentityRealm() {
    // ── Live store bindings ──
    const persona = useAetherStore((s) => s.persona);
    const preferences = useAetherStore((s) => s.preferences);
    const setPersona = useAetherStore((s) => s.setPersona);
    const setPreferences = useAetherStore((s) => s.setPreferences);
    const activeSoul = useAetherStore((s) => s.activeSoul);

    // Superpowers are local UI state (not backend data)
    const [superpowers, setSuperpowers] = useState<SuperpowerItem[]>(MOCK_SUPERPOWERS);

    const toggleSuperpower = useCallback((id: string) => {
        setSuperpowers((prev) =>
            prev.map((sp) => (sp.id === id ? { ...sp, enabled: !sp.enabled } : sp))
        );
    }, []);

    return (
        <div className="w-full h-full flex items-end justify-center">
            {/* Persona Panel — slides up from bottom */}
            <motion.div
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                exit={{ y: "100%" }}
                transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="w-full max-w-3xl h-[60vh] bg-[rgba(10,10,18,0.95)] backdrop-blur-2xl border border-white/[0.06] border-b-0 rounded-t-3xl overflow-y-auto no-scrollbar"
            >
                <div className="p-8 space-y-8">
                    {/* Drag Handle */}
                    <div className="flex justify-center">
                        <div className="w-10 h-1 rounded-full bg-white/10" />
                    </div>

                    {/* Agent Name — synced with store */}
                    <div>
                        <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-3">
                            Agent Name
                        </label>
                        <input
                            type="text"
                            value={persona.name}
                            onChange={(e) => setPersona({ name: e.target.value })}
                            placeholder="Enter agent name"
                            className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl px-4 py-3 text-2xl font-bold text-white/90 outline-none focus:border-cyan-400/30 transition-colors duration-200"
                        />
                    </div>

                    {/* Voice Info — Gemini attribution + active soul */}
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-2">
                                Voice Engine
                            </label>
                            <span className="text-white/60 text-sm font-mono">
                                Puck · <span className="text-cyan-400/60">Gemini Live API</span>
                            </span>
                        </div>
                        {activeSoul && (
                            <div>
                                <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-2">
                                    Active Soul
                                </label>
                                <span className="text-emerald-400/80 text-sm font-mono">
                                    {activeSoul}
                                </span>
                            </div>
                        )}
                    </div>

                    {/* Voice Tone — synced with store */}
                    <div>
                        <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-3">
                            Voice Tone
                        </label>
                        <SegmentedControl
                            options={VOICE_TONES}
                            value={persona.voiceTone as VoiceToneOption}
                            onChange={(val) => setPersona({ voiceTone: val })}
                        />
                    </div>

                    {/* Experience Level — synced with store */}
                    <div>
                        <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-3">
                            Experience Level
                        </label>
                        <SegmentedControl
                            options={EXPERIENCE_LEVELS}
                            value={persona.experienceLevel as ExperienceLevelOption}
                            onChange={(val) => setPersona({ experienceLevel: val })}
                        />
                    </div>

                    {/* Accent Color — synced with store */}
                    <div>
                        <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-3">
                            Accent Color
                        </label>
                        <div className="flex gap-4">
                            {ACCENT_COLOR_SWATCHES.map((swatch) => (
                                <button
                                    key={swatch.id}
                                    onClick={() => setPreferences({ accentColor: swatch.id })}
                                    className={`w-8 h-8 rounded-full transition-all duration-200 ${preferences.accentColor === swatch.id
                                        ? "ring-2 ring-white/80 ring-offset-2 ring-offset-[#020206] scale-110"
                                        : "hover:scale-110"
                                        }`}
                                    style={{
                                        backgroundColor: swatch.color,
                                        boxShadow:
                                            preferences.accentColor === swatch.id
                                                ? `0 0 16px ${swatch.color}60`
                                                : "none",
                                    }}
                                    aria-label={`Set accent to ${swatch.id}`}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Superpowers */}
                    <div>
                        <label className="block text-white/30 text-xs uppercase tracking-[0.15em] font-mono mb-3">
                            Superpowers
                        </label>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                            {superpowers.map((sp, i) => (
                                <SuperpowerCard
                                    key={sp.id}
                                    item={sp}
                                    index={i}
                                    onToggle={() => toggleSuperpower(sp.id)}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
