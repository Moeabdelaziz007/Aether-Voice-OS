"use client";

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ExternalLink,
    Maximize2,
    Minimize2,
    X,
    Search,
    Zap,
    Plus,
    CheckCircle2,
    Globe,
    RefreshCw,
    ArrowLeft,
    Sparkles,
    Shield,
} from 'lucide-react';
import { useForgeStore } from '@/store/useForgeStore';

/* ─────────────────────────────────────────────
   ClawHub Skill Categories — Quick‑inject pills
   ───────────────────────────────────────────── */
const SKILL_CATEGORIES = [
    { id: 'all', label: 'All', icon: Globe },
    { id: 'coding', label: 'Coding', icon: Zap },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'data', label: 'Data', icon: Search },
    { id: 'creative', label: 'Creative', icon: Sparkles },
];

/* ─────────────────────────────────────────────
   Featured skills from ClawHub (mock registry)
   ───────────────────────────────────────────── */
const FEATURED_SKILLS = [
    { id: 'sql-architect', label: 'SQL Architecture', category: 'data', desc: 'Advanced query optimization & schema design', aura: 9.4 },
    { id: 'rust-optimizer', label: 'Rust Hot-Path Opt', category: 'coding', desc: 'Zero-cost abstractions & performance tuning', aura: 9.1 },
    { id: 'threejs-master', label: '3D Scene Mastery', category: 'creative', desc: 'WebGL pipelines, shaders & spatial computing', aura: 8.8 },
    { id: 'pentest-auditor', label: 'Security Auditing', category: 'security', desc: 'Penetration testing & vulnerability assessment', aura: 9.6 },
    { id: 'react-architect', label: 'React Architecture', category: 'coding', desc: 'Component patterns, SSR & state machines', aura: 9.2 },
    { id: 'ml-pipeline', label: 'ML Pipeline', category: 'data', desc: 'Training loops, feature engineering & deployment', aura: 8.9 },
    { id: 'api-designer', label: 'API Designer', category: 'coding', desc: 'REST/GraphQL schema design & versioning', aura: 8.7 },
    { id: 'prompt-engineer', label: 'Prompt Engineering', category: 'creative', desc: 'Advanced prompt patterns & chain-of-thought', aura: 9.3 },
];

type WidgetMode = 'compact' | 'expanded' | 'browser';

