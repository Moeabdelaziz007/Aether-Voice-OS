'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useRef, useCallback } from 'react';
import { useAetherGateway } from '@/hooks/useAetherGateway';

interface TranscriptPulse {
  id: string;
  text: string;
  role: 'user' | 'agent';
  timestamp: number;
}

interface CommunicationSanctumProps {
  agentName: string;
  agentAura?: 'cyan' | 'purple' | 'emerald' | 'amber';
  emotionalState?: 'listening' | 'thinking' | 'speaking' | 'processing';
  onVoiceInput?: (text: string) => void;
  onIntentReceived?: (intent: string) => void;
}

export default function CommunicationSanctum({
  agentName,
  agentAura = 'cyan',
  emotionalState = 'listening',
  onVoiceInput,
  onIntentReceived,
}: CommunicationSanctumProps) {
  const [transcripts, setTranscripts] = useState<TranscriptPulse[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [agentThinking, setAgentThinking] = useState(false);
  const [currentEmotionalState, setCurrentEmotionalState] =
    useState<'listening' | 'thinking' | 'speaking' | 'processing'>(emotionalState);
  const [lightningIntensity, setLightningIntensity] = useState(0);

  const gateway = useAetherGateway();
  const transcriptTimeoutRef = useRef<NodeJS.Timeout>();

  // Background color based on aura and state
  const getBackgroundGradient = () => {
    switch (agentAura) {
      case 'cyan':
        return 'from-cyan-950 via-black to-cyan-900';
      case 'purple':
        return 'from-purple-950 via-black to-purple-900';
      case 'emerald':
        return 'from-emerald-950 via-black to-emerald-900';
      case 'amber':
        return 'from-amber-950 via-black to-amber-900';
      default:
        return 'from-black via-black to-black';
    }
  };

  const getLightningColor = () => {
    switch (agentAura) {
      case 'cyan':
        return 'rgba(0, 255, 200, ';
      case 'purple':
        return 'rgba(168, 85, 247, ';
      case 'emerald':
        return 'rgba(52, 211, 153, ';
      case 'amber':
        return 'rgba(251, 146, 60, ';
      default:
        return 'rgba(255, 255, 255, ';
    }
  };

  // Transcript callback
  useEffect(() => {
    gateway.onTranscript.current = (text, role) => {
      const newTranscript: TranscriptPulse = {
        id: Date.now().toString(),
        text,
        role,
        timestamp: Date.now(),
      };

      setTranscripts((prev) => [...prev, newTranscript]);

      // Auto-fade after 4 seconds
      clearTimeout(transcriptTimeoutRef.current);
      transcriptTimeoutRef.current = setTimeout(() => {
        setTranscripts((prev) => prev.filter((t) => t.id !== newTranscript.id));
      }, 4000);

      if (role === 'user') {
        setIsListening(false);
        setCurrentEmotionalState('thinking');
        setAgentThinking(true);

        if (onVoiceInput) {
          onVoiceInput(text);
        }

        // Simulate agent thinking
        setTimeout(() => {
          setCurrentEmotionalState('speaking');
          setAgentThinking(false);
          setLightningIntensity(0.8);
        }, 1500);

        // Return to listening
        setTimeout(() => {
          setCurrentEmotionalState('listening');
          setLightningIntensity(0.2);
        }, 4500);
      }
    };
  }, [gateway, onVoiceInput]);

  // Audio activity effect
  useEffect(() => {
    gateway.onAudioResponse.current = (audioData) => {
      const dataView = new Uint8Array(audioData);
      const rms = Math.sqrt(
        dataView.reduce((acc, val) => acc + val * val, 0) / dataView.length
      );
      const normalized = Math.min(rms / 50, 1);
      setLightningIntensity(Math.max(0.2, normalized));
    };
  }, [gateway]);

  const startListening = useCallback(() => {
    gateway.toggleAudio();
    setIsListening(true);
    setCurrentEmotionalState('listening');
    setLightningIntensity(0.3);
  }, [gateway]);

  const stopListening = useCallback(() => {
    gateway.toggleAudio();
    setIsListening(false);
  }, [gateway]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (transcriptTimeoutRef.current) {
        clearTimeout(transcriptTimeoutRef.current);
      }
    };
  }, []);

  return (
    <motion.div
      className={`relative w-full min-h-screen bg-gradient-to-br ${getBackgroundGradient()} overflow-hidden flex flex-col items-center justify-center p-6`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.5 }}
    >
      {/* Reality Warp transition effect */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        initial={{ opacity: 1, backdropFilter: 'blur(20px)' }}
        animate={{ opacity: 0, backdropFilter: 'blur(0px)' }}
        transition={{ duration: 1.5, ease: 'easeInOut' }}
      />

      {/* Background lightning field */}
      <motion.div
        className="absolute inset-0 opacity-0 pointer-events-none"
        animate={{
          opacity: [0, lightningIntensity * 0.3, 0],
        }}
        transition={{
          duration: 0.1,
          repeat: Infinity,
          repeatType: 'mirror',
        }}
      >
        <svg
          className="w-full h-full"
          viewBox="0 0 1000 1000"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Lightning bolts */}
          {[...Array(3)].map((_, i) => (
            <motion.path
              key={`lightning-${i}`}
              d={`M ${200 + i * 300} 0 Q ${250 + i * 300} 250 ${300 + i * 300} 500 Q ${250 + i * 300} 750 ${200 + i * 300} 1000`}
              stroke={getLightningColor() + Math.max(0.1, lightningIntensity) + ')'}
              strokeWidth="2"
              fill="none"
              filter="url(#glow)"
              animate={{
                strokeDashoffset: [0, -100],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
                delay: i * 0.2,
              }}
            />
          ))}
        </svg>
      </motion.div>

      {/* Agent Presence - Central Avatar */}
      <motion.div
        className="relative z-20 mb-12"
        animate={{
          scale: currentEmotionalState === 'speaking' ? [1, 1.05, 1] : 1,
        }}
        transition={{
          duration: 2,
          repeat: currentEmotionalState === 'speaking' ? Infinity : 0,
        }}
      >
        {/* Aura glow rings */}
        <motion.div
          className="absolute inset-0 w-80 h-80 -m-20 rounded-full border border-white/20 blur-xl"
          animate={{
            scale: [0.9, 1.1, 0.9],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* Main presence orb */}
        <motion.div
          className="relative w-80 h-80 rounded-full flex items-center justify-center"
          animate={{
            boxShadow: [
              `0 0 40px ${getLightningColor()}${0.2 + lightningIntensity * 0.3})`,
              `0 0 80px ${getLightningColor()}${0.4 + lightningIntensity * 0.4})`,
              `0 0 40px ${getLightningColor()}${0.2 + lightningIntensity * 0.3})`,
            ],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {/* Gradient fill */}
          <div
            className={`absolute inset-0 rounded-full bg-gradient-conic from-cyan-500/20 via-white/5 to-cyan-500/20`}
          />

          {/* Emotional state indicator */}
          <div className="absolute inset-0 rounded-full border-2 border-white/30 flex items-center justify-center">
            <motion.div
              className="text-6xl"
              animate={{
                scale: [1, 1.15, 1],
              }}
              transition={{
                duration: currentEmotionalState === 'speaking' ? 0.6 : 1.5,
                repeat: Infinity,
              }}
            >
              {currentEmotionalState === 'listening' && '👂'}
              {currentEmotionalState === 'thinking' && '💭'}
              {currentEmotionalState === 'speaking' && '🗣️'}
              {currentEmotionalState === 'processing' && '⚡'}
            </motion.div>
          </div>

          {/* Status pulse ring */}
          {(currentEmotionalState === 'speaking' || isListening) && (
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-white/50"
              animate={{
                scale: [0.9, 1.2],
                opacity: [1, 0],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeOut',
              }}
            />
          )}
        </motion.div>

        {/* Agent name */}
        <motion.p
          className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-xl font-bold text-white whitespace-nowrap"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {agentName}
        </motion.p>
      </motion.div>

      {/* Transcript Pulse - Ephemeral floating */}
      <AnimatePresence>
        {transcripts.map((transcript) => (
          <motion.div
            key={transcript.id}
            className={`absolute z-30 max-w-md px-6 py-4 rounded-xl border backdrop-blur-sm ${
              transcript.role === 'user'
                ? 'border-cyan-500/50 bg-cyan-500/10'
                : 'border-purple-500/50 bg-purple-500/10'
            }`}
            initial={{
              opacity: 0,
              y: transcript.role === 'user' ? 50 : -50,
              scale: 0.8,
            }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
            }}
            exit={{
              opacity: 0,
              y: transcript.role === 'user' ? 50 : -50,
              scale: 0.8,
            }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-start gap-3">
              <span className="text-xl">
                {transcript.role === 'user' ? '👤' : '🤖'}
              </span>
              <p
                className={`text-sm leading-relaxed ${
                  transcript.role === 'user' ? 'text-cyan-200' : 'text-purple-200'
                }`}
              >
                {transcript.text}
              </p>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Voice Control Button */}
      <motion.button
        onClick={isListening ? stopListening : startListening}
        className={`relative z-40 mt-24 w-28 h-28 rounded-full flex items-center justify-center backdrop-blur-sm border-2 transition-all shadow-2xl ${
          isListening
            ? 'bg-red-500/20 border-red-500/70 shadow-red-500/40'
            : 'bg-white/10 border-white/30 hover:border-white/50'
        }`}
        animate={{
          scale: isListening ? [1, 1.05, 1] : 1,
        }}
        transition={{
          duration: 1.5,
          repeat: isListening ? Infinity : 0,
        }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <svg
          className={`w-12 h-12 ${
            isListening ? 'text-red-400' : 'text-white'
          }`}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
          <path d="M17 16.91c-1.48 1.46-3.51 2.36-5.71 2.56v4.09h-2v-4.09C6.51 19.27 4.48 18.37 3 16.91l1.41-1.41c1.26 1.27 3.02 2.05 4.96 2.05 1.93 0 3.7-.78 4.96-2.05L17 16.91z" />
        </svg>

        {/* Recording pulse */}
        {isListening && (
          <motion.div
            className="absolute inset-0 rounded-full border border-red-500"
            animate={{ scale: [1, 1.4], opacity: [1, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </motion.button>

      {/* Status information */}
      <motion.div
        className="relative z-30 mt-8 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        <p className="text-sm text-gray-400">
          {isListening
            ? '🎙️ Listening...'
            : currentEmotionalState === 'thinking'
            ? '💭 Processing your input...'
            : currentEmotionalState === 'speaking'
            ? '🗣️ Responding...'
            : 'Click to speak'}
        </p>
        <p className="text-xs text-gray-600 mt-2">
          {currentEmotionalState.toUpperCase()}
        </p>
      </motion.div>
    </motion.div>
  );
}
