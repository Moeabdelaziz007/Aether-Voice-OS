'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

interface IdentityCustomizationStepProps {
  auraLevel?: number;
  onAuraChange?: (level: number) => void;
  toneResonance?: number;
  onToneChange?: (tone: number) => void;
  personalityTraits?: string[];
  onTraitToggle?: (trait: string) => void;
}

const PERSONALITY_TRAITS = [
  { id: 'analytical', label: 'Analytical', emoji: '🧠' },
  { id: 'creative', label: 'Creative', emoji: '🎨' },
  { id: 'empathetic', label: 'Empathetic', emoji: '💚' },
  { id: 'logical', label: 'Logical', emoji: '⚡' },
  { id: 'curious', label: 'Curious', emoji: '🔍' },
  { id: 'patient', label: 'Patient', emoji: '🕐' },
  { id: 'focused', label: 'Focused', emoji: '🎯' },
  { id: 'adaptable', label: 'Adaptable', emoji: '🔄' },
];

export default function IdentityCustomizationStep({
  auraLevel = 50,
  onAuraChange,
  toneResonance = 50,
  onToneChange,
  personalityTraits = [],
  onTraitToggle,
}: IdentityCustomizationStepProps) {
  const [currentAura, setCurrentAura] = useState(auraLevel);
  const [currentTone, setCurrentTone] = useState(toneResonance);
  const [activeTraits, setActiveTraits] = useState<Set<string>>(new Set(personalityTraits));
  const [environmentTheme, setEnvironmentTheme] = useState<'dark' | 'ethereal' | 'cosmic'>('dark');

  // Update environment based on aura level
  useEffect(() => {
    if (currentAura < 33) {
      setEnvironmentTheme('dark');
    } else if (currentAura < 66) {
      setEnvironmentTheme('ethereal');
    } else {
      setEnvironmentTheme('cosmic');
    }
  }, [currentAura]);

  const handleAuraChange = (newValue: number) => {
    setCurrentAura(newValue);
    if (onAuraChange) {
      onAuraChange(newValue);
    }
  };

  const handleToneChange = (newValue: number) => {
    setCurrentTone(newValue);
    if (onToneChange) {
      onToneChange(newValue);
    }
  };

  const handleTraitToggle = (traitId: string) => {
    const newTraits = new Set(activeTraits);
    if (newTraits.has(traitId)) {
      newTraits.delete(traitId);
    } else {
      newTraits.add(traitId);
    }
    setActiveTraits(newTraits);
    if (onTraitToggle) {
      onTraitToggle(traitId);
    }
  };

  const getEnvironmentGradient = () => {
    switch (environmentTheme) {
      case 'dark':
        return 'from-black via-gray-900 to-black';
      case 'ethereal':
        return 'from-blue-950 via-purple-900 to-blue-950';
      case 'cosmic':
        return 'from-indigo-950 via-purple-900 to-pink-900';
      default:
        return 'from-black via-gray-900 to-black';
    }
  };

  const getToneLabel = () => {
    if (currentTone < 25) return 'Clinical';
    if (currentTone < 50) return 'Professional';
    if (currentTone < 75) return 'Conversational';
    return 'Playful';
  };

  const getAuraLabel = () => {
    if (currentAura < 25) return 'Subtle';
    if (currentAura < 50) return 'Moderate';
    if (currentAura < 75) return 'Radiant';
    return 'Luminous';
  };

  return (
    <motion.div
      className={`relative w-full min-h-screen bg-gradient-to-b ${getEnvironmentGradient()} flex flex-col items-center justify-center overflow-hidden p-6 transition-all duration-1000`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* Dynamic background based on theme */}
      <motion.div
        className="absolute inset-0 opacity-20"
        animate={{
          background:
            environmentTheme === 'dark'
              ? 'radial-gradient(circle, rgba(0,255,200,0.1) 0%, transparent 70%)'
              : environmentTheme === 'ethereal'
              ? 'radial-gradient(circle, rgba(168,85,247,0.15) 0%, transparent 70%)'
              : 'radial-gradient(circle, rgba(236,72,153,0.1) 0%, transparent 70%)',
        }}
        transition={{ duration: 1 }}
      />

      {/* Title */}
      <motion.div
        className="relative z-10 mb-12 text-center"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 mb-2">
          IDENTITY RESONANCE
        </h1>
        <p className="text-lg text-gray-300">
          Fine-tune your agent's essence and presence
        </p>
      </motion.div>

      {/* Main control panel */}
      <motion.div
        className="relative z-20 max-w-2xl w-full rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-12 mb-12"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {/* Aura Level Control */}
        <div className="mb-12">
          <div className="flex justify-between items-center mb-4">
            <label className="text-lg font-semibold text-cyan-300">Aura Level</label>
            <motion.span
              className="text-sm font-mono text-gray-400"
              key={currentAura}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {getAuraLabel()} ({currentAura}%)
            </motion.span>
          </div>

          {/* Slider */}
          <motion.div className="relative h-16 flex items-center">
            <input
              type="range"
              min="0"
              max="100"
              value={currentAura}
              onChange={(e) => handleAuraChange(Number(e.target.value))}
              className="w-full h-2 bg-gradient-to-r from-gray-700 to-gray-600 rounded-lg appearance-none cursor-pointer accent-cyan-500 slider"
              style={{
                background: `linear-gradient(to right, rgba(0,255,200,0.3) 0%, rgba(0,255,200,0.7) ${currentAura}%, rgba(100,100,100,0.3) ${currentAura}%, rgba(100,100,100,0.2) 100%)`,
              }}
            />

            {/* Animated value indicator */}
            <motion.div
              className="absolute top-8 left-0 bg-cyan-500/20 border border-cyan-500/50 rounded px-3 py-1 text-xs text-cyan-300 pointer-events-none"
              style={{
                left: `calc(${currentAura}% - 30px)`,
              }}
              animate={{
                boxShadow: [
                  '0 0 10px rgba(0, 255, 200, 0.4)',
                  '0 0 20px rgba(0, 255, 200, 0.6)',
                  '0 0 10px rgba(0, 255, 200, 0.4)',
                ],
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              {currentAura}
            </motion.div>
          </motion.div>

          {/* Visual representation */}
          <motion.div
            className="mt-6 h-16 rounded-lg border border-cyan-500/30 bg-gradient-to-r from-cyan-500/10 to-cyan-500/5 overflow-hidden"
            animate={{
              boxShadow: [
                `0 0 20px rgba(0, 255, 200, ${0.1 + currentAura / 500})`,
                `0 0 40px rgba(0, 255, 200, ${0.2 + currentAura / 500})`,
                `0 0 20px rgba(0, 255, 200, ${0.1 + currentAura / 500})`,
              ],
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <motion.div
              className="h-full bg-gradient-conic from-cyan-500 via-purple-500 to-cyan-500 blur-lg"
              style={{ width: `${currentAura}%` }}
              animate={{
                width: `${currentAura}%`,
              }}
              transition={{ duration: 0.5 }}
            />
          </motion.div>
        </div>

        {/* Tone Resonance Control */}
        <div className="mb-12">
          <div className="flex justify-between items-center mb-4">
            <label className="text-lg font-semibold text-purple-300">Tone Resonance</label>
            <motion.span
              className="text-sm font-mono text-gray-400"
              key={currentTone}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {getToneLabel()} ({currentTone}%)
            </motion.span>
          </div>

          {/* Slider */}
          <motion.div className="relative h-16 flex items-center">
            <input
              type="range"
              min="0"
              max="100"
              value={currentTone}
              onChange={(e) => handleToneChange(Number(e.target.value))}
              className="w-full h-2 bg-gradient-to-r from-gray-700 to-gray-600 rounded-lg appearance-none cursor-pointer accent-purple-500 slider"
              style={{
                background: `linear-gradient(to right, rgba(168,85,247,0.3) 0%, rgba(168,85,247,0.7) ${currentTone}%, rgba(100,100,100,0.3) ${currentTone}%, rgba(100,100,100,0.2) 100%)`,
              }}
            />

            {/* Animated value indicator */}
            <motion.div
              className="absolute top-8 left-0 bg-purple-500/20 border border-purple-500/50 rounded px-3 py-1 text-xs text-purple-300 pointer-events-none"
              style={{
                left: `calc(${currentTone}% - 30px)`,
              }}
              animate={{
                boxShadow: [
                  '0 0 10px rgba(168, 85, 247, 0.4)',
                  '0 0 20px rgba(168, 85, 247, 0.6)',
                  '0 0 10px rgba(168, 85, 247, 0.4)',
                ],
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              {currentTone}
            </motion.div>
          </motion.div>

          {/* Tone spectrum visualization */}
          <div className="mt-6 h-8 rounded-lg overflow-hidden border border-purple-500/30">
            <div className="h-full flex">
              {['Clinical', 'Professional', 'Conversational', 'Playful'].map((label, idx) => (
                <div
                  key={label}
                  className="flex-1 flex items-center justify-center text-xs font-mono text-gray-500 border-r border-purple-500/20 last:border-r-0"
                >
                  {label}
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Personality Traits Selection */}
      <motion.div
        className="relative z-20 max-w-2xl w-full"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <h2 className="text-xl font-semibold text-gray-300 mb-6">Personality Traits</h2>

        <motion.div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {PERSONALITY_TRAITS.map((trait, idx) => {
            const isActive = activeTraits.has(trait.id);

            return (
              <motion.button
                key={trait.id}
                onClick={() => handleTraitToggle(trait.id)}
                className={`relative p-4 rounded-xl border-2 backdrop-blur-sm transition-all ${
                  isActive
                    ? 'bg-gradient-to-br from-purple-500/30 to-cyan-500/20 border-purple-500/70 shadow-lg shadow-purple-500/30'
                    : 'bg-white/5 border-white/20 hover:border-white/40'
                }`}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.92 }}
              >
                {isActive && (
                  <motion.div
                    className="absolute inset-0 rounded-xl bg-purple-400/20 blur-md"
                    animate={{ opacity: [0.3, 0.7, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                )}

                <div className="relative z-10 text-center">
                  <div className="text-3xl mb-2">{trait.emoji}</div>
                  <p className="text-sm font-semibold text-gray-200">{trait.label}</p>
                </div>
              </motion.button>
            );
          })}
        </motion.div>
      </motion.div>

      {/* Status summary */}
      <motion.div
        className="relative z-20 mt-12 text-center text-sm text-gray-400"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <p>
          Traits selected:{' '}
          <span className="text-purple-300 font-semibold">{activeTraits.size} / {PERSONALITY_TRAITS.length}</span>
        </p>
        <p className="text-xs mt-2">
          Environment: <span className="text-cyan-300 font-semibold">{environmentTheme}</span>
        </p>
      </motion.div>

      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgba(0,255,200,0.8), rgba(168,85,247,0.8));
          cursor: pointer;
          box-shadow: 0 0 15px rgba(0,255,200,0.5);
          border: 2px solid white;
        }

        .slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgba(0,255,200,0.8), rgba(168,85,247,0.8));
          cursor: pointer;
          box-shadow: 0 0 15px rgba(0,255,200,0.5);
          border: 2px solid white;
        }
      `}</style>
    </motion.div>
  );
}
