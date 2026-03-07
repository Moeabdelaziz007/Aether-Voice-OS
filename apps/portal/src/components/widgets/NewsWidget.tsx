'use client';

import React, { useState } from 'react';
import { ExternalLink, Clock } from 'lucide-react';

interface NewsItem {
    title: string;
    source: string;
    publishedAt: string;
    category: string;
}

const MOCK_NEWS: NewsItem[] = [
    { title: 'OpenAI Unveils GPT-5 with Real-Time Reasoning', source: 'TechCrunch', publishedAt: '2h ago', category: 'AI' },
    { title: 'Bitcoin Crosses $100K for First Time in 2026', source: 'Bloomberg', publishedAt: '4h ago', category: 'Crypto' },
    { title: 'Google DeepMind Releases Gemini 3.0 Preview', source: 'The Verge', publishedAt: '6h ago', category: 'AI' },
    { title: 'SpaceX Starship Successfully Lands on Mars', source: 'Reuters', publishedAt: '8h ago', category: 'Space' },
];

const CATEGORY_COLORS: Record<string, string> = {
    'AI': 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    'Crypto': 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    'Space': 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    'Tech': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};

export default function NewsWidget() {
    const [news] = useState<NewsItem[]>(MOCK_NEWS);

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">Headlines</span>
                <span className="text-[10px] font-mono text-white/20">{news.length} articles</span>
            </div>

            {/* News list */}
            <div className="flex flex-col gap-3">
                {news.map((item, i) => (
                    <div key={i} className="group flex flex-col gap-1.5 pb-3 border-b border-white/5 last:border-0 last:pb-0">
                        <div className="flex items-start gap-2">
                            <div className="flex-1">
                                <p className="text-sm text-white/70 leading-snug group-hover:text-white/90 transition-colors cursor-pointer">
                                    {item.title}
                                </p>
                            </div>
                            <ExternalLink className="w-3 h-3 text-white/10 group-hover:text-white/30 mt-1 shrink-0 transition-colors" />
                        </div>
                        <div className="flex items-center gap-2">
                            <span className={`text-[9px] px-1.5 py-0.5 rounded border font-mono ${CATEGORY_COLORS[item.category] || 'text-white/40 bg-white/5 border-white/10'}`}>
                                {item.category}
                            </span>
                            <span className="text-[10px] text-white/20 font-mono">{item.source}</span>
                            <span className="flex items-center gap-1 text-[10px] text-white/15 font-mono ml-auto">
                                <Clock className="w-2.5 h-2.5" />
                                {item.publishedAt}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
