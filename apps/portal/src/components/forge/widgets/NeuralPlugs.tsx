"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plug, CheckCircle2, Loader2, Unplug } from 'lucide-react';
import { useForgeStore, AVAILABLE_PLUGS } from '@/store/useForgeStore';

export default function NeuralPlugs() {
    const { dna, connectPlug, disconnectPlug } = useForgeStore();
    const [connecting, setConnecting] = useState<string | null>(null);

    const handleTogglePlug = (plugId: string) => {
        const isConnected = dna.neuralPlugs.includes(plugId);
        if (isConnected) {
            disconnectPlug(plugId);
        } else {
            setConnecting(plugId);
            // Simulate connection delay
            setTimeout(() => {
                connectPlug(plugId);
                setConnecting(null);
            }, 1200);
        }
    };

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 bg-green-500/10 border border-green-500/20 rounded-xl">
                    <Plug className="w-5 h-5 text-green-400" />
                </div>
                <div>
                    <h3 className="text-sm font-black text-white/80 uppercase tracking-wider">Neural Plugs</h3>
                    <p className="text-[9px] text-white/30 uppercase tracking-widest">MCP Connection Store</p>
                </div>
                {dna.neuralPlugs.length > 0 && (
                    <div className="ml-auto px-2.5 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
                        <span className="text-[9px] font-black text-green-400">{dna.neuralPlugs.length} Connected</span>
                    </div>
                )}
            </div>

            <p className="text-[10px] text-white/30 leading-relaxed">
                Connect real-world accounts to give your agent superpowers. Say &quot;Connect my Spotify&quot; and watch the Neural Plug snap into the core.
            </p>

            {/* Plug Grid */}
            <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_PLUGS.map((plug) => {
                    const isConnected = dna.neuralPlugs.includes(plug.id);
                    const isConnecting = connecting === plug.id;

                    return (
                        <motion.button
                            key={plug.id}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleTogglePlug(plug.id)}
                            className={`relative p-4 rounded-2xl border text-left transition-all overflow-hidden ${
                                isConnected
                                    ? 'bg-green-500/[0.08] border-green-500/30'
                                    : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                            }`}
                        >
                            {/* Connection Pulse */}
                            <AnimatePresence>
                                {isConnecting && (
                                    <motion.div
                                        initial={{ scale: 0, opacity: 0.5 }}
                                        animate={{ scale: 3, opacity: 0 }}
                                        exit={{ opacity: 0 }}
                                        transition={{ duration: 1 }}
                                        className="absolute inset-0 bg-green-400 rounded-2xl pointer-events-none"
                                    />
                                )}
                            </AnimatePresence>

                            <div className="relative z-10">
                                <div className="flex items-start justify-between mb-3">
                                    <span className="text-2xl">{plug.icon}</span>
                                    {isConnecting ? (
                                        <Loader2 className="w-4 h-4 text-green-400 animate-spin" />
                                    ) : isConnected ? (
                                        <CheckCircle2 className="w-4 h-4 text-green-400" />
                                    ) : (
                                        <Plug className="w-3.5 h-3.5 text-white/15" />
                                    )}
                                </div>
                                <div className={`text-xs font-bold mb-1 ${isConnected ? 'text-green-300' : 'text-white/60'}`}>
                                    {plug.name}
                                </div>
                                <p className="text-[9px] text-white/25 leading-tight">{plug.description}</p>

                                {/* Connection Status Indicator */}
                                <div className="mt-3 flex items-center gap-1.5">
                                    <div className={`w-1.5 h-1.5 rounded-full ${
                                        isConnected ? 'bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.6)]' :
                                        isConnecting ? 'bg-amber-400 animate-pulse' : 'bg-white/10'
                                    }`} />
                                    <span className={`text-[8px] font-mono uppercase tracking-widest ${
                                        isConnected ? 'text-green-400/60' :
                                        isConnecting ? 'text-amber-400/60' : 'text-white/15'
                                    }`}>
                                        {isConnecting ? 'Syncing...' : isConnected ? 'Online' : 'Offline'}
                                    </span>
                                </div>
                            </div>
                        </motion.button>
                    );
                })}
            </div>

            {/* Connected Summary */}
            {dna.neuralPlugs.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-3 bg-green-500/[0.04] border border-green-500/15 rounded-xl"
                >
                    <div className="text-[9px] font-mono text-green-400/50 uppercase tracking-widest mb-2">
                        Active Neural Connections
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                        {dna.neuralPlugs.map((id) => {
                            const plug = AVAILABLE_PLUGS.find((p) => p.id === id);
                            return (
                                <span key={id} className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-500/10 border border-green-500/20 rounded-md text-[8px] text-green-300">
                                    {plug?.icon} {plug?.name}
                                </span>
                            );
                        })}
                    </div>
                </motion.div>
            )}
        </div>
    );
}
