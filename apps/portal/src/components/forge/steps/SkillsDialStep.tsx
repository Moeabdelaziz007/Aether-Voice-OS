'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

interface Skill {
  id: string;
  name: string;
  description: string;
  category: 'core' | 'analysis' | 'creation' | 'integration';
}

interface SkillsDialStepProps {
  selectedSkills?: string[];
  onSkillToggle?: (skillId: string) => void;
  isListening?: boolean;
}

const DEFAULT_SKILLS: Skill[] = [
  {
    id: 'reasoning',
    name: 'Advanced Reasoning',
    description: 'Multi-step logical analysis',
    category: 'core',
  },
  {
    id: 'learning',
    name: 'Continuous Learning',
    description: 'Adapt from new information',
    category: 'core',
  },
  {
    id: 'research',
    name: 'Research & Analysis',
    description: 'Deep data synthesis',
    category: 'analysis',
  },
  {
    id: 'coding',
    name: 'Code Generation',
    description: 'Write and debug code',
    category: 'creation',
  },
  {
    id: 'writing',
    name: 'Creative Writing',
    description: 'Narrative composition',
    category: 'creation',
  },
  {
    id: 'integration',
    name: 'Tool Integration',
    description: 'Connect external APIs',
    category: 'integration',
  },
  {
    id: 'planning',
    name: 'Strategic Planning',
    description: 'Goal decomposition',
    category: 'analysis',
  },
  {
    id: 'communication',
    name: 'Communication',
    description: 'Clear explanations',
    category: 'core',
  },
];

