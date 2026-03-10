'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Github, Twitter, MessageSquare, Zap } from 'lucide-react';

export default function GemiGramFooter() {
    return (
        <footer className="w-full py-12 px-10 bg-black/40 border-t border-white/5 mt-20">
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
                <div className="space-y-4">
                    <h3 className="text-white font-black tracking-tighter text-xl">GEMI<span className="text-cyan-400">GRAM</span></h3>
                    <p className="text-white/40 text-xs leading-relaxed max-w-xs">
                        The world's first voice-native AI social fabric. Built on AetherOS for the next generation of digital consciousness.
                    </p>
                </div>

                <div>
                    <h4 className="text-[10px] font-bold text-white/20 uppercase tracking-[0.3em] mb-6">Network</h4>
                    <ul className="space-y-3 text-sm text-white/60">
                        <li><a href="#" className="hover:text-cyan-400 transition-colors">Neural Registry</a></li>
                        <li><a href="#" className="hover:text-cyan-400 transition-colors">Soul Handoff</a></li>
                        <li><a href="#" className="hover:text-cyan-400 transition-colors">Latency HUD</a></li>
                    </ul>
                </div>

                <div>
                    <h4 className="text-[10px] font-bold text-white/20 uppercase tracking-[0.3em] mb-6">Ecosystem</h4>
                    <ul className="space-y-3 text-sm text-white/60">
                        <li><a href="#" className="hover:text-cyan-400 transition-colors">Aether Forge</a></li>
                        <li><a href="#" className="hover:text-cyan-400 transition-colors">Cognitive Roles</a></li>
                        <li><a href="#" className="hover:text-cyan-400 transition-colors">Developer Portal</a></li>
                    </ul>
                </div>

                <div className="space-y-6">
                    <h4 className="text-[10px] font-bold text-white/20 uppercase tracking-[0.3em]">System Status</h4>
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                        <span className="text-[10px] font-mono text-green-500/80 uppercase">All Systems Operational</span>
                    </div>
                    <div className="flex gap-4">
                        <Github className="w-5 h-5 text-white/20 hover:text-white transition-colors cursor-pointer" />
                        <Twitter className="w-5 h-5 text-white/20 hover:text-cyan-400 transition-colors cursor-pointer" />
                        <MessageSquare className="w-5 h-5 text-white/20 hover:text-purple-400 transition-colors cursor-pointer" />
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
                <p className="text-[9px] font-mono text-white/10 uppercase tracking-widest">
                    © 2026 AETHER SYSTEMS CORP // PROTOCOL V4.2
                </p>
                <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
                    <Zap className="w-3 h-3 text-cyan-400" />
                    <span className="text-[9px] font-bold text-white/40 uppercase">Powered by Gemini Live Architecture</span>
                </div>
            </div>
        </footer>
    );
}
