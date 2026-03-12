'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { AgentCreationStep } from '@/store/types';

const STEPS: { id: AgentCreationStep; label: string; description: string }[] = [
  {
    id: 'identity',
    label: 'Identity',
    description: 'Define your agent\'s name and role',
  },
  {
    id: 'brain',
    label: 'Brain',
    description: 'Configure skills and expertise',
  },
  {
    id: 'voice',
    label: 'Voice',
    description: 'Set voice characteristics',
  },
  {
    id: 'review',
    label: 'Review',
    description: 'Verify before deployment',
  },
  {
    id: 'deploy',
    label: 'Deploy',
    description: 'Launch your agent',
  },
];

export default function CreateAgentPage() {
  const [currentStep, setCurrentStep] = useState<AgentCreationStep>('identity');
  const [agentName, setAgentName] = useState('');
  const [agentRole, setAgentRole] = useState('');

  const currentStepIndex = STEPS.findIndex((s) => s.id === currentStep);
  const progress = ((currentStepIndex + 1) / STEPS.length) * 100;

  const handleNext = useCallback(() => {
    if (currentStepIndex < STEPS.length - 1) {
      setCurrentStep(STEPS[currentStepIndex + 1].id);
    }
  }, [currentStepIndex]);

  const handlePrev = useCallback(() => {
    if (currentStepIndex > 0) {
      setCurrentStep(STEPS[currentStepIndex - 1].id);
    }
  }, [currentStepIndex]);

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
        transition={{ duration: 0.4 }}
      >
        <Link href="/">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent cursor-pointer hover:scale-105 transition-transform">
            GEMIGRAM
          </h1>
        </Link>

        <div className="flex items-center gap-4">
          <span className="text-sm text-white/60">
            Step {currentStepIndex + 1} of {STEPS.length}
          </span>
          <Link href="/">
            <button className="text-sm text-white/70 hover:text-white transition-colors">
              Cancel
            </button>
          </Link>
        </div>
      </motion.nav>

      {/* Progress Bar */}
      <motion.div
        className="relative z-30 w-full h-1 bg-white/5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <motion.div
          className="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500"
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
        />
      </motion.div>

      {/* Main Content */}
      <div className="relative z-20 flex items-center justify-center min-h-[calc(100vh-140px)] px-4 py-8">
        <div className="w-full max-w-4xl">
          {/* Step Indicators */}
          <motion.div
            className="flex justify-between mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            {STEPS.map((step, index) => (
              <motion.button
                key={step.id}
                onClick={() => index <= currentStepIndex && setCurrentStep(step.id)}
                className="flex flex-col items-center gap-2 flex-1"
                whileHover={{ scale: 1.05 }}
              >
                <motion.div
                  className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                    index <= currentStepIndex
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg shadow-cyan-500/50'
                      : 'bg-white/10 text-white/50 border border-white/20'
                  }`}
                  animate={{
                    scale: index === currentStepIndex ? 1.1 : 1,
                    boxShadow:
                      index === currentStepIndex
                        ? '0 0 20px rgba(0, 243, 255, 0.5)'
                        : 'none',
                  }}
                >
                  {index + 1}
                </motion.div>
                <div className="text-center">
                  <p className="text-xs font-medium text-white">{step.label}</p>
                  <p className="text-xs text-white/40">{step.description}</p>
                </div>
              </motion.button>
            ))}
          </motion.div>

          {/* Step Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4 }}
              className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 mb-8"
            >
              {currentStep === 'identity' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Agent Identity
                    </h2>
                    <p className="text-white/60">
                      Give your agent a name and define its core role.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-white/80 mb-2">
                        Agent Name
                      </label>
                      <input
                        type="text"
                        value={agentName}
                        onChange={(e) => setAgentName(e.target.value)}
                        placeholder="e.g., Nova, Atlas, Orion..."
                        className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:border-cyan-500 focus:outline-none transition-colors"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-white/80 mb-2">
                        Agent Role
                      </label>
                      <input
                        type="text"
                        value={agentRole}
                        onChange={(e) => setAgentRole(e.target.value)}
                        placeholder="e.g., AI Companion, Creative Guide, Code Expert..."
                        className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:border-cyan-500 focus:outline-none transition-colors"
                      />
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 'brain' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Brain Configuration
                    </h2>
                    <p className="text-white/60">
                      Select skills and expertise for your agent.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    {[
                      'Coding',
                      'Debugging',
                      'Architecture',
                      'DevOps',
                      'Learning',
                      'Creative',
                    ].map((skill) => (
                      <motion.button
                        key={skill}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-4 py-2 rounded-lg border border-white/20 text-white/70 hover:border-cyan-500 hover:text-cyan-400 transition-colors text-sm"
                      >
                        {skill}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}

              {currentStep === 'voice' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Voice Configuration
                    </h2>
                    <p className="text-white/60">
                      Customize how your agent communicates.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-white/80 mb-3">
                        Voice Tone
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        {['Professional', 'Casual', 'Friendly', 'Mentor'].map(
                          (tone) => (
                            <button
                              key={tone}
                              className="px-4 py-2 rounded-lg border border-white/20 text-white/70 hover:border-purple-500 hover:text-purple-400 transition-colors text-sm"
                            >
                              {tone}
                            </button>
                          )
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 'review' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Review Configuration
                    </h2>
                    <p className="text-white/60">
                      Verify your agent settings before deployment.
                    </p>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/10">
                      <span className="text-white/60">Agent Name:</span>
                      <span className="text-white font-mono">{agentName}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/10">
                      <span className="text-white/60">Role:</span>
                      <span className="text-white font-mono">{agentRole}</span>
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 'deploy' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Deploy Agent
                    </h2>
                    <p className="text-white/60">
                      Your agent is ready to be deployed to the Gemigram network.
                    </p>
                  </div>

                  <motion.div
                    className="p-4 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30"
                    animate={{
                      boxShadow: [
                        '0 0 20px rgba(0, 243, 255, 0.2)',
                        '0 0 40px rgba(188, 19, 254, 0.3)',
                        '0 0 20px rgba(0, 243, 255, 0.2)',
                      ],
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    <p className="text-white/80 text-sm">
                      Agent DNA: <span className="font-mono text-cyan-400">GENESIS-{Date.now().toString().slice(-6)}</span>
                    </p>
                    <p className="text-white/60 text-xs mt-2">
                      Your agent will be deployed immediately upon confirmation.
                    </p>
                  </motion.div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex justify-between gap-4">
            <motion.button
              onClick={handlePrev}
              disabled={currentStepIndex === 0}
              whileHover={{ scale: currentStepIndex > 0 ? 1.05 : 1 }}
              whileTap={{ scale: currentStepIndex > 0 ? 0.95 : 1 }}
              className="px-6 py-3 rounded-lg border border-white/20 text-white/70 hover:text-white hover:border-white/40 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Back
            </motion.button>

            <motion.button
              onClick={handleNext}
              disabled={currentStepIndex === STEPS.length - 1}
              whileHover={{ scale: currentStepIndex < STEPS.length - 1 ? 1.05 : 1 }}
              whileTap={{ scale: currentStepIndex < STEPS.length - 1 ? 0.95 : 1 }}
              className="flex-1 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {currentStepIndex === STEPS.length - 1 ? 'Deploy Agent' : 'Next'}
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  );
}
