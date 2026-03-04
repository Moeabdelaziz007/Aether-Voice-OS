"use client";

/**
 * MemoryRealm — Conversation timeline with search.
 * Orb is at 100px left-center. Timeline flows on the right side.
 * Wired to live transcript from Zustand store + mock fallback.
 */

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Search } from "lucide-react";
import GlassPanel from "@/components/shared/GlassPanel";
import { useAetherStore } from "@/store/useAetherStore";
import { MOCK_MEMORIES, type MemoryEntry } from "@/lib/mockData";

// Color map for transcript roles
const ROLE_COLORS = {
    user: "#00F3FF",
    agent: "#A855F7",
    system: "#F59E0B",
};

// Convert transcript messages to MemoryEntry format
function transcriptToMemory(msg: { id: string; role: string; content: string; timestamp: number }, index: number): MemoryEntry {
    const roleColor = ROLE_COLORS[msg.role as keyof typeof ROLE_COLORS] || ROLE_COLORS.system;
    const time = new Date(msg.timestamp);
    const timeStr = time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

    return {
        id: msg.id,
        title: msg.role === "user" ? "You said" : "Aether responded",
        summary: msg.content,
        timestamp: timeStr,
        category: msg.role === "user" ? "code" : "design",
        dotColor: roleColor,
    };
}

function MemoryNode({ entry, index }: { entry: MemoryEntry; index: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex gap-4 relative"
        >
            {/* Timeline connector + dot */}
            <div className="flex flex-col items-center shrink-0">
                <div
                    className="w-2.5 h-2.5 rounded-full shrink-0 mt-1.5 shadow-[0_0_8px_currentColor]"
                    style={{ backgroundColor: entry.dotColor, color: entry.dotColor }}
                />
                {/* Connector line */}
                <div className="w-px flex-1 bg-white/10 mt-1" />
            </div>

            {/* Card Content */}
            <GlassPanel
                className="flex-1 mb-3 !p-4"
                hover
            >
                <div className="flex items-start justify-between gap-3 mb-1">
                    <h3 className="text-white/90 text-sm font-medium">{entry.title}</h3>
                    <span className="text-white/30 text-xs font-mono shrink-0">{entry.timestamp}</span>
                </div>
                <p className="text-white/50 text-xs leading-relaxed">{entry.summary}</p>
            </GlassPanel>
        </motion.div>
    );
}

export default function MemoryRealm() {
    const [searchQuery, setSearchQuery] = useState("");
    const transcript = useAetherStore((s) => s.transcript);

    // Use live transcript if available, else mock data
    const memories: MemoryEntry[] = useMemo(() => {
        if (transcript.length > 0) {
            return transcript.map((msg, i) => transcriptToMemory(msg, i)).reverse();
        }
        return MOCK_MEMORIES;
    }, [transcript]);

    const filteredMemories = useMemo(() => {
        if (!searchQuery.trim()) return memories;
        const q = searchQuery.toLowerCase();
        return memories.filter(
            (m) =>
                m.title.toLowerCase().includes(q) ||
                m.summary.toLowerCase().includes(q)
        );
    }, [searchQuery, memories]);

    const isLive = transcript.length > 0;

    return (
        <div className="w-full h-full flex">
            {/* Left spacer for orb area */}
            <div className="w-[25%] shrink-0 hidden md:block" />

            {/* Timeline area */}
            <div className="flex-1 flex flex-col h-full pt-12 pr-6 pl-6 md:pl-0 overflow-hidden">
                {/* Search Bar */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="relative mb-6 max-w-2xl"
                >
                    <Search
                        size={14}
                        className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30"
                    />
                    <input
                        type="text"
                        placeholder="Search neural memory..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-full py-2.5 pl-10 pr-4 text-sm text-white/80 placeholder-white/30 outline-none focus:border-cyan-400/30 focus:shadow-[0_0_20px_rgba(0,243,255,0.05)] transition-all duration-300 font-sans"
                    />
                </motion.div>

                {/* Section Title */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.15 }}
                    className="flex items-center gap-3 mb-4"
                >
                    <h2 className="text-white/30 text-xs uppercase tracking-[0.2em] font-mono">
                        Neural Memory — {filteredMemories.length} entries
                    </h2>
                    {isLive && (
                        <span className="font-mono text-[9px] tracking-widest text-emerald-400/60 bg-emerald-400/[0.06] px-2 py-0.5 rounded-full border border-emerald-400/10 animate-pulse">
                            LIVE
                        </span>
                    )}
                </motion.div>

                {/* Timeline */}
                <div className="flex-1 overflow-y-auto no-scrollbar pb-24 max-w-2xl">
                    {filteredMemories.map((entry, i) => (
                        <MemoryNode key={entry.id} entry={entry} index={i} />
                    ))}

                    {filteredMemories.length === 0 && (
                        <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-white/20 text-sm font-mono mt-8 text-center"
                        >
                            No memories match &ldquo;{searchQuery}&rdquo;
                        </motion.p>
                    )}
                </div>
            </div>
        </div>
    );
}