export default function SkillsDialStep({
  selectedSkills = [],
  onSkillToggle,
  isListening = false,
}: SkillsDialStepProps) {
  const [rotation, setRotation] = useState(0);
  const [activeSkills, setActiveSkills] = useState<Set<string>>(new Set(selectedSkills));
  const [dialFill, setDialFill] = useState(0);

  // Dial rotation animation
  useEffect(() => {
    const interval = setInterval(() => {
      setRotation((r) => (r + 0.5) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Update dial fill based on selected skills
  useEffect(() => {
    const fillPercentage = (activeSkills.size / DEFAULT_SKILLS.length) * 100;
    setDialFill(fillPercentage);
  }, [activeSkills.size]);

  const toggleSkill = (skillId: string) => {
    const newSkills = new Set(activeSkills);
    if (newSkills.has(skillId)) {
      newSkills.delete(skillId);
    } else {
      newSkills.add(skillId);
    }
    setActiveSkills(newSkills);
    if (onSkillToggle) {
      onSkillToggle(skillId);
    }
  };

  const getSkillAngle = (index: number) => {
    return (index / DEFAULT_SKILLS.length) * 360;
  };

  const getSkillPosition = (angle: number) => {
    const radius = 200;
    const rad = (angle * Math.PI) / 180;
    return {
      x: Math.cos(rad) * radius,
      y: Math.sin(rad) * radius,
    };
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'core':
        return 'from-cyan-500 to-cyan-600';
      case 'analysis':
        return 'from-blue-500 to-blue-600';
      case 'creation':
        return 'from-purple-500 to-purple-600';
      case 'integration':
        return 'from-emerald-500 to-emerald-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <div className="relative w-full min-h-screen bg-gradient-to-b from-black via-purple-900/10 to-black flex flex-col items-center justify-center overflow-hidden p-6">
      {/* Title */}
      <motion.div
        className="relative z-10 mb-12 text-center"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-cyan-400 to-emerald-400 mb-2">
          SKILLS AUTONOMY
        </h1>
        <p className="text-lg text-gray-300">
          Define agent capabilities through voice narration
        </p>
      </motion.div>

      {/* Central Circular Dial */}
      <div className="relative z-20 mb-16">
        {/* Outer dial rings */}
        <svg
          className="absolute w-[600px] h-[600px] -left-[300px] -top-[300px]"
          viewBox="0 0 600 600"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Background rings */}
          <circle
            cx="300"
            cy="300"
            r="250"
            fill="none"
            stroke="rgba(0, 255, 200, 0.1)"
            strokeWidth="1"
          />
          <circle
            cx="300"
            cy="300"
            r="200"
            fill="none"
            stroke="rgba(168, 85, 247, 0.1)"
            strokeWidth="1"
            strokeDasharray="5,5"
          />
          <circle
            cx="300"
            cy="300"
            r="150"
            fill="none"
            stroke="rgba(0, 200, 255, 0.1)"
            strokeWidth="1"
          />

          {/* Fill arc */}
          <defs>
            <linearGradient
              id="fillGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="rgba(0, 255, 200, 0.4)" />
              <stop offset="100%" stopColor="rgba(168, 85, 247, 0.4)" />
            </linearGradient>
          </defs>

          <motion.path
            d={`M 300 300 L 300 50 A 250 250 0 ${dialFill > 50 ? 1 : 0} 1 ${
              300 + 250 * Math.sin((dialFill * Math.PI) / 100)
            } ${
              300 - 250 * Math.cos((dialFill * Math.PI) / 100)
            } Z`}
            fill="url(#fillGradient)"
            animate={{
              d: `M 300 300 L 300 50 A 250 250 0 ${dialFill > 50 ? 1 : 0} 1 ${
                300 + 250 * Math.sin((dialFill * Math.PI) / 100)
              } ${
                300 - 250 * Math.cos((dialFill * Math.PI) / 100)
              } Z`,
            }}
            transition={{ duration: 0.5 }}
          />

          {/* Listening pulse ring (when isListening) */}
          {isListening && (
            <motion.circle
              cx="300"
              cy="300"
              r="280"
              fill="none"
              stroke="rgba(0, 255, 200, 0.3)"
              strokeWidth="2"
              animate={{
                r: [280, 320],
                opacity: [1, 0],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
              }}
            />
          )}
        </svg>

        {/* Center nucleus with percentage */}
        <motion.div
          className="relative w-40 h-40 rounded-full flex items-center justify-center"
          animate={{
            boxShadow: [
              '0 0 30px rgba(0, 255, 200, 0.3)',
              '0 0 60px rgba(168, 85, 247, 0.4)',
              '0 0 30px rgba(0, 255, 200, 0.3)',
            ],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="absolute inset-0 rounded-full bg-gradient-conic from-cyan-500/30 via-purple-500/20 to-cyan-500/30 blur-xl" />
          <div className="absolute inset-0 rounded-full border-2 border-cyan-500/50 backdrop-blur-sm" />
          <div className="relative z-10 text-center">
            <motion.div
              className="text-4xl font-bold text-cyan-300"
              key={dialFill}
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              {Math.round(dialFill)}%
            </motion.div>
            <p className="text-xs text-gray-400 mt-2">Capacity</p>
          </div>
        </motion.div>
      </div>

      {/* Skills arranged in circle */}
      <div className="relative z-20 w-[600px] h-[600px] flex items-center justify-center mb-12">
        {DEFAULT_SKILLS.map((skill, idx) => {
          const angle = getSkillAngle(idx);
          const pos = getSkillPosition(angle);
          const isActive = activeSkills.has(skill.id);
          const rad = (angle * Math.PI) / 180;

          return (
            <motion.button
              key={skill.id}
              onClick={() => toggleSkill(skill.id)}
              className={`absolute w-24 h-24 rounded-xl backdrop-blur-sm border-2 flex flex-col items-center justify-center transition-all ${
                isActive
                  ? `bg-gradient-to-br ${getCategoryColor(skill.category)} shadow-lg`
                  : 'bg-white/5 border-white/20 hover:border-white/40'
              }`}
              style={{
                left: `${300 + pos.x}px`,
                top: `${300 + pos.y}px`,
                transform: 'translate(-50%, -50%)',
              }}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
            >
              {/* Active indicator glow */}
              {isActive && (
                <motion.div
                  className="absolute inset-0 rounded-xl blur-md opacity-50"
                  style={{
                    background: `linear-gradient(135deg, var(--color-from), var(--color-to))`,
                  }}
                  animate={{ opacity: [0.3, 0.7, 0.3] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              )}

              {/* Content */}
              <div className="relative z-10 text-center">
                <span className="text-lg mb-1 block">
                  {skill.category === 'core' && '⚙️'}
                  {skill.category === 'analysis' && '🔬'}
                  {skill.category === 'creation' && '✨'}
                  {skill.category === 'integration' && '🔗'}
                </span>
                <p className="text-xs font-semibold text-white leading-tight">
                  {skill.name}
                </p>
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Status bar */}
      <motion.div
        className="relative z-20 text-center text-sm text-gray-400"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p>
          Selected skills:{' '}
          <span className="text-cyan-300 font-semibold">{activeSkills.size} / {DEFAULT_SKILLS.length}</span>
        </p>
        <p className="text-xs mt-2 text-gray-500">
          {isListening ? '🎙️ Listening for skill descriptions...' : 'Click skills or speak to add...'}
        </p>
      </motion.div>
    </div>
  );
}
