'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Plus, Edit3, Check, Command } from 'lucide-react';
import { useAetherStore } from '@/store/useAetherStore';
import { useWidgetStore } from '@/store/useWidgetStore';
import UserMenu from '@/components/auth/UserMenu';

interface TopBarProps {
    onOpenSettings: () => void;
    onToggleOmnibar: () => void;
}

import GemigramLogo from '@/components/shared/GemigramLogo';

// ... (existing code)

export default function TopBar({ onOpenSettings, onToggleOmnibar }: TopBarProps) {
    const engineState = useAetherStore((s) => s.engineState);
    const latencyMs = useAetherStore((s) => s.latencyMs);

    // ... (existing constants)

    return (
        <header className="h-14 flex items-center justify-between px-6 border-b border-white/[0.05] bg-black/40 backdrop-blur-3xl">
            {/* Left — Mission Status / Branding */}
            <div className="flex items-center gap-6">
                <GemigramLogo size="sm" className="hidden md:flex" />

                <div className="flex items-center gap-4">
                    {/* Telemetry Status Strip */}
                    <div className="hidden lg:flex items-center gap-2 font-mono text-[9px] uppercase tracking-tighter">
                        <span className="text-white/20">NETWORK:</span>
                        <span className="text-cyan-400">STABLE</span>
                        <span className="text-white/10 mx-1">|</span>
                        <span className="text-white/20">LATENCY:</span>
                        <span className={latencyMs > 100 ? 'text-amber-500' : 'text-emerald-400'}>
                            {latencyMs > 0 ? `${latencyMs}MS` : 'N/A'}
                        </span>
                    </div>

                    <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full animate-pulse`} style={{ backgroundColor: "#06b6d4" }} />
                        <span className="text-[10px] font-black tracking-widest text-white/40 uppercase">
                            CORE::{engineState}
                        </span>
                    </div>
                </div>
            </div>

            {/* Center — Search trigger */}
            <button
                onClick={onToggleOmnibar}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06]
                           hover:bg-white/[0.06] hover:border-white/[0.1] transition-all text-white/20 hover:text-white/40"
            >
                <Command className="w-3 h-3" />
                <span className="text-xs font-mono">Search or command...</span>
                <kbd className="text-[9px] px-1.5 py-0.5 rounded bg-white/[0.05] border border-white/[0.08] font-mono">⌘K</kbd>
            </button>

            {/* Right — Actions + User */}
            <div className="flex items-center gap-2">
                {/* Add Widget */}
                <button
                    onClick={() => useWidgetStore.getState().setStoreOpen(true)}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-mono
                               text-white/30 hover:text-cyan-400 hover:bg-cyan-500/5 border border-transparent
                               hover:border-cyan-500/20 transition-all uppercase tracking-wider"
                >
                    <Plus className="w-3 h-3" />
                    Widget
                </button>

                {/* Edit mode toggle */}
                <button
                    onClick={() => useWidgetStore.getState().setEditMode(!useWidgetStore.getState().editMode)}
                    className={`p-2 rounded-lg transition-all ${useWidgetStore.getState().editMode
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                        : 'text-white/20 hover:text-white/40 hover:bg-white/5'
                        }`}
                    title={useWidgetStore.getState().editMode ? 'Done editing' : 'Edit widgets'}
                >
                    {useWidgetStore.getState().editMode ? <Check className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
                </button>

                {/* Divider */}
                <div className="w-px h-5 bg-white/[0.06]" />

                {/* User menu */}
                <UserMenu onOpenSettings={onOpenSettings} />
            </div>
        </header>
    );
}
