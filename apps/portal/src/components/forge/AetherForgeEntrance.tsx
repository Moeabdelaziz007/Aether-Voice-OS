'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useRef, useCallback } from 'react';
import { useAetherGateway } from '@/hooks/useAetherGateway';
import { useAetherStore } from '@/store/useAetherStore';

interface AetherForgeEntranceProps {
  onIntentCaptured?: (intent: string) => void;
  onForgeComplete?: () => void;
}

export default function AetherForgeEntrance({
  onIntentCaptured,
  onForgeComplete,
}: AetherForgeEntranceProps) {
  const [forgeState, setForgeState] = useState<
    'idle' | 'listening' | 'analyzing' | 'creating' | 'complete'
  >('idle');
  const [orbPulse, setOrbPulse] = useState(0);
  const [transcriptText, setTranscriptText] = useState('');
  const [statusTag, setStatusTag] = useState('AWAITING VOICE INPUT');

  const gateway = useAetherGateway();
  const store = useAetherStore();
  const micActiveRef = useRef(false);
  const orbAnimationRef = useRef<NodeJS.Timeout | null>(null);

  // Voice activity effect on orb
  useEffect(() => {
    gateway.onAudioResponse.current = (audioData) => {
      // Visual feedback: increase pulse on audio activity
      const dataView = new Uint8Array(audioData);
      const rms = Math.sqrt(
        dataView.reduce((acc, val) => acc + val * val, 0) / dataView.length
      );
      setOrbPulse(Math.min(rms / 50, 1));
    };
  }, [gateway]);

  // Transcript callback - update status in real-time
  useEffect(() => {
    gateway.onTranscript.current = (text, role) => {
      if (role === 'user') {
        setTranscriptText(text);
        setStatusTag('ANALYZING INTENT...');
        if (onIntentCaptured) {
          onIntentCaptured(text);
        }
      }
    };
  }, [gateway, onIntentCaptured]);

  // Simulate DNA extraction phases
  const startDNAExtraction = useCallback(() => {
    setForgeState('listening');
    setStatusTag('DNA EXTRACTION ACTIVE');

    // Simulate listening phase with visual effects
    orbAnimationRef.current = setInterval(() => {
      setOrbPulse((p) => Math.sin(Date.now() / 300) * 0.5 + 0.5);
    }, 50);

    // Auto-transition to analyzing after 3 seconds
    setTimeout(() => {
      if (transcriptText) {
        setForgeState('analyzing');
        setStatusTag('PERSONA SYNTHESIS...');
      }
    }, 3000);

    // Auto-transition to creating
    setTimeout(() => {
      setForgeState('creating');
      setStatusTag('FORGING AGENT DNA');
      if (orbAnimationRef.current) {
        clearInterval(orbAnimationRef.current);
      }
    }, 6000);

    // Complete
    setTimeout(() => {
      setForgeState('complete');
      setStatusTag('FORGE COMPLETE');
      if (onForgeComplete) {
        onForgeComplete();
      }
    }, 9000);
  }, [transcriptText, onForgeComplete]);

  // Toggle microphone
  const toggleMicrophone = useCallback(() => {
    if (!micActiveRef.current) {
      gateway.toggleAudio();
      micActiveRef.current = true;
      startDNAExtraction();
    } else {
      gateway.toggleAudio();
      micActiveRef.current = false;
      if (orbAnimationRef.current) {
        clearInterval(orbAnimationRef.current);
      }
    }
  }, [gateway, startDNAExtraction]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (orbAnimationRef.current) {
        clearInterval(orbAnimationRef.current);
      }
    };
  }, []);

  const getNeuralOrbGradient = () => {
    // Gradient responds to pulse and forge state
    const hue = 200 + orbPulse * 60;
    return `conic-gradient(from 0deg, hsl(${hue}, 100%, 50%), hsl(${hue + 120}, 80%, 45%), hsl(${hue - 120}, 90%, 55%), hsl(${hue}, 100%, 50%))`;
  };

  return (
    <div className="relative w-full min-h-screen bg-black overflow-hidden flex flex-col items-center justify-center">
      {/* Ambient particle background */}
      <div className="absolute inset-0 opacity-30">
        <div
          className="absolute inset-0 bg-gradient-to-br from-cyan-900/20 via-black to-purple-900/20"
          style={{
            animation: 'drift 20s linear infinite',
          }}
        />
      </div>

      {/* Neural Orb - Central Focus */}
      <motion.div
        className="relative z-10 mb-12"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1.5, ease: 'easeOut' }}
      >
        {/* Outer glow rings */}
        <div className="absolute inset-0 w-96 h-96 -m-24">
          <motion.div
            className="absolute inset-0 rounded-full border border-cyan-500/30 blur-xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <motion.div
            className="absolute inset-4 rounded-full border border-purple-500/20 blur-lg"
            animate={{
              scale: [1, 1.15, 1],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.5,
            }}
          />
        </div>

        {/* Main Neural Orb */}
        <motion.div
          className="relative w-96 h-96 rounded-full shadow-2xl overflow-hidden"
          style={{
            background: getNeuralOrbGradient(),
            boxShadow: `
              0 0 40px rgba(0, 255, 200, ${0.3 + orbPulse * 0.4}),
              0 0 80px rgba(168, 85, 247, ${0.2 + orbPulse * 0.3}),
              0 0 120px rgba(0, 200, 255, ${0.1 + orbPulse * 0.2})
            `,
          }}
          animate={{
            scale: 1 + orbPulse * 0.1,
          }}
        >
          {/* Inner neural filaments */}
          <motion.div
            className="absolute inset-0 opacity-80"
            animate={{
              rotateZ: 360,
            }}
            transition={{
              duration: 15,
              repeat: Infinity,
              ease: 'linear',
            }}
          >
            <svg
              className="w-full h-full"
              viewBox="0 0 200 200"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="white"
                strokeWidth="0.5"
                opacity="0.3"
              />
              {[...Array(8)].map((_, i) => (
                <line
                  key={i}
                  x1="100"
                  y1="20"
                  x2="100"
                  y2="180"
                  stroke="white"
                  strokeWidth="0.3"
                  opacity="0.4"
                  transform={`rotate(${i * 45} 100 100)`}
                />
              ))}
            </svg>
          </motion.div>

          {/* Center bright core */}
          <div className="absolute inset-1/3 rounded-full bg-white/60 blur-lg" />
        </motion.div>

        {/* Pulsing ring indicator (microphone state) */}
        {forgeState !== 'idle' && (
          <motion.div
            className="absolute inset-0 rounded-full border-2"
            style={{
              borderColor: micActiveRef.current ? '#00ffc8' : '#a855f7',
            }}
            animate={{
              scale: [0.8, 1.2],
              opacity: [1, 0.3],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}
      </motion.div>

      {/* Status Information */}
      <div className="relative z-20 mt-8 text-center">
        {/* Status Tag */}
        <motion.div
          className="inline-block px-6 py-3 rounded-full border border-cyan-500/50 bg-cyan-500/5 backdrop-blur-sm mb-6"
          key={statusTag}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.3 }}
        >
          <p className="text-sm font-mono text-cyan-300 tracking-widest">
            {statusTag}
          </p>
        </motion.div>

        {/* Transcript Pulse - ephemeral, fades quickly */}
        <AnimatePresence>
          {transcriptText && (
            <motion.div
              className="max-w-xl mx-auto px-6 py-4 rounded-lg border border-purple-500/30 bg-purple-500/5 backdrop-blur-sm mb-8"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.4 }}
            >
              <p className="text-sm text-gray-300 italic leading-relaxed">
                "{transcriptText}"
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Microphone Control - Floating Action */}
      <motion.button
        onClick={toggleMicrophone}
        className={`relative z-30 mt-12 w-20 h-20 rounded-full flex items-center justify-center backdrop-blur-sm border-2 transition-all ${
          micActiveRef.current
            ? 'bg-red-500/20 border-red-500/50 shadow-lg shadow-red-500/30'
            : 'bg-cyan-500/20 border-cyan-500/50 shadow-lg shadow-cyan-500/30'
        }`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        {/* Microphone icon SVG */}
        <svg
          className={`w-8 h-8 ${micActiveRef.current ? 'text-red-400' : 'text-cyan-400'}`}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
          <path d="M17 16.91c-1.48 1.46-3.51 2.36-5.71 2.56v4.09h-2v-4.09C6.51 19.27 4.48 18.37 3 16.91l1.41-1.41c1.26 1.27 3.02 2.05 4.96 2.05 1.93 0 3.7-.78 4.96-2.05L17 16.91z" />
        </svg>

        {/* Recording indicator */}
        {micActiveRef.current && (
          <motion.div
            className="absolute inset-0 rounded-full border border-red-500"
            animate={{ scale: [1, 1.3], opacity: [1, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </motion.button>

      {/* Help text */}
      <motion.p
        className="relative z-30 mt-8 text-xs text-gray-500 text-center max-w-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        {forgeState === 'idle'
          ? 'Click the microphone or speak to begin crafting your agent'
          : `Status: ${forgeState.toUpperCase()}`}
      </motion.p>

      <style>{`
        @keyframes drift {
          0%, 100% { transform: translateX(0) translateY(0); }
          25% { transform: translateX(10px) translateY(-10px); }
          50% { transform: translateX(0) translateY(10px); }
          75% { transform: translateX(-10px) translateY(-10px); }
        }
      `}</style>
    </div>
  );
}
