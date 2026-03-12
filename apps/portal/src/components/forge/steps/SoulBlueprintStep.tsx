'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

interface MemoryCrystal {
  id: string;
  label: string;
  intensity: number;
  angle: number;
}

interface SoulBlueprintStepProps {
  agentName: string;
  agentPersona: string;
  memoryCrystals?: MemoryCrystal[];
  onCrystalActivate?: (crystalId: string) => void;
  isLoading?: boolean;
}

export default function SoulBlueprintStep({
  agentName,
  agentPersona,
  memoryCrystals = [],
  onCrystalActivate,
  isLoading = false,
}: SoulBlueprintStepProps) {
  const [activeCrystals, setActiveCrystals] = useState<Set<string>>(new Set());
  const [hologramRotation, setHologramRotation] = useState(0);

  // Hologram rotation animation
  useEffect(() => {
    const interval = setInterval(() => {
      setHologramRotation((r) => (r + 0.5) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const defaultCrystals: MemoryCrystal[] =
    memoryCrystals.length > 0
      ? memoryCrystals
      : [
          { id: 'core', label: 'Core Identity', intensity: 0.9, angle: 0 },
          { id: 'knowledge', label: 'Knowledge Base', intensity: 0.7, angle: 45 },
          { id: 'skills', label: 'Skill Matrix', intensity: 0.6, angle: 90 },
          { id: 'memory', label: 'Long-term Memory', intensity: 0.5, angle: 135 },
          { id: 'reasoning', label: 'Logic Gates', intensity: 0.8, angle: 180 },
          { id: 'creativity', label: 'Creative Impulse', intensity: 0.4, angle: 225 },
          { id: 'adaptation', label: 'Adaptive Engine', intensity: 0.7, angle: 270 },
          { id: 'ethics', label: 'Ethics Module', intensity: 0.6, angle: 315 },
        ];

  const handleCrystalClick = (crystalId: string) => {
    const newActive = new Set(activeCrystals);
    if (newActive.has(crystalId)) {
      newActive.delete(crystalId);
    } else {
      newActive.add(crystalId);
    }
    setActiveCrystals(newActive);
    if (onCrystalActivate) {
      onCrystalActivate(crystalId);
    }
  };

  const getCrystalPosition = (angle: number) => {
    const radius = 180;
    const rad = (angle * Math.PI) / 180;
    return {
      x: Math.cos(rad) * radius,
      y: Math.sin(rad) * radius,
    };
  };

  return (
    <div className="relative w-full min-h-screen bg-gradient-to-b from-black via-blue-900/10 to-black flex flex-col items-center justify-center overflow-hidden p-6">
      {/* Background holographic grid */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full">
          <defs>
            <pattern
              id="grid"
              width="40"
              height="40"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="cyan"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Title section */}
      <motion.div
        className="relative z-10 mb-12 text-center"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 mb-2">
          SOUL BLUEPRINTING
        </h1>
        <p className="text-lg text-gray-300">
          Forging the consciousness of <span className="text-cyan-300 font-semibold">{agentName}</span>
        </p>
      </motion.div>

      {/* Central Holographic Skeleton */}
      <div className="relative z-20 w-96 h-96 flex items-center justify-center mb-12">
        {/* Holographic skeleton outline */}
        <motion.div
          className="absolute inset-0 rounded-3xl border-2 border-cyan-500/30 backdrop-blur-sm"
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-purple-500/5 rounded-3xl" />
        </motion.div>

        {/* Core nucleus */}
        <motion.div
          className="relative w-32 h-32 rounded-full"
          animate={{
            boxShadow: [
              '0 0 20px rgba(0, 255, 200, 0.5)',
              '0 0 40px rgba(168, 85, 247, 0.5)',
              '0 0 20px rgba(0, 255, 200, 0.5)',
            ],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="absolute inset-0 rounded-full bg-gradient-conic from-cyan-500 via-purple-500 to-cyan-500 blur-lg opacity-70" />
          <div className="absolute inset-2 rounded-full bg-black/80 backdrop-blur-sm border border-cyan-500/50" />
          <div className="absolute inset-4 rounded-full bg-gradient-to-br from-cyan-400/30 to-purple-400/20 flex items-center justify-center">
            <span className="text-xs font-mono text-cyan-300">DNA</span>
          </div>
        </motion.div>

        {/* Memory Crystal Ring */}
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 400 400"
          xmlns="http://www.w3.org/2000/svg"
          style={{ transform: `rotate(${hologramRotation}deg)` }}
        >
          {/* Orbital path */}
          <circle
            cx="200"
            cy="200"
            r="150"
            fill="none"
            stroke="rgba(0, 255, 200, 0.2)"
            strokeWidth="1"
            strokeDasharray="5,5"
          />
          {/* Connection lines to crystals */}
          {defaultCrystals.map((crystal) => {
            const pos = getCrystalPosition(crystal.angle);
            const scaledX = pos.x + 200;
            const scaledY = pos.y + 200;
            const isActive = activeCrystals.has(crystal.id);
            return (
              <line
                key={`line-${crystal.id}`}
                x1="200"
                y1="200"
                x2={scaledX}
                y2={scaledY}
                stroke={isActive ? 'rgba(0, 255, 200, 0.8)' : 'rgba(100, 100, 255, 0.3)'}
                strokeWidth={isActive ? 2 : 1}
              />
            );
          })}
        </svg>
      </div>

      {/* Memory Crystals - Interactive */}
      <motion.div
        className="relative z-20 grid grid-cols-2 md:grid-cols-4 gap-4 mb-12 max-w-4xl mx-auto"
        layout
      >
        {defaultCrystals.map((crystal, idx) => {
          const isActive = activeCrystals.has(crystal.id);
          const pos = getCrystalPosition(crystal.angle);

          return (
            <motion.button
              key={crystal.id}
              onClick={() => handleCrystalClick(crystal.id)}
              className={`relative p-4 rounded-xl border-2 backdrop-blur-sm transition-all ${
                isActive
                  ? 'bg-cyan-500/20 border-cyan-500 shadow-lg shadow-cyan-500/50'
                  : 'bg-purple-500/10 border-purple-500/30 hover:border-purple-500/60'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08 }}
            >
              {/* Crystal glow */}
              {isActive && (
                <motion.div
                  className="absolute inset-0 rounded-xl bg-cyan-400/20 blur-md"
                  animate={{ opacity: [0.3, 0.7, 0.3] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}

              {/* Crystal content */}
              <div className="relative z-10 text-center">
                <motion.div
                  className="text-2xl mb-2"
                  animate={isActive ? { scale: [1, 1.2, 1] } : {}}
                  transition={{ duration: 0.6, repeat: Infinity }}
                >
                  💎
                </motion.div>
                <p className="text-xs font-mono text-gray-300">{crystal.label}</p>
                <motion.div
                  className="mt-2 h-1 bg-gradient-to-r from-cyan-500/0 via-cyan-500 to-cyan-500/0 rounded-full"
                  animate={isActive ? { scaleX: [0, 1, 0] } : { scaleX: 0 }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  style={{ originX: 0.5 }}
                />
              </div>
            </motion.button>
          );
        })}
      </motion.div>

      {/* Status information */}
      <motion.div
        className="relative z-20 text-center text-sm text-gray-400"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p>
          Memories activated:{' '}
          <span className="text-cyan-300 font-semibold">{activeCrystals.size} / {defaultCrystals.length}</span>
        </p>
        {isLoading && (
          <div className="mt-4 flex items-center justify-center gap-2">
            <motion.div
              className="w-2 h-2 rounded-full bg-cyan-400"
              animate={{ scale: [1, 0.5, 1] }}
              transition={{ duration: 0.6, repeat: Infinity }}
            />
            <span className="text-xs text-gray-500">DNA synthesis in progress...</span>
          </div>
        )}
      </motion.div>
    </div>
  );
}
