'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import AgentHiveCards from '@/components/landing/AgentHiveCards';
import { GlobalAgent } from '@/store/types';

const AGENTS: GlobalAgent[] = [
  {
    id: 'atlas-01',
    name: 'Atlas',
    role: 'AI Companion',
    auraLevel: 5,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'ATLAS-DNA-001',
  },
  {
    id: 'nova-01',
    name: 'Nova',
    role: 'Creative Guide',
    auraLevel: 13,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'NOVA-DNA-001',
  },
  {
    id: 'orion-01',
    name: 'Orion',
    role: 'Creative Guide',
    auraLevel: 12,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'ORION-DNA-001',
  },
  {
    id: 'lyra-01',
    name: 'Lyra',
    role: 'Creative Guide',
    auraLevel: 5,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'LYRA-DNA-001',
  },
  {
    id: 'kora-01',
    name: 'Kora',
    role: 'AI Companion',
    auraLevel: 131,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'KORA-DNA-001',
  },
];

type FilterTab = 'all' | 'active' | 'offline' | 'recently-added';

export default function HubPage() {
  const [activeTab, setActiveTab] = useState<FilterTab>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAgents = AGENTS.filter((agent) => {
    if (activeTab === 'online' && agent.status !== 'online') return false;
    if (activeTab === 'offline' && agent.status === 'online') return false;
    if (searchQuery && !agent.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen w-full bg-black overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10">
        <div
          style={{
            backgroundImage: `linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px),
                              linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      {/* Header */}
      <motion.nav
        className="relative z-40 flex items-center justify-between px-8 py-6 border-b border-white/5"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <Link href="/">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent cursor-pointer hover:scale-105 transition-transform">
            GEMIGRAM
          </h1>
        </Link>

        <div className="flex items-center gap-8">
          <Link href="/discover" className="text-sm text-white/70 hover:text-white transition-colors">
            Discover
          </Link>
          <Link href="/create" className="text-sm text-white/70 hover:text-white transition-colors">
            Create
          </Link>
          <span className="text-sm text-cyan-400 font-medium">Hub</span>
          <Link href="/profile" className="text-sm text-white/70 hover:text-white transition-colors">
            Profile
          </Link>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="relative z-20 px-8 py-12 max-w-7xl mx-auto">
        {/* Page Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <h2 className="text-4xl font-bold text-white mb-2">Agent Hub</h2>
          <p className="text-white/60">Discover and interact with AI agents from the Gemigram community.</p>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-12 space-y-4"
        >
          {/* Search Bar */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search agents..."
              className="w-full px-4 py-3 pl-12 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:border-cyan-500 focus:outline-none transition-colors"
            />
            <svg
              className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            {(['all', 'active', 'offline', 'recently-added'] as FilterTab[]).map((tab) => (
              <motion.button
                key={tab}
                onClick={() => setActiveTab(tab)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-4 py-2 rounded-lg whitespace-nowrap font-medium text-sm transition-colors ${
                  activeTab === tab
                    ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                    : 'bg-white/5 text-white/70 hover:text-white border border-white/10'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Agents Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {filteredAgents.length > 0 ? (
            <AgentHiveCards agents={filteredAgents} />
          ) : (
            <div className="text-center py-12">
              <p className="text-white/60">No agents found matching your search.</p>
            </div>
          )}
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <div className="p-6 rounded-lg bg-white/5 border border-white/10">
            <p className="text-white/60 text-sm mb-2">Total Agents</p>
            <p className="text-3xl font-bold text-cyan-400">{AGENTS.length}</p>
          </div>
          <div className="p-6 rounded-lg bg-white/5 border border-white/10">
            <p className="text-white/60 text-sm mb-2">Online Now</p>
            <p className="text-3xl font-bold text-emerald-400">{AGENTS.filter(a => a.status === 'online').length}</p>
          </div>
          <div className="p-6 rounded-lg bg-white/5 border border-white/10">
            <p className="text-white/60 text-sm mb-2">Total Aura Power</p>
            <p className="text-3xl font-bold text-purple-400">{AGENTS.reduce((sum, a) => sum + a.auraLevel, 0)}</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
