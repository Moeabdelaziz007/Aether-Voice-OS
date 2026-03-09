'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    LayoutDashboard,
    Brain,
    Sparkles,
    UserCircle,
    Settings,
    Mic,
    ChevronLeft,
    ChevronRight,
    Layers,
    Terminal,
    Globe,
    Zap,
} from 'lucide-react';
import { useAetherStore, type RealmType } from '@/store/useAetherStore';

export type SidebarPanel = 'dashboard' | 'hub' | 'memory' | 'skills' | 'persona' | 'voice' | 'terminal' | null;

interface SidebarProps {
    activePanel: SidebarPanel;
    onPanelChange: (panel: SidebarPanel) => void;
    onOpenSettings: () => void;
}

const NAV_ITEMS: { id: SidebarPanel; icon: React.ReactNode; label: string; realm?: RealmType }[] = [
    { id: 'dashboard', icon: <LayoutDashboard className="w-5 h-5" />, label: 'Dashboard' },
    { id: 'hub', icon: <Globe className="w-5 h-5" />, label: 'Agent Hub' },
    { id: 'voice', icon: <Mic className="w-5 h-5" />, label: 'Voice Agent', realm: 'void' },
    { id: 'memory', icon: <Brain className="w-5 h-5" />, label: 'Memory', realm: 'memory' },
    { id: 'skills', icon: <Sparkles className="w-5 h-5" />, label: 'Skills', realm: 'skills' },
    { id: 'persona', icon: <UserCircle className="w-5 h-5" />, label: 'Persona', realm: 'identity' },
    { id: 'terminal', icon: <Terminal className="w-5 h-5" />, label: 'Terminal' },
];

export default function Sidebar({ activePanel, onPanelChange, onOpenSettings }: SidebarProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const setRealm = useAetherStore((s) => s.setRealm);

    const handleNavClick = (item: typeof NAV_ITEMS[0]) => {
        onPanelChange(item.id);
        if (item.realm) {
            setRealm(item.realm);
        }
    };

    return (
        <motion.aside
            animate={{ width: isExpanded ? 200 : 56 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed left-0 top-0 h-full z-50 flex flex-col
                       bg-black/40 backdrop-blur-xl border-r border-white/[0.06]"
        >
            {/* Logo */}
            <div className="flex items-center justify-center h-14 border-b border-white/[0.06]">
                <motion.div
                    className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500/30 to-purple-500/30
                                flex items-center justify-center border border-white/10"
                    whileHover={{ scale: 1.1 }}
                >
                    <Zap className="w-4 h-4 text-cyan-400" />
                </motion.div>
                <AnimatePresence>
                    {isExpanded && (
                        <motion.span
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -10 }}
                            className="ml-2.5 text-sm font-bold tracking-tight text-white/90 whitespace-nowrap"
                        >
                            GEMIGRAM
                        </motion.span>
                    )}
                </AnimatePresence>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-3 flex flex-col gap-1 px-2">
                {NAV_ITEMS.map((item) => {
                    const isActive = activePanel === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => handleNavClick(item)}
                            title={item.label}
                            className={`
                                relative flex items-center gap-3 px-2.5 py-2.5 rounded-lg transition-all duration-200
                                ${isActive
                                    ? 'bg-white/[0.08] text-white'
                                    : 'text-white/30 hover:text-white/60 hover:bg-white/[0.04]'
                                }
                            `}
                        >
                            {/* Active indicator */}
                            {isActive && (
                                <motion.div
                                    layoutId="sidebar-active"
                                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-cyan-400"
                                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                />
                            )}
                            {item.icon}
                            <AnimatePresence>
                                {isExpanded && (
                                    <motion.span
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -10 }}
                                        className="text-xs font-medium whitespace-nowrap"
                                    >
                                        {item.label}
                                    </motion.span>
                                )}
                            </AnimatePresence>
                        </button>
                    );
                })}
            </nav>

            {/* Bottom controls */}
            <div className="py-3 px-2 border-t border-white/[0.06] flex flex-col gap-1">
                <button
                    onClick={onOpenSettings}
                    title="Settings"
                    className="flex items-center gap-3 px-2.5 py-2.5 rounded-lg text-white/30 hover:text-white/60 hover:bg-white/[0.04] transition-all"
                >
                    <Settings className="w-5 h-5" />
                    <AnimatePresence>
                        {isExpanded && (
                            <motion.span
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="text-xs font-medium whitespace-nowrap"
                            >
                                Settings
                            </motion.span>
                        )}
                    </AnimatePresence>
                </button>

                {/* Collapse toggle */}
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="flex items-center justify-center px-2.5 py-2 rounded-lg text-white/20 hover:text-white/40 hover:bg-white/[0.04] transition-all"
                >
                    {isExpanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </button>
            </div>
        </motion.aside>
    );
}
