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

export default function TopBar({ onOpenSettings, onToggleOmnibar }: TopBarProps) {
    const engineState = useAetherStore((s) => s.engineState);
    const latencyMs = useAetherStore((s) => s.latencyMs);
    const editMode = useWidgetStore((s) => s.editMode);
    const setEditMode = useWidgetStore((s) => s.setEditMode);
    const setStoreOpen = useWidgetStore((s) => s.setStoreOpen);

    const stateColor = {
        IDLE: '#4b5563',
        LISTENING: '#39ff14',
        THINKING: '#ffd700',
        SPEAKING: '#00ff88',
        INTERRUPTING: '#ff1744',
    }[engineState] || '#4b5563';

    return (
        <header className="h-12 flex items-center justify-between px-4 border-b border-white/[0.06] bg-black/20 backdrop-blur-xl">
            {/* Left — Status */}
            <div className="flex items-center gap-3">
                {/* Engine state */}
                <div className="flex items-center gap-2">
                    <motion.div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: stateColor }}
                        animate={{ scale: engineState !== 'IDLE' ? [1, 1.3, 1] : 1 }}
                        transition={{ duration: 1.5, repeat: engineState !== 'IDLE' ? Infinity : 0 }}
                    />
                    <span className="text-[10px] font-mono text-white/30 uppercase tracking-wider">
                        {engineState}
                    </span>
                </div>

                {/* Latency */}
                {latencyMs > 0 && (
                    <span className="text-[9px] font-mono text-white/15">
                        {latencyMs}ms
                    </span>
                )}
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
                    onClick={() => setStoreOpen(true)}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-mono
                               text-white/30 hover:text-cyan-400 hover:bg-cyan-500/5 border border-transparent
                               hover:border-cyan-500/20 transition-all uppercase tracking-wider"
                >
                    <Plus className="w-3 h-3" />
                    Widget
                </button>

                {/* Edit mode toggle */}
                <button
                    onClick={() => setEditMode(!editMode)}
                    className={`p-2 rounded-lg transition-all ${
                        editMode
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                            : 'text-white/20 hover:text-white/40 hover:bg-white/5'
                    }`}
                    title={editMode ? 'Done editing' : 'Edit widgets'}
                >
                    {editMode ? <Check className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
                </button>

                {/* Divider */}
                <div className="w-px h-5 bg-white/[0.06]" />

                {/* User menu */}
                <UserMenu onOpenSettings={onOpenSettings} />
            </div>
        </header>
    );
}
