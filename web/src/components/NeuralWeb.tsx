'use client';

import React from 'react';
import { motion } from 'framer-motion';

export interface HandoverEvent {
    id: string;
    fromAgent: string;
    toAgent: string;
    task: string;
    status: 'pending' | 'active' | 'completed';
}

export const NeuralWeb: React.FC<{ events: HandoverEvent[] }> = ({ events }) => {
    return (
        <div className="w-full carbon-panel rounded-xl border border-white/[0.06] p-4 mt-4">
            <div className="flex justify-between items-center mb-4 border-b border-white/[0.06] pb-2">
                <span className="text-xs text-cyan-400 uppercase tracking-widest font-semibold">
                    Neural Handovers (ADK)
                </span>
                <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 rounded-full">
                    {events.length} Active Handovers
                </span>
            </div>

            <div className="space-y-3 max-h-40 overflow-y-auto scrollbar-thin">
                {events.map((event, i) => (
                    <motion.div
                        key={event.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-center gap-3 text-xs font-mono"
                    >
                        <div className="px-2 py-1 bg-white/5 rounded border border-white/10 text-gray-300">
                            {event.fromAgent}
                        </div>
                        <div className="flex-1 flex items-center">
                            <div className="h-px bg-cyan-500/30 flex-1 relative">
                                <motion.div
                                    className="absolute inset-0 bg-cyan-400 shadow-[0_0_10px_#00f3ff]"
                                    initial={{ scaleX: 0, originX: 0 }}
                                    animate={{ scaleX: 1 }}
                                    transition={{ duration: 1, repeat: Infinity }}
                                />
                            </div>
                        </div>
                        <div className="px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded border border-cyan-500/30">
                            {event.toAgent}
                        </div>
                        <p className="text-[10px] text-gray-500 truncate w-32 ml-2">
                            {event.task}
                        </p>
                    </motion.div>
                ))}

                {events.length === 0 && (
                    <div className="text-center text-gray-600 text-xs py-4 italic font-mono">
                        Awaiting orchestration...
                    </div>
                )}
            </div>
        </div>
    );
};
