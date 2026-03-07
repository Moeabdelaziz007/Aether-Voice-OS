'use client';

import React from 'react';
import { UserCircle, Mic } from 'lucide-react';
import { useAetherStore, VOICE_TONE_PROMPTS, type VoiceTone } from '@/store/useAetherStore';

const VOICE_TONES: { id: VoiceTone; label: string; emoji: string }[] = [
    { id: 'professional', label: 'Professional', emoji: '👔' },
    { id: 'casual', label: 'Casual', emoji: '😎' },
    { id: 'friendly', label: 'Friendly', emoji: '🤗' },
    { id: 'mentor', label: 'Mentor', emoji: '🧙' },
    { id: 'minimal', label: 'Minimal', emoji: '⚡' },
];

const FORMALITY_OPTIONS = [
    { id: 'formal' as const, label: 'Formal' },
    { id: 'casual' as const, label: 'Casual' },
    { id: 'technical' as const, label: 'Technical' },
];

const VERBOSITY_OPTIONS = [
    { id: 'concise' as const, label: 'Concise' },
    { id: 'balanced' as const, label: 'Balanced' },
    { id: 'verbose' as const, label: 'Verbose' },
];

export default function PersonaPanel() {
    const preferences = useAetherStore((s) => s.preferences);
    const setPreferences = useAetherStore((s) => s.setPreferences);
    const personaConfig = useAetherStore((s) => s.personaConfig);
    const setPersonaConfig = useAetherStore((s) => s.setPersonaConfig);

    return (
        <div className="flex flex-col h-full gap-6">
            {/* Header */}
            <div className="flex items-center gap-2">
                <UserCircle className="w-5 h-5 text-amber-400" />
                <h2 className="text-lg font-medium text-white/90">Persona & Voice</h2>
            </div>

            {/* Persona Name */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    AI Name
                </label>
                <input
                    type="text"
                    value={preferences.personaName}
                    onChange={(e) => setPreferences({ personaName: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-sm text-white/70 outline-none focus:border-cyan-500/30 transition-colors"
                />
            </div>

            {/* Persona Role */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    Role
                </label>
                <input
                    type="text"
                    value={preferences.personaRole}
                    onChange={(e) => setPreferences({ personaRole: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-sm text-white/70 outline-none focus:border-cyan-500/30 transition-colors"
                />
            </div>

            {/* Voice Tone */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    <Mic className="w-3 h-3 inline mr-1" /> Voice Tone
                </label>
                <div className="grid grid-cols-5 gap-2">
                    {VOICE_TONES.map((tone) => (
                        <button
                            key={tone.id}
                            onClick={() => setPreferences({ voiceTone: tone.id })}
                            className={`flex flex-col items-center gap-1 p-2.5 rounded-lg border transition-all ${
                                preferences.voiceTone === tone.id
                                    ? 'bg-cyan-500/10 border-cyan-500/30 text-white/80'
                                    : 'bg-white/[0.02] border-white/[0.06] text-white/30 hover:text-white/50 hover:border-white/10'
                            }`}
                        >
                            <span className="text-lg">{tone.emoji}</span>
                            <span className="text-[9px] font-mono">{tone.label}</span>
                        </button>
                    ))}
                </div>
                {/* Tone preview */}
                <div className="mt-2 p-2 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                    <p className="text-[10px] text-white/20 italic">
                        {VOICE_TONE_PROMPTS[preferences.voiceTone]}
                    </p>
                </div>
            </div>

            {/* Formality */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    Formality
                </label>
                <div className="flex gap-2">
                    {FORMALITY_OPTIONS.map((opt) => (
                        <button
                            key={opt.id}
                            onClick={() => setPersonaConfig({ formality: opt.id })}
                            className={`flex-1 py-2 rounded-lg text-xs font-medium border transition-all ${
                                personaConfig.formality === opt.id
                                    ? 'bg-white/[0.08] border-white/[0.15] text-white/70'
                                    : 'bg-white/[0.02] border-white/[0.06] text-white/30 hover:text-white/50'
                            }`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Verbosity */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    Verbosity
                </label>
                <div className="flex gap-2">
                    {VERBOSITY_OPTIONS.map((opt) => (
                        <button
                            key={opt.id}
                            onClick={() => setPersonaConfig({ verbosity: opt.id })}
                            className={`flex-1 py-2 rounded-lg text-xs font-medium border transition-all ${
                                personaConfig.verbosity === opt.id
                                    ? 'bg-white/[0.08] border-white/[0.15] text-white/70'
                                    : 'bg-white/[0.02] border-white/[0.06] text-white/30 hover:text-white/50'
                            }`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Custom Prompt */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    Custom System Prompt (Optional)
                </label>
                <textarea
                    value={personaConfig.customPrompt || ''}
                    onChange={(e) => setPersonaConfig({ customPrompt: e.target.value })}
                    placeholder="Add custom instructions for the AI persona..."
                    rows={3}
                    className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-white/60 placeholder:text-white/15 outline-none focus:border-cyan-500/30 transition-colors resize-none"
                />
            </div>

            {/* Greeting */}
            <div>
                <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">
                    Greeting Message
                </label>
                <input
                    type="text"
                    value={preferences.greeting}
                    onChange={(e) => setPreferences({ greeting: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-sm text-white/70 outline-none focus:border-cyan-500/30 transition-colors"
                />
            </div>
        </div>
    );
}
