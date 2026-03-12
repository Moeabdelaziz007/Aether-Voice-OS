'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { GlobalAgent } from '@/store/types';

interface AgentHiveCardsProps {
  agents: GlobalAgent[];
}

const getGlowColor = (index: number): string => {
  const colors = ['#00F3FF', '#BC13FE', '#00F3FF', '#BC13FE', '#10B981'];
  return colors[index % colors.length];
};

export default function AgentHiveCards({ agents }: AgentHiveCardsProps) {
  return (
    <div className="overflow-x-auto pb-4 scrollbar-hide">
      <motion.div
        className="flex gap-4 px-4 min-w-min"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1, delayChildren: 0.2 }}
      >
        {agents.map((agent, index) => {
          const glowColor = getGlowColor(index);
          const isGlowing = glowColor === '#00F3FF' || glowColor === '#BC13FE';

          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{
                scale: 1.05,
                boxShadow: `0 0 30px ${glowColor}80`,
              }}
              transition={{ duration: 0.4 }}
              className="min-w-[280px] group"
            >
              <Link href={`/agent/${agent.id}`}>
                <div
                  className="h-80 rounded-xl p-4 backdrop-blur-xl bg-black/40 border transition-all duration-300 flex flex-col justify-between overflow-hidden cursor-pointer"
                  style={{
                    borderColor: `${glowColor}40`,
                    background: `linear-gradient(135deg, rgba(0, 0, 0, 0.4), rgba(${glowColor === '#00F3FF' ? '0, 243, 255' : '188, 19, 254'}, 0.05))`,
                  }}
                >
                  {/* Background glow effect */}
                  <motion.div
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    animate={{
                      boxShadow: [
                        `inset 0 0 20px ${glowColor}20`,
                        `inset 0 0 40px ${glowColor}40`,
                        `inset 0 0 20px ${glowColor}20`,
                      ],
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />

                  {/* Avatar placeholder with glow */}
                  <motion.div
                    className="relative mx-auto mb-4 w-24 h-24 rounded-lg flex items-center justify-center overflow-hidden"
                    animate={{
                      boxShadow: isGlowing
                        ? [
                            `0 0 20px ${glowColor}60`,
                            `0 0 40px ${glowColor}80`,
                            `0 0 20px ${glowColor}60`,
                          ]
                        : undefined,
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    style={{
                      border: `2px solid ${glowColor}80`,
                      background: `linear-gradient(135deg, ${glowColor}20, ${glowColor}05)`,
                    }}
                  >
                    {/* Placeholder AI avatar */}
                    <div className="w-full h-full flex items-center justify-center text-2xl font-bold">
                      {agent.name[0]}
                    </div>
                  </motion.div>

                  {/* Agent Info */}
                  <div className="relative z-10 text-center mb-4 flex-1 flex flex-col justify-start">
                    <h3 className="text-lg font-bold text-white mb-1">
                      {agent.name}
                    </h3>
                    <p className="text-xs text-white/50 mb-2">{agent.role}</p>

                    {/* Status */}
                    <div className="flex items-center justify-center gap-2">
                      <motion.div
                        className="w-2 h-2 rounded-full bg-emerald-400"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                      <span className="text-xs text-white/40 capitalize">
                        {agent.status}
                      </span>
                    </div>
                  </div>

                  {/* Aura Level */}
                  <motion.div
                    className="relative z-10 pt-4 border-t"
                    style={{ borderColor: `${glowColor}20` }}
                  >
                    <div className="flex items-center justify-between text-xs text-white/60">
                      <span className="text-white/40">Aura Level</span>
                      <motion.span
                        className="text-white font-mono font-bold"
                        style={{ color: glowColor }}
                      >
                        {agent.auraLevel}
                      </motion.span>
                    </div>

                    {/* Progress bar */}
                    <motion.div
                      className="w-full h-1 rounded-full mt-2 overflow-hidden"
                      style={{ background: `${glowColor}20` }}
                    >
                      <motion.div
                        className="h-full rounded-full"
                        style={{ background: glowColor }}
                        animate={{
                          width: [`${(agent.auraLevel % 100)}%`, `${((agent.auraLevel + 10) % 100)}%`],
                        }}
                        transition={{ duration: 3, repeat: Infinity }}
                      />
                    </motion.div>
                  </motion.div>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}
