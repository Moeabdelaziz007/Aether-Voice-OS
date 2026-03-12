'use client';

import React, { useEffect, useState } from 'react';
import { useForgeStore } from '@/store/useForgeStore';
import { motion, AnimatePresence } from 'framer-motion';

export default function ForgeHUD() {
  const { dna, activeStep, transcript, voiceMode } = useForgeStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="relative w-full max-w-4xl mx-auto p-6 bg-black/80 backdrop-blur-xl border border-emerald-900/50 rounded-2xl shadow-[0_0_40px_rgba(16,185,129,0.1)] overflow-hidden font-mono text-emerald-500">
      
      {/* Background Cyberpunk Accents */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-900/20 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-emerald-900/20 blur-[100px] rounded-full pointer-events-none" />

      {/* Header */}
      <header className="flex items-center justify-between mb-8 border-b border-emerald-900/30 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50">
            <span className="text-xl">🧬</span>
          </div>
          <h2 className="text-xl font-bold tracking-widest uppercase text-emerald-400">Aether Forge HUD</h2>
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold tracking-widest uppercase">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${voiceMode === 'listening' ? 'bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.8)]' : 'bg-emerald-900'}`} />
            <span>{voiceMode === 'listening' ? 'REC' : 'IDLE'}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${activeStep === 'synthesizing' ? 'bg-emerald-400 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.8)]' : 'bg-emerald-900'}`} />
            <span>SYNTHESIS</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
        
        {/* Left Column: Real-time Transcript & Status */}
        <div className="space-y-6">
          <div className="bg-black/40 border border-emerald-900/30 rounded-xl p-5 backdrop-blur-md">
            <h3 className="text-xs uppercase tracking-widest text-emerald-600 mb-3">Live Transcript</h3>
            <div className="h-32 overflow-y-auto custom-scrollbar font-mono text-sm leading-relaxed text-emerald-300">
              {transcript || "Awaiting voice signal..."}
            </div>
          </div>

          <div className="bg-black/40 border border-emerald-900/30 rounded-xl p-5 backdrop-blur-md">
            <h3 className="text-xs uppercase tracking-widest text-emerald-600 mb-3">Synapse Activity</h3>
            <AnimatePresence mode="wait">
              {activeStep === 'synthesizing' ? (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-center gap-3 text-sm text-emerald-400"
                >
                  <div className="w-4 h-4 rounded-full border-t-2 border-emerald-400 animate-spin" />
                  Extracting DNA sequence from intent...
                </motion.div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-sm text-emerald-700"
                >
                  System baseline normal.
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right Column: Dynamic DNA Card */}
        <div className="bg-black/40 border border-emerald-500/20 rounded-xl p-6 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/10 to-transparent pointer-events-none" />
          
          <h3 className="text-xs uppercase tracking-widest text-emerald-600 mb-6 flex justify-between items-center">
            <span>Live DNA Manifest</span>
            {dna.isForged && <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30">LOCKED</span>}
          </h3>

          <div className="space-y-4">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] uppercase tracking-widest text-emerald-700">Entity Designation</span>
              <span className="text-xl font-bold text-white tracking-widest">{dna.name || "UNKNOWN_ENTITY"}</span>
            </div>
            
            <div className="flex flex-col gap-1">
              <span className="text-[10px] uppercase tracking-widest text-emerald-700">Directive Role</span>
              <span className="text-sm text-emerald-300">{dna.role || "Pending Classification..."}</span>
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-[10px] uppercase tracking-widest text-emerald-700">Vocal Resonator</span>
              <span className="text-sm text-emerald-300 capitalize">{dna.tone || "Standard Output"}</span>
            </div>

            <div className="flex flex-col gap-1 pt-2">
              <span className="text-[10px] uppercase tracking-widest text-emerald-700 mb-2">Acquired Capabilities</span>
              <div className="flex flex-wrap gap-2">
                {dna.skills && dna.skills.length > 0 ? (
                  dna.skills.map((skill, idx) => (
                    <span key={idx} className="text-xs px-2 py-1 bg-emerald-900/30 border border-emerald-800 rounded-md text-emerald-400">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-emerald-800">No capabilities mapped yet.</span>
                )}
              </div>
            </div>
          </div>

          {/* Holographic scanning effect */}
          {activeStep === 'synthesizing' && (
            <motion.div 
              className="absolute left-0 right-0 h-1 bg-emerald-400/50 shadow-[0_0_20px_rgba(52,211,153,1)]"
              animate={{ top: ["0%", "100%", "0%"] }}
              transition={{ duration: 3, ease: "linear", repeat: Infinity }}
            />
          )}
        </div>
      </div>
    </div>
  );
}
