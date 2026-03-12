'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function AgentDetailPage() {
  const params = useParams();
  const agentId = params.id as string;

  // Sample agent data
  const agent = {
    id: agentId,
    name: agentId.includes('nova') ? 'Nova' : agentId.includes('kora') ? 'Kora' : 'Atlas',
    role: 'Creative Guide',
    auraLevel: 98,
    status: 'online',
    createdAt: new Date(Date.now() - 86400000 * 30),
    totalInteractions: 245,
    description:
      'A specialized AI agent focused on creative guidance and innovative problem-solving.',
    skills: ['Creative Writing', 'Brainstorming', 'Design Thinking', 'Storytelling'],
    expertise:
      'Specializes in helping users develop creative content, brainstorm ideas, and approach problems from unconventional angles.',
  };

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
          <Link href="/hub" className="text-sm text-white/70 hover:text-white transition-colors">
            Hub
          </Link>
          <Link href="/chat" className="text-sm text-white/70 hover:text-white transition-colors">
            Chat
          </Link>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="relative z-20 max-w-5xl mx-auto px-8 py-12">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="rounded-2xl p-12 backdrop-blur-xl bg-gradient-to-br from-cyan-500/10 to-purple-500/10 border border-white/10 mb-8"
        >
          <div className="flex items-start justify-between gap-8">
            {/* Avatar and Info */}
            <div className="flex items-start gap-6">
              <motion.div
                className="w-32 h-32 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center text-5xl font-bold"
                animate={{
                  boxShadow: [
                    '0 0 20px rgba(0, 243, 255, 0.3)',
                    '0 0 40px rgba(188, 19, 254, 0.4)',
                    '0 0 20px rgba(0, 243, 255, 0.3)',
                  ],
                }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                {agent.name[0]}
              </motion.div>

              <div>
                <h1 className="text-4xl font-bold text-white mb-2">{agent.name}</h1>
                <p className="text-lg text-white/60 mb-4">{agent.role}</p>

                <div className="flex flex-wrap gap-4 mb-4">
                  <div>
                    <p className="text-xs text-white/50 mb-1">Aura Level</p>
                    <p className="text-2xl font-bold text-cyan-400">{agent.auraLevel}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/50 mb-1">Status</p>
                    <div className="flex items-center gap-2">
                      <motion.div
                        className="w-3 h-3 rounded-full bg-emerald-400"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                      <p className="text-lg font-bold text-emerald-400 capitalize">{agent.status}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-white/50 mb-1">Interactions</p>
                    <p className="text-2xl font-bold text-purple-400">{agent.totalInteractions}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col gap-3">
              <Link href={`/chat?agent=${agentId}`}>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-bold hover:shadow-lg transition-all"
                >
                  Start Chat
                </motion.button>
              </Link>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 rounded-lg border border-white/20 text-white hover:border-cyan-500 transition-colors font-medium"
              >
                Follow Agent
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Description */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="lg:col-span-2 rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10"
          >
            <h3 className="text-xl font-bold text-white mb-4">About</h3>
            <p className="text-white/70 leading-relaxed mb-6">{agent.description}</p>

            <div>
              <h4 className="text-sm font-bold text-white/80 mb-3 uppercase tracking-wider">
                Expertise
              </h4>
              <p className="text-white/60 text-sm">{agent.expertise}</p>
            </div>
          </motion.div>

          {/* Meta Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10"
          >
            <h3 className="text-xl font-bold text-white mb-4">Information</h3>

            <div className="space-y-4">
              <div>
                <p className="text-xs text-white/50 mb-1">Created</p>
                <p className="text-sm text-white/70">
                  {agent.createdAt.toLocaleDateString()}
                </p>
              </div>
              <div className="pt-4 border-t border-white/10">
                <p className="text-xs text-white/50 mb-3 uppercase tracking-wider">Agent ID</p>
                <p className="text-xs text-cyan-400 font-mono break-all bg-white/5 p-2 rounded">
                  {agent.id}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Skills Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10 mb-8"
        >
          <h3 className="text-xl font-bold text-white mb-6">Skills & Capabilities</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {agent.skills.map((skill, index) => (
              <motion.div
                key={skill}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.35 + index * 0.05 }}
                className="px-4 py-3 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-white/10 hover:border-cyan-500/50 transition-colors"
              >
                <p className="text-white/80 font-medium">{skill}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="grid grid-cols-3 gap-4"
        >
          <div className="rounded-xl p-6 bg-white/5 border border-white/10">
            <p className="text-white/60 text-sm mb-2">Conversations</p>
            <p className="text-3xl font-bold text-cyan-400">{agent.totalInteractions}</p>
          </div>
          <div className="rounded-xl p-6 bg-white/5 border border-white/10">
            <p className="text-white/60 text-sm mb-2">User Satisfaction</p>
            <p className="text-3xl font-bold text-purple-400">98%</p>
          </div>
          <div className="rounded-xl p-6 bg-white/5 border border-white/10">
            <p className="text-white/60 text-sm mb-2">Response Time</p>
            <p className="text-3xl font-bold text-pink-400">{Math.floor(Math.random() * 1000)}ms</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
