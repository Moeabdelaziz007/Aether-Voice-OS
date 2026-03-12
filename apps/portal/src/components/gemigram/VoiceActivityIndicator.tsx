'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface VoiceActivityIndicatorProps {
  isListening: boolean;
  isProcessing: boolean;
  transcript?: string;
}

/**
 * Real-time voice activity indicator with waveform animation
 * Accessible with ARIA live regions for screen readers
 */
export default function VoiceActivityIndicator({
  isListening,
  isProcessing,
  transcript,
}: VoiceActivityIndicatorProps) {
  return (
    <div
      className="flex items-center gap-3 px-4 py-2 rounded-lg bg-black/60 border border-cyan-500/20"
      role="status"
      aria-live="polite"
      aria-label={`Voice status: ${isListening ? 'listening' : 'idle'}`}
    >
      {/* Animated pulse indicator */}
      {isListening && (
        <motion.div
          className="flex items-center gap-1"
          aria-hidden="true"
        >
          {[0, 1, 2, 3, 4].map((i) => (
            <motion.div
              key={i}
              className="w-1 h-4 bg-gradient-to-t from-cyan-500 to-cyan-400 rounded-full"
              animate={{
                height: ['4px', '16px', '4px'],
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 0.6,
                delay: i * 0.1,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          ))}
        </motion.div>
      )}

      {/* Processing spinner */}
      {isProcessing && !isListening && (
        <motion.div
          className="w-4 h-4 rounded-full border-2 border-purple-500/50 border-t-purple-500"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          aria-hidden="true"
        />
      )}

      {/* Status text */}
      <span className="text-xs font-semibold text-gray-300">
        {isListening ? 'Listening' : isProcessing ? 'Processing' : 'Ready'}
      </span>

      {/* Transcript preview (accessible) */}
      {transcript && (
        <span className="text-xs text-gray-400 ml-2 max-w-[200px] truncate" aria-label={`You said: ${transcript}`}>
          "{transcript}"
        </span>
      )}
    </div>
  );
}
