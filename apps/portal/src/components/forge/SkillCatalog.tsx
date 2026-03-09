"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "../../store/useAetherStore";

// Mock data based on 18-March goals
const MOCK_SKILLS = [
    { id: "gmail-send", name: "Send Email", category: "Gmail", description: "Send an email via GWS Gmail API." },
    { id: "gmail-read", name: "Read Emails", category: "Gmail", description: "Read recent emails from Inbox." },
    { id: "sheets-append", name: "Append Row", category: "Sheets", description: "Append a row to a Google Sheet." },
    { id: "docs-create", name: "Create Doc", category: "Docs", description: "Create a new Google Document." },
    { id: "calendar-event", name: "Create Event", category: "Calendar", description: "Schedule a Google Calendar event." },
    { id: "drive-search", name: "Search Drive", category: "Drive", description: "Search for files in Google Drive." },
    { id: "automation-workflow", name: "Trigger Workflow", category: "Automation", description: "Trigger a custom automation workflow." }
];

export function SkillCatalog() {
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const toolCalls = useAetherStore((state) => state.toolCallHistory);

    // Identify active skills that are currently running (status: pending or running, etc.)
    // For this demonstration, we pulse skills that are in the toolCalls array.
    const activeSkillIds = useMemo(() => {
        return new Set(toolCalls.map(tc => tc.toolName));
    }, [toolCalls]);

    const categories = useMemo(() => {
        const cats = new Set(MOCK_SKILLS.map(s => s.category));
        return Array.from(cats);
    }, []);

    const filteredSkills = useMemo(() => {
        return MOCK_SKILLS.filter(skill => {
            const matchesSearch = skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                skill.description.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesCategory = selectedCategory ? skill.category === selectedCategory : true;
            return matchesSearch && matchesCategory;
        });
    }, [searchQuery, selectedCategory]);

    return (
        <div className="flex flex-col h-full bg-black/80 text-cyan-500 font-mono p-6 border border-cyan-800 rounded-xl backdrop-blur-md">
            <h2 className="text-2xl font-bold mb-4 tracking-widest text-cyan-300 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]">
                [ 18-MARCH SKILL CATALOG ]
            </h2>

            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <input
                    type="text"
                    placeholder="Search Skills..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="flex-1 bg-cyan-950/30 border border-cyan-800 rounded px-4 py-2 text-cyan-100 placeholder-cyan-700 focus:outline-none focus:border-cyan-400 transition-colors"
                />
                <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2 sm:pb-0">
                    <button
                        onClick={() => setSelectedCategory(null)}
                        className={`px-3 py-1 text-sm rounded border transition-colors whitespace-nowrap ${selectedCategory === null ? 'bg-cyan-800 text-white border-cyan-400' : 'bg-transparent text-cyan-600 border-cyan-800 hover:border-cyan-600'}`}
                    >
                        ALL
                    </button>
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setSelectedCategory(cat)}
                            className={`px-3 py-1 text-sm rounded border transition-colors whitespace-nowrap ${selectedCategory === cat ? 'bg-cyan-800 text-white border-cyan-400' : 'bg-transparent text-cyan-600 border-cyan-800 hover:border-cyan-600'}`}
                        >
                            {cat.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <AnimatePresence>
                        {filteredSkills.map(skill => {
                            const isActive = activeSkillIds.has(skill.id) || activeSkillIds.has(skill.name);
                            return (
                                <motion.div
                                    key={skill.id}
                                    layout
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    transition={{ duration: 0.2 }}
                                    className={`relative p-4 rounded-lg border bg-gradient-to-br from-cyan-950/40 to-black/60 overflow-hidden ${isActive ? 'border-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.5)]' : 'border-cyan-900/50'}`}
                                >
                                    {isActive && (
                                        <motion.div
                                            className="absolute inset-0 bg-cyan-400/20"
                                            animate={{ opacity: [0.1, 0.4, 0.1] }}
                                            transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
                                        />
                                    )}
                                    <div className="relative z-10">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className={`font-bold ${isActive ? 'text-cyan-100' : 'text-cyan-400'}`}>{skill.name}</h3>
                                            <span className="text-[10px] px-2 py-0.5 rounded-full border border-cyan-800/50 text-cyan-600 bg-cyan-950/30">
                                                {skill.category}
                                            </span>
                                        </div>
                                        <p className="text-sm text-cyan-700 mt-2">{skill.description}</p>
                                    </div>
                                </motion.div>
                            );
                        })}
                    </AnimatePresence>
                </motion.div>
                {filteredSkills.length === 0 && (
                    <div className="text-center text-cyan-800 mt-10">
                        NO SKILLS FOUND MATCHING QUERY.
                    </div>
                )}
            </div>
        </div>
    );
}
