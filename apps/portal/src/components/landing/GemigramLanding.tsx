'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import NeuralOrb from './NeuralOrb';
import AgentHiveCards from './AgentHiveCards';
import VoiceSynthesisPanel from './VoiceSynthesisPanel';
import { GlobalAgent } from '@/store/types';

interface GemigramLandingProps {
  onConnectClick?: () => void;
  onCreateAgentClick?: () => void;
}

const FEATURED_AGENTS: GlobalAgent[] = [
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

export default function GemigramLanding({
  onConnectClick,
  onCreateAgentClick,
}: GemigramLandingProps) {
  const [isHovering, setIsHovering] = useState(false);

  const handleConnectClick = useCallback(() => {
    onConnectClick?.();
  }, [onConnectClick]);

  const handleCreateAgentClick = useCallback(() => {
    onCreateAgentClick?.();
  }, [onCreateAgentClick]);

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-black">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px),
                              linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      {/* Animated Background Glow */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full opacity-20 pointer-events-none"
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.15, 0.25, 0.15],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          background: 'radial-gradient(circle, #00F3FF 0%, #BC13FE 50%, transparent 100%)',
          filter: 'blur(40px)',
        }}
      />

      {/* Navigation Header */}
      <nav className="relative z-40 flex items-center justify-between px-8 py-6 border-b border-white/5">
        <motion.h1
          className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
          whileHover={{ scale: 1.05 }}
        >
          GEMIGRAM
        </motion.h1>

        <div className="flex items-center gap-8">
          <Link
            href="/discover"
            className="text-sm text-white/70 hover:text-white transition-colors"
          >
            Discover
          </Link>
          <Link
            href="/create"
            className="text-sm text-white/70 hover:text-white transition-colors"
          >
            Create
          </Link>
          <Link
            href="/hub"
            className="text-sm text-white/70 hover:text-white transition-colors"
          >
            Hub
          </Link>
          <Link
            href="/login"
            className="text-sm text-white/70 hover:text-white transition-colors"
          >
            Login
          </Link>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          >
            <svg
              className="w-5 h-5 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </motion.button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-30 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-4">
        {/* Neural Orb */}
        <motion.div
          className="mb-12"
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          <NeuralOrb isHovering={isHovering} />
        </motion.div>

        {/* Main Heading */}
        <motion.div
          className="text-center mb-8 max-w-2xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              GEMIGRAM
            </span>
          </h2>
          <p className="text-lg text-white/60 tracking-wide">
            The Voice-Native AI Social Nexus.
          </p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <motion.button
            onClick={handleConnectClick}
            whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(188, 19, 254, 0.5)' }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-3 rounded-lg border border-purple-500/50 text-white font-medium hover:bg-purple-500/10 transition-colors"
          >
            CONNECT NOW
          </motion.button>

          <Link href="/create">
            <motion.button
              whileHover={{ scale: 1.05, color: '#00F3FF' }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 text-cyan-400 font-bold tracking-wider hover:text-cyan-300 transition-colors"
            >
              CREATE AGENT
            </motion.button>
          </Link>
        </motion.div>

        {/* Agent Hive Section */}
        <motion.div
          className="w-full max-w-6xl mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h3 className="text-xl font-bold text-cyan-400 tracking-widest mb-6 text-center">
            AGENT HIVE
          </h3>
          <AgentHiveCards agents={FEATURED_AGENTS} />
        </motion.div>

        {/* Voice Synthesis Section */}
        <motion.div
          className="w-full max-w-3xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <h3 className="text-xl font-bold text-purple-400 tracking-widest mb-6 text-center">
            VOICE SYNTHESIS
          </h3>
          <VoiceSynthesisPanel />
        </motion.div>
      </div>
    </div>
  );
}
