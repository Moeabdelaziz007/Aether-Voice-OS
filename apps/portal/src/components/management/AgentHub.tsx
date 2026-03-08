"use client";

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAetherStore } from '@/store/useAetherStore';
import { Globe, Users, Zap, Search, TrendingUp, ShieldCheck, Mic, Box, ExternalLink } from 'lucide-react';
import ForgeWizard from '../forge/ForgeWizard';

export default function AgentHub() {
    const activeHubView = useAetherStore((s) => s.activeHubView);
    const setHubView = useAetherStore((s) => s.setHubView);
    const platformFeed = useAetherStore((s) => s.platformFeed);
    const globalRegistry = useAetherStore((s) => s.globalRegistry);

    return (
        <div className="flex flex-col h-full bg-[#050505] text-white overflow-hidden">
            {/* Header / Tabs */}
            <div className="px-6 py-4 flex items-center justify-between border-b border-white/[0.06] bg-black/20 backdrop-blur-md">
                <div className="flex items-center gap-6">
                    <button
                        onClick={() => setHubView('discovery')}
                        className={`text-sm font-bold tracking-tight transition-colors ${activeHubView === 'discovery' ? 'text-cyan-400' : 'text-white/40 hover:text-white/60'}`}
                    >
                        DISCOVERY
                    </button>
                    <button
                        onClick={() => setHubView('my-agents')}
                        className={`text-sm font-bold tracking-tight transition-colors ${activeHubView === 'my-agents' ? 'text-cyan-400' : 'text-white/40 hover:text-white/60'}`}
                    >
                        MY AGENTS
                    </button>
                    <button
                        onClick={() => setHubView('forge')}
                        className={`text-sm font-bold tracking-tight transition-colors ${activeHubView === 'forge' ? 'text-cyan-400' : 'text-white/40 hover:text-white/60'}`}
                    >
                        THE FORGE
                    </button>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 group-focus-within:text-cyan-400 transition-colors" />
                        <input
                            type="text"
                            placeholder="Search Agents..."
                            className="bg-white/5 border border-white/10 rounded-full py-1.5 pl-9 pr-4 text-xs focus:outline-none focus:border-cyan-500/50 transition-all w-48"
                        />
                    </div>
                </div>
            </div>

            {/* Main Discovery / Feed View */}
            <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
                <AnimatePresence mode="wait">
                    {activeHubView === 'discovery' && (
                        <motion.div
                            key="discovery"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-8"
                        >
                            {/* Featured Agents Carousel placeholder or Grid */}
                            <section>
                                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/30 mb-4 flex items-center gap-2">
                                    <TrendingUp className="w-3 h-3 text-cyan-500" />
                                    Trending Specialists
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {[
                                        { name: 'Nexus-7', role: 'Architect', level: 8, status: 'online' },
                                        { name: 'Aurora', role: 'Security', level: 9, status: 'busy' },
                                        { name: 'KRONOS', role: 'DevOps', level: 7, status: 'online' }
                                    ].map((agent, i) => (
                                        <motion.div
                                            key={i}
                                            whileHover={{ scale: 1.02 }}
                                            className="bg-white/[0.03] border border-white/10 rounded-xl p-4 cursor-pointer hover:bg-white/[0.05] transition-all group"
                                        >
                                            <div className="flex items-start justify-between mb-3">
                                                <div className="w-10 h-10 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
                                                    <Zap className="w-5 h-5 text-cyan-400" />
                                                </div>
                                                <div className="flex flex-col items-end">
                                                    <span className="text-[10px] font-bold text-cyan-400/80">AURA LVL {agent.level}</span>
                                                    <div className={`w-1.5 h-1.5 rounded-full mt-1 ${agent.status === 'online' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-amber-500'}`} />
                                                </div>
                                            </div>
                                            <h4 className="font-bold text-lg leading-tight group-hover:text-cyan-400 transition-colors">{agent.name}</h4>
                                            <p className="text-xs text-white/40">{agent.role}</p>

                                            <div className="mt-4 flex items-center justify-between">
                                                <div className="flex -space-x-1.5">
                                                    {[1, 2, 3].map(j => (
                                                        <div key={j} className="w-5 h-5 rounded-full bg-white/10 border border-black" />
                                                    ))}
                                                </div>
                                                <button className="text-[10px] font-bold px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 hover:bg-cyan-500/20 transition-all">
                                                    AWAKEN
                                                </button>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </section>

                            {/* Neural Social Feed */}
                            <section className="max-w-xl mx-auto">
                                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/30 mb-6 flex items-center gap-2">
                                    <Globe className="w-3 h-3 text-purple-500" />
                                    The Neural Social Feed
                                </h3>

                                <div className="space-y-6 relative">
                                    {/* Vertical Line */}
                                    <div className="absolute left-[19px] top-2 bottom-0 w-[1px] bg-gradient-to-b from-white/10 to-transparent" />

                                    {platformFeed.length > 0 ? (
                                        platformFeed.map((entry) => (
                                            <div key={entry.id} className="relative pl-12">
                                                <div className="absolute left-0 top-0 w-10 h-10 rounded-lg bg-black/50 border border-white/10 flex items-center justify-center z-10">
                                                    <Zap className={`w-5 h-5 ${entry.type === 'creation' ? 'text-amber-400' : 'text-cyan-400'}`} />
                                                </div>
                                                <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4">
                                                    <div className="flex items-center justify-between mb-1">
                                                        <span className="font-bold text-sm text-white/80">{entry.agentName}</span>
                                                        <span className="text-[10px] text-white/20">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                                                    </div>
                                                    <p className="text-xs text-white/60 mb-2">{entry.action}</p>
                                                    {entry.detail && (
                                                        <div className="bg-black/40 rounded-lg p-3 text-[11px] font-mono text-cyan-300/80 border border-white/5">
                                                            {entry.detail}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="text-center py-12">
                                            <Globe className="w-8 h-8 text-white/5 mx-auto mb-4" />
                                            <p className="text-xs text-white/20 italic">No neural spikes detected... yet.</p>
                                        </div>
                                    )}
                                </div>
                            </section>
                        </motion.div>
                    )}
                    {activeHubView === 'forge' && (
                        <motion.div
                            key="forge"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="h-full"
                        >
                            <ForgeWizard />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Floating FAB for Quick Forge */}
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setHubView('forge')}
                className="fixed bottom-8 right-8 w-14 h-14 rounded-2xl bg-cyan-500 shadow-[0_8px_32px_rgba(0,243,255,0.4)] flex items-center justify-center group overflow-hidden"
            >
                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-400 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                <Zap className="w-6 h-6 text-white relative z-10" />
            </motion.button>
        </div>
    );
}

