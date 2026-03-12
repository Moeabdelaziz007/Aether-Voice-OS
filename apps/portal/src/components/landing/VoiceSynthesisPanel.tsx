'use client';

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';

interface VoiceSynthesisPanelState {
  tone: number;
  resonance: number;
  style: number;
  pitch: number;
  isPlaying: boolean;
}

export default function VoiceSynthesisPanel() {
  const [state, setState] = useState<VoiceSynthesisPanelState>({
    tone: 50,
    resonance: 50,
    style: 50,
    pitch: 50,
    isPlaying: false,
  });

  const handleSliderChange = useCallback(
    (key: keyof Omit<VoiceSynthesisPanelState, 'isPlaying'>) =>
      (e: React.ChangeEvent<HTMLInputElement>) => {
        setState((prev) => ({
          ...prev,
          [key]: Number(e.target.value),
        }));
      },
    []
  );

  const handlePlayClick = useCallback(() => {
    setState((prev) => ({
      ...prev,
      isPlaying: !prev.isPlaying,
    }));

    // Reset after animation
    if (!state.isPlaying) {
      setTimeout(() => {
        setState((prev) => ({
          ...prev,
          isPlaying: false,
        }));
      }, 3000);
    }
  }, [state.isPlaying]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10 overflow-hidden"
    >
      {/* Background glow */}
      <motion.div
        className="absolute inset-0 opacity-0"
        animate={{
          boxShadow: [
            'inset 0 0 20px rgba(188, 19, 254, 0.1)',
            'inset 0 0 40px rgba(188, 19, 254, 0.2)',
            'inset 0 0 20px rgba(188, 19, 254, 0.1)',
          ],
        }}
        transition={{ duration: 3, repeat: Infinity }}
      />

      {/* Waveform Visualization */}
      <motion.div className="relative h-32 mb-8 flex items-center justify-center bg-black/20 rounded-lg overflow-hidden border border-white/5">
        {/* SVG Waveform */}
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 400 100"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#BC13FE" />
              <stop offset="50%" stopColor="#00F3FF" />
              <stop offset="100%" stopColor="#BC13FE" />
            </linearGradient>
          </defs>

          {/* Animated waveform path */}
          <motion.path
            d="M 0 50 Q 25 30 50 50 T 100 50 T 150 50 T 200 50 T 250 50 T 300 50 T 350 50 T 400 50"
            fill="none"
            stroke="url(#waveGradient)"
            strokeWidth="2"
            strokeLinecap="round"
            animate={{
              d: [
                'M 0 50 Q 25 30 50 50 T 100 50 T 150 50 T 200 50 T 250 50 T 300 50 T 350 50 T 400 50',
                `M 0 50 Q 25 ${30 + state.tone * 0.3} 50 50 T 100 50 T 150 50 T 200 50 T 250 50 T 300 50 T 350 50 T 400 50`,
                'M 0 50 Q 25 30 50 50 T 100 50 T 150 50 T 200 50 T 250 50 T 300 50 T 350 50 T 400 50',
              ],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />

          {/* Additional waveform layers */}
          <motion.path
            d="M 0 50 Q 15 35 30 50 T 60 50 T 90 50 T 120 50 T 150 50 T 180 50 T 210 50 T 240 50"
            fill="none"
            stroke="rgba(0, 243, 255, 0.4)"
            strokeWidth="1"
            opacity={0.5}
            animate={{
              d: [
                'M 0 50 Q 15 35 30 50 T 60 50 T 90 50 T 120 50 T 150 50 T 180 50 T 210 50 T 240 50',
                `M 0 50 Q 15 ${35 + state.resonance * 0.2} 30 50 T 60 50 T 90 50 T 120 50 T 150 50 T 180 50 T 210 50 T 240 50`,
                'M 0 50 Q 15 35 30 50 T 60 50 T 90 50 T 120 50 T 150 50 T 180 50 T 210 50 T 240 50',
              ],
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </svg>

        {/* Glow effect on waveform */}
        <motion.div
          className="absolute inset-0 opacity-0"
          animate={{
            opacity: state.isPlaying ? [0.3, 0.6, 0.3] : 0,
          }}
          transition={{ duration: 1, repeat: Infinity }}
          style={{
            background: 'radial-gradient(ellipse at center, rgba(0, 243, 255, 0.3), transparent)',
            filter: 'blur(8px)',
          }}
        />
      </motion.div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-6 mb-6 relative z-10">
        {/* Tone Control */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-medium text-white/70 uppercase tracking-wider">
              Tone
            </label>
            <motion.span
              className="text-xs font-mono text-cyan-400"
              key={state.tone}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 0.2 }}
            >
              {Math.round(state.tone)}
            </motion.span>
          </div>
          <motion.input
            type="range"
            min="0"
            max="100"
            value={state.tone}
            onChange={handleSliderChange('tone')}
            className="w-full h-1.5 rounded-full bg-gradient-to-r from-purple-900 to-purple-700 appearance-none cursor-pointer accent-purple-400"
            style={{
              accentColor: '#BC13FE',
            }}
          />
        </div>

        {/* Resonance Control */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-medium text-white/70 uppercase tracking-wider">
              Resonance
            </label>
            <motion.span
              className="text-xs font-mono text-cyan-400"
              key={state.resonance}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 0.2 }}
            >
              {Math.round(state.resonance)}
            </motion.span>
          </div>
          <motion.input
            type="range"
            min="0"
            max="100"
            value={state.resonance}
            onChange={handleSliderChange('resonance')}
            className="w-full h-1.5 rounded-full bg-gradient-to-r from-cyan-900 to-cyan-700 appearance-none cursor-pointer"
            style={{
              accentColor: '#00F3FF',
            }}
          />
        </div>

        {/* Style Control */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-medium text-white/70 uppercase tracking-wider">
              Style
            </label>
            <motion.span
              className="text-xs font-mono text-purple-400"
              key={state.style}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 0.2 }}
            >
              {Math.round(state.style)}
            </motion.span>
          </div>
          <motion.input
            type="range"
            min="0"
            max="100"
            value={state.style}
            onChange={handleSliderChange('style')}
            className="w-full h-1.5 rounded-full bg-gradient-to-r from-purple-900 to-pink-700 appearance-none cursor-pointer"
            style={{
              accentColor: '#FF1CF7',
            }}
          />
        </div>

        {/* Pitch Control */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-medium text-white/70 uppercase tracking-wider">
              Pitch
            </label>
            <motion.span
              className="text-xs font-mono text-cyan-400"
              key={state.pitch}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 0.2 }}
            >
              {Math.round(state.pitch)}
            </motion.span>
          </div>
          <motion.input
            type="range"
            min="0"
            max="100"
            value={state.pitch}
            onChange={handleSliderChange('pitch')}
            className="w-full h-1.5 rounded-full bg-gradient-to-r from-cyan-900 to-emerald-700 appearance-none cursor-pointer"
            style={{
              accentColor: '#10B981',
            }}
          />
        </div>
      </div>

      {/* Output Display and Play Button */}
      <div className="flex items-center gap-4 pt-4 border-t border-white/5 relative z-10">
        {/* Processing text */}
        <div className="flex-1">
          <motion.p
            className="text-xs text-white/50 font-mono"
            animate={{
              opacity: state.isPlaying ? [0.5, 1, 0.5] : 0.5,
            }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {state.isPlaying
              ? 'Processing Voice. Hyper-realistic Output...'
              : 'Ready for synthesis...'}
          </motion.p>

          {/* Animated dots */}
          {state.isPlaying && (
            <motion.div className="flex gap-1 mt-2">
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  className="w-1 h-1 rounded-full bg-cyan-400"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    delay: i * 0.2,
                  }}
                />
              ))}
            </motion.div>
          )}
        </div>

        {/* Play button */}
        <motion.button
          onClick={handlePlayClick}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-cyan-600 flex items-center justify-center flex-shrink-0 hover:shadow-lg transition-shadow"
          style={{
            boxShadow: state.isPlaying
              ? '0 0 20px rgba(0, 243, 255, 0.6)'
              : 'none',
          }}
        >
          {state.isPlaying ? (
            <motion.div
              className="w-5 h-5 flex items-center justify-center"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity }}
            >
              <div className="w-1.5 h-1.5 rounded-full bg-white mx-0.5" />
              <div className="w-1.5 h-1.5 rounded-full bg-white mx-0.5" />
            </motion.div>
          ) : (
            <svg
              className="w-5 h-5 text-white ml-0.5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </motion.button>
      </div>
    </motion.div>
  );
}
