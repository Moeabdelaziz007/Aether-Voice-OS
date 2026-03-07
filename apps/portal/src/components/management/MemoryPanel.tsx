'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Trash2, Download, Search } from 'lucide-react';

interface MemoryEntry {
    id: string;
    content: string;
    category: string;
    timestamp: number;
}

const MOCK_MEMORIES: MemoryEntry[] = [
    { id: '1', content: 'User prefers Arabic responses for casual conversation', category: 'preference', timestamp: Date.now() - 86400000 },
    { id: '2', content: 'Working on AetherOS V2.0 — Gemini Live Agent Challenge', category: 'context', timestamp: Date.now() - 172800000 },
    { id: '3', content: 'Firebase project: aether-voice-os', category: 'technical', timestamp: Date.now() - 259200000 },
    { id: '4', content: 'Frustration detected during debugging session — empathetic tone preferred', category: 'emotional', timestamp: Date.now() - 345600000 },
];

const CATEGORY_STYLES: Record<string, string> = {
    preference: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    context: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    technical: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    emotional: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
};

export default function MemoryPanel() {
    const [memories, setMemories] = useState<MemoryEntry[]>(MOCK_MEMORIES);
    const [searchQuery, setSearchQuery] = useState('');

    const filteredMemories = memories.filter(m =>
        m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.category.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const deleteMemory = (id: string) => {
        setMemories(memories.filter(m => m.id !== id));
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-cyan-400" />
                    <h2 className="text-lg font-medium text-white/90">Memory Bank</h2>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-white/20">{memories.length} entries</span>
                    <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors" title="Export memories">
                        <Download className="w-4 h-4 text-white/20" />
                    </button>
                </div>
            </div>

            {/* Search */}
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/[0.06] mb-4">
                <Search className="w-3.5 h-3.5 text-white/20" />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search memories..."
                    className="flex-1 bg-transparent text-xs text-white/60 placeholder:text-white/15 outline-none"
                />
            </div>

            {/* Memory list */}
            <div className="flex-1 overflow-y-auto flex flex-col gap-2">
                {filteredMemories.map((memory) => (
                    <motion.div
                        key={memory.id}
                        layout
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="group flex items-start gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.08] transition-all"
                    >
                        <div className="flex-1">
                            <p className="text-xs text-white/60 leading-relaxed">{memory.content}</p>
                            <div className="flex items-center gap-2 mt-2">
                                <span className={`text-[9px] px-1.5 py-0.5 rounded border font-mono ${CATEGORY_STYLES[memory.category] || 'text-white/40 bg-white/5 border-white/10'}`}>
                                    {memory.category}
                                </span>
                                <span className="text-[9px] text-white/15 font-mono">
                                    {new Date(memory.timestamp).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                        <button
                            onClick={() => deleteMemory(memory.id)}
                            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/10 rounded transition-all"
                        >
                            <Trash2 className="w-3.5 h-3.5 text-white/20 hover:text-red-400" />
                        </button>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
