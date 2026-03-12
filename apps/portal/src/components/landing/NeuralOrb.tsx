'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface NeuralOrbProps {
  isHovering?: boolean;
}

export default function NeuralOrb({ isHovering = false }: NeuralOrbProps) {
  return (
    <motion.div
      className="relative w-64 h-64 flex items-center justify-center"
      animate={{
        scale: isHovering ? 1.1 : 1,
      }}
      transition={{ duration: 0.4 }}
    >
      {/* Outer rotating rings */}
      <motion.svg
        className="absolute w-full h-full"
        viewBox="0 0 256 256"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      >
        <circle
          cx="128"
          cy="128"
          r="120"
          fill="none"
          stroke="url(#gradient1)"
          strokeWidth="1"
          opacity="0.3"
        />
        <defs>
          <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00F3FF" />
            <stop offset="50%" stopColor="#BC13FE" />
            <stop offset="100%" stopColor="#FF1CF7" />
          </linearGradient>
        </defs>
      </motion.svg>

      {/* Rotating orbital lines */}
      <motion.svg
        className="absolute w-full h-full"
        viewBox="0 0 256 256"
        animate={{ rotate: -360 }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      >
        <ellipse
          cx="128"
          cy="128"
          rx="100"
          ry="50"
          fill="none"
          stroke="url(#gradient2)"
          strokeWidth="0.5"
          opacity="0.2"
        />
        <defs>
          <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00F3FF" />
            <stop offset="100%" stopColor="#BC13FE" />
          </linearGradient>
        </defs>
      </motion.svg>

      {/* Core glow effect */}
      <motion.div
        className="absolute w-48 h-48 rounded-full opacity-30"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{
          background: 'radial-gradient(circle, #00F3FF 0%, #BC13FE 40%, transparent 70%)',
          filter: 'blur(20px)',
        }}
      />

      {/* Inner glowing sphere */}
      <motion.div
        className="absolute w-32 h-32 rounded-full"
        animate={{
          scale: [1, 1.1, 1],
          boxShadow: [
            '0 0 20px rgba(0, 243, 255, 0.3), inset 0 0 20px rgba(188, 19, 254, 0.2)',
            '0 0 40px rgba(0, 243, 255, 0.6), inset 0 0 30px rgba(188, 19, 254, 0.4)',
            '0 0 20px rgba(0, 243, 255, 0.3), inset 0 0 20px rgba(188, 19, 254, 0.2)',
          ],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{
          background: 'radial-gradient(circle at 30% 30%, rgba(0, 243, 255, 0.4), rgba(188, 19, 254, 0.2), transparent)',
          border: '2px solid rgba(0, 243, 255, 0.2)',
        }}
      />

      {/* Center bright core */}
      <motion.div
        className="absolute w-16 h-16 rounded-full"
        animate={{
          opacity: [0.6, 1, 0.6],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{
          background: 'radial-gradient(circle, #00F3FF 0%, #BC13FE 100%)',
          boxShadow: '0 0 30px rgba(0, 243, 255, 0.8), 0 0 60px rgba(188, 19, 254, 0.4)',
          filter: 'blur(0.5px)',
        }}
      />

      {/* Floating particles */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-cyan-400"
          animate={{
            x: [0, Math.cos((i / 8) * Math.PI * 2) * 80],
            y: [0, Math.sin((i / 8) * Math.PI * 2) * 80],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 3 + i * 0.2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{
            filter: 'blur(0.5px)',
          }}
        />
      ))}
    </motion.div>
  );
}
