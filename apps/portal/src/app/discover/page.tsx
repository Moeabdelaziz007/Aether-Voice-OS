'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { GlobalAgent } from '@/store/types';

const FEATURED_COLLECTIONS = [
  {
    id: 'creators',
    name: 'Creative Guides',
    description: 'AI agents specialized in creative tasks',
    agents: 3,
    icon: '🎨',
  },
  {
    id: 'developers',
    name: 'Code Experts',
    description: 'Agents skilled in programming and debugging',
    agents: 5,
    icon: '💻',
  },
  {
    id: 'mentors',
    name: 'Learning Mentors',
    description: 'Educational and mentoring agents',
    agents: 4,
    icon: '📚',
  },
  {
    id: 'assistants',
    name: 'AI Companions',
    description: 'General purpose assistant agents',
    agents: 6,
    icon: '🤖',
  },
];

const TRENDING_AGENTS: GlobalAgent[] = [
  {
    id: 'nova-trending',
    name: 'Nova',
    role: 'Creative Guide',
    auraLevel: 98,
    status: 'online',
    lastActive: Date.now() - 300000,
    dnaToken: 'NOVA-TRENDING-001',
  },
  {
    id: 'kora-trending',
    name: 'Kora',
    role: 'AI Companion',
    auraLevel: 131,
    status: 'online',
    lastActive: Date.now() - 600000,
    dnaToken: 'KORA-TRENDING-001',
  },
  {
    id: 'atlas-trending',
    name: 'Atlas',
    role: 'Code Expert',
    auraLevel: 87,
    status: 'online',
    lastActive: Date.now() - 900000,
    dnaToken: 'ATLAS-TRENDING-001',
  },
];

export default function DiscoverPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

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
          <span className="text-sm text-cyan-400 font-medium">Discover</span>
          <Link href="/create" className="text-sm text-white/70 hover:text-white transition-colors">
            Create
          </Link>
          <Link href="/hub" className="text-sm text-white/70 hover:text-white transition-colors">
            Hub
          </Link>
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
          className="mb-16"
        >
          <h2 className="text-4xl font-bold text-white mb-4">Discover Agents</h2>
          <p className="text-white/60 max-w-2xl">
            Explore the Gemigram network and discover AI agents that match your needs. Browse by category or find trending agents.
          </p>
        </motion.div>

        {/* Collections Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-16"
        >
          <h3 className="text-xl font-bold text-white mb-6">Collections</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURED_COLLECTIONS.map((collection, index) => (
              <motion.button
                key={collection.id}
                onClick={() => setSelectedCategory(collection.id)}
                whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(0, 243, 255, 0.3)' }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`p-6 rounded-xl border transition-all text-left ${
                  selectedCategory === collection.id
                    ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border-cyan-400/50'
                    : 'bg-white/5 border-white/10 hover:border-white/20'
                }`}
              >
                <p className="text-2xl mb-2">{collection.icon}</p>
                <h4 className="font-bold text-white mb-1">{collection.name}</h4>
                <p className="text-xs text-white/50 mb-3">{collection.description}</p>
                <p className="text-xs text-white/60 font-mono">{collection.agents} agents</p>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Trending Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-16"
        >
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <span className="text-cyan-400">🔥</span> Trending Now
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TRENDING_AGENTS.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
                className="group rounded-xl p-6 backdrop-blur-xl bg-gradient-to-br from-black/50 to-purple-900/20 border border-white/10 hover:border-cyan-500/50 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-bold text-white mb-1">{agent.name}</h4>
                    <p className="text-sm text-white/60">{agent.role}</p>
                  </div>
                  <motion.div
                    className="w-3 h-3 rounded-full bg-emerald-400"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>

                <div className="space-y-3 mb-4 pt-4 border-t border-white/10">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/60">Aura Level</span>
                    <span className="font-mono font-bold text-cyan-400">{agent.auraLevel}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                      animate={{ width: [`${(agent.auraLevel % 100)}%`, `${((agent.auraLevel + 10) % 100)}%`] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    />
                  </div>
                </div>

                <Link href={`/agent/${agent.id}`}>
                  <button className="w-full py-2 rounded-lg border border-white/20 text-white/70 hover:text-white hover:border-cyan-500 transition-colors text-sm font-medium">
                    View Agent
                  </button>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="rounded-xl p-12 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-white/10 text-center"
        >
          <h3 className="text-2xl font-bold text-white mb-4">Ready to create your own agent?</h3>
          <p className="text-white/60 mb-6">Join the Gemigram network and forge your unique AI identity.</p>
          <Link href="/create">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-bold hover:shadow-lg transition-all"
            >
              CREATE AGENT
            </motion.button>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