export default function ClawHubWidget() {
    const { dna, updateDNA } = useForgeStore();
    const [mode, setMode] = useState<WidgetMode>('compact');
    const [activeCategory, setActiveCategory] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [injecting, setInjecting] = useState<string | null>(null);

    const filteredSkills = FEATURED_SKILLS.filter(skill => {
        const matchesCategory = activeCategory === 'all' || skill.category === activeCategory;
        const matchesSearch = !searchQuery || skill.label.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    const injectSkill = useCallback((skillId: string) => {
        // Enforce basic injection sanitization to guard against XSS/Path Traversal
        // passing through the widget. Skill IDs should strictly be alphanumeric/hyphens.
        const cleanSkillId = skillId.replace(/[^a-zA-Z0-9-]/g, '').slice(0, 64);

        if (!cleanSkillId) return;

        setInjecting(cleanSkillId);
        // Simulate injection with neural animation delay
        setTimeout(() => {
            const exists = dna.skills.includes(cleanSkillId);
            if (!exists) {
                updateDNA({ skills: [...dna.skills, cleanSkillId] });
            }
            setInjecting(null);
        }, 800);
    }, [dna.skills, updateDNA]);

    const removeSkill = useCallback((skillId: string) => {
        updateDNA({ skills: dna.skills.filter(s => s !== skillId) });
    }, [dna.skills, updateDNA]);

    const isSkillInjected = (id: string) => dna.skills.includes(id);

    return (
        <motion.div
            layout
            className={`relative overflow-hidden transition-all duration-500 ${
                mode === 'browser'
                    ? 'fixed inset-4 z-50 rounded-[32px]'
                    : mode === 'expanded'
                        ? 'w-full rounded-[32px]'
                        : 'w-full rounded-[24px]'
            }`}
        >
            {/* Backdrop for browser mode */}
            <AnimatePresence>
                {mode === 'browser' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/80 backdrop-blur-xl z-40"
                        onClick={() => setMode('expanded')}
                    />
                )}
            </AnimatePresence>

            <motion.div
                layout
                className={`relative bg-black/60 backdrop-blur-[40px] border border-white/[0.08] overflow-hidden flex flex-col ${
                    mode === 'browser'
                        ? 'fixed inset-4 z-50 rounded-[32px] shadow-[0_32px_128px_rgba(0,243,255,0.15)]'
                        : mode === 'expanded'
                            ? 'rounded-[32px] shadow-[0_16px_64px_rgba(0,0,0,0.6)]'
                            : 'rounded-[24px] shadow-[0_8px_32px_rgba(0,0,0,0.4)]'
                }`}
            >
                {/* ─── Header Bar ─── */}
                <div className="px-5 py-3 border-b border-white/[0.06] flex items-center justify-between bg-white/[0.02]">
                    <div className="flex items-center gap-3">
                        {mode === 'browser' && (
                            <button
                                onClick={() => setMode('expanded')}
                                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4 text-white/40" />
                            </button>
                        )}
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.6)]" />
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/50">
                                ClawHub
                            </span>
                            <span className="text-[10px] font-mono text-cyan-400/60">// SKILL FORGE</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-1.5">
                        {dna.skills.length > 0 && (
                            <div className="px-2.5 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full mr-2">
                                <span className="text-[9px] font-black text-cyan-400 uppercase tracking-widest">
                                    {dna.skills.length} INJECTED
                                </span>
                            </div>
                        )}
                        <button
                            onClick={() => setMode(mode === 'browser' ? 'expanded' : 'browser')}
                            className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                            title="Open ClawHub Browser"
                        >
                            {mode === 'browser' ? (
                                <Minimize2 className="w-3.5 h-3.5 text-white/40" />
                            ) : (
                                <Maximize2 className="w-3.5 h-3.5 text-white/40" />
                            )}
                        </button>
                        {mode === 'browser' && (
                            <button
                                onClick={() => setMode('compact')}
                                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                            >
                                <X className="w-3.5 h-3.5 text-white/40" />
                            </button>
                        )}
                    </div>
                </div>

                {/* ─── Content Area ─── */}
                <AnimatePresence mode="wait">
                    {mode === 'browser' ? (
                        /* ─── Full Browser Mode: iframe ─── */
                        <motion.div
                            key="browser"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex-1 flex flex-col"
                        >
                            {/* Browser URL Bar */}
                            <div className="px-5 py-2.5 border-b border-white/[0.04] flex items-center gap-3 bg-white/[0.01]">
                                <div className="flex-1 flex items-center gap-2 bg-white/[0.04] rounded-xl px-4 py-2 border border-white/[0.06]">
                                    <Globe className="w-3.5 h-3.5 text-cyan-400/60" />
                                    <span className="text-xs text-white/60 font-mono">https://www.clawhub.ai</span>
                                    <Shield className="w-3 h-3 text-green-400/60 ml-auto" />
                                </div>
                                <a
                                    href="https://www.clawhub.ai"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                                >
                                    <ExternalLink className="w-3.5 h-3.5 text-white/30" />
                                </a>
                            </div>

                            {/* iframe Container */}
                            <div className="flex-1 relative">
                                <iframe
                                    src="https://www.clawhub.ai"
                                    className="w-full h-full border-0"
                                    style={{ minHeight: '500px' }}
                                    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                                    title="ClawHub — AI Skills Marketplace"
                                />

                                {/* Floating Inject Panel */}
                                <motion.div
                                    initial={{ y: 20, opacity: 0 }}
                                    animate={{ y: 0, opacity: 1 }}
                                    transition={{ delay: 0.5 }}
                                    className="absolute bottom-4 right-4 left-4 bg-black/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4"
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="text-[9px] font-mono text-cyan-400/60 uppercase tracking-widest mb-1">
                                                Neural Injection Ready
                                            </div>
                                            <p className="text-xs text-white/50">
                                                Browse ClawHub skills above, then inject them into your agent&apos;s DNA below.
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="px-3 py-1.5 bg-cyan-500/10 rounded-full">
                                                <span className="text-[10px] font-black text-cyan-400">
                                                    {dna.skills.length} Skills Loaded
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            </div>
                        </motion.div>
                    ) : (
                        /* ─── Compact / Expanded: Skill Cards ─── */
                        <motion.div
                            key="cards"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-col"
                        >
                            {/* Search + Category Filters */}
                            <div className="px-5 py-3 space-y-3">
                                {/* Search */}
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/20" />
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        placeholder="Search skills..."
                                        className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl py-2 pl-9 pr-4 text-xs text-white/80 placeholder:text-white/20 focus:outline-none focus:border-cyan-500/30 transition-all"
                                    />
                                </div>

                                {/* Category Pills */}
                                <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hidden">
                                    {SKILL_CATEGORIES.map(cat => (
                                        <button
                                            key={cat.id}
                                            onClick={() => setActiveCategory(cat.id)}
                                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[9px] font-bold uppercase tracking-widest whitespace-nowrap transition-all ${
                                                activeCategory === cat.id
                                                    ? 'bg-cyan-500/15 border border-cyan-500/30 text-cyan-400'
                                                    : 'bg-white/[0.03] border border-white/[0.06] text-white/30 hover:text-white/50'
                                            }`}
                                        >
                                            <cat.icon className="w-3 h-3" />
                                            {cat.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Skill Cards Grid */}
                            <div className={`px-5 pb-4 grid gap-2.5 ${
                                mode === 'expanded' ? 'grid-cols-2' : 'grid-cols-1'
                            } max-h-[320px] overflow-y-auto custom-scrollbar`}>
                                {filteredSkills.map((skill) => {
                                    const injected = isSkillInjected(skill.id);
                                    const isInjecting = injecting === skill.id;

                                    return (
                                        <motion.div
                                            key={skill.id}
                                            layout
                                            initial={{ opacity: 0, scale: 0.95 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            className={`group relative p-4 rounded-2xl border transition-all cursor-pointer ${
                                                injected
                                                    ? 'bg-cyan-500/[0.08] border-cyan-500/30'
                                                    : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.04]'
                                            }`}
                                            onClick={() => injected ? removeSkill(skill.id) : injectSkill(skill.id)}
                                        >
                                            {/* Injection Pulse Animation */}
                                            <AnimatePresence>
                                                {isInjecting && (
                                                    <motion.div
                                                        initial={{ scale: 0, opacity: 0 }}
                                                        animate={{ scale: 2.5, opacity: [0.3, 0] }}
                                                        exit={{ opacity: 0 }}
                                                        transition={{ duration: 0.8 }}
                                                        className="absolute inset-0 bg-cyan-400 rounded-2xl pointer-events-none"
                                                    />
                                                )}
                                            </AnimatePresence>

                                            <div className="relative z-10 flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className={`text-xs font-bold ${
                                                            injected ? 'text-cyan-400' : 'text-white/70'
                                                        }`}>
                                                            {skill.label}
                                                        </span>
                                                        {injected && (
                                                            <CheckCircle2 className="w-3 h-3 text-cyan-400" />
                                                        )}
                                                    </div>
                                                    <p className="text-[9px] text-white/30 leading-relaxed mb-2">{skill.desc}</p>
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-[8px] font-mono text-purple-400/60 uppercase tracking-widest px-1.5 py-0.5 bg-purple-500/10 rounded">
                                                            {skill.category}
                                                        </span>
                                                        <span className="text-[8px] font-mono text-amber-400/60">
                                                            ★ {skill.aura}
                                                        </span>
                                                    </div>
                                                </div>

                                                <div className={`p-2 rounded-xl transition-all ${
                                                    injected
                                                        ? 'bg-cyan-500/20 text-cyan-400'
                                                        : 'bg-white/[0.04] text-white/20 group-hover:text-white/40'
                                                }`}>
                                                    {isInjecting ? (
                                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                                    ) : injected ? (
                                                        <CheckCircle2 className="w-4 h-4" />
                                                    ) : (
                                                        <Plus className="w-4 h-4" />
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </div>

                            {/* Footer: Open Full Browser */}
                            <div className="px-5 py-3 border-t border-white/[0.04] flex items-center justify-between">
                                <div className="text-[9px] text-white/20 font-mono uppercase tracking-widest">
                                    Powered by clawhub.ai
                                </div>
                                <button
                                    onClick={() => setMode('browser')}
                                    className="flex items-center gap-2 px-4 py-2 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] rounded-xl text-[10px] font-bold text-cyan-400 uppercase tracking-widest transition-all"
                                >
                                    <Globe className="w-3 h-3" />
                                    Browse Full Catalog
                                    <ExternalLink className="w-3 h-3 opacity-40" />
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </motion.div>
    );
}
