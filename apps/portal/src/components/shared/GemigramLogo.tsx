'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface GemigramLogoProps {
    size?: 'sm' | 'md' | 'lg';
    includeSubtext?: boolean;
    className?: string;
}

export default function GemigramLogo({
    size = 'md',
    includeSubtext = false,
    className = ""
}: GemigramLogoProps) {
    const iconSize = {
        sm: 'w-6 h-6',
        md: 'w-9 h-9',
        lg: 'w-14 h-14'
    }[size];

    const textSize = {
        sm: 'text-sm tracking-[0.2em]',
        md: 'text-xl tracking-[0.3em]',
        lg: 'text-3xl tracking-[0.4em]'
    }[size];

    return (
        <div className={`flex flex-col items-center ${className}`}>
            <div className="flex items-center gap-3">
                {/* Futuristic Hexagonal 'G' Icon */}
                <motion.div
                    whileHover={{ scale: 1.1, rotate: 10 }}
                    className={`${iconSize} relative flex items-center justify-center`}
                >
                    <div className="absolute inset-0 bg-cyan-500/20 blur-md rounded-lg animate-pulse" />
                    <svg
                        viewBox="0 0 100 100"
                        className="w-full h-full drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]"
                    >
                        {/* Hexagonal Outer Frame */}
                        <path
                            d="M50 5 L90 27.5 V72.5 L50 95 L10 72.5 V27.5 Z"
                            fill="none"
                            stroke="white"
                            strokeWidth="4"
                            className="opacity-20"
                        />
                        {/* Stylized 'G' Inner Path */}
                        <path
                            d="M75 35 C70 25 60 20 50 20 C35 20 25 30 25 50 C25 70 35 80 50 80 C65 80 75 70 75 55 H50"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="8"
                            strokeLinecap="round"
                            className="text-cyan-400"
                        />
                        {/* Core Neural Pulse */}
                        <circle cx="50" cy="50" r="5" className="fill-white animate-pulse" />
                    </svg>
                </motion.div>

                {/* Gemigram Typography */}
                <h1 className={`${textSize} font-black text-white italic uppercase select-none`}>
                    Gemi<span className="text-cyan-400">gram</span>
                </h1>
            </div>

            {includeSubtext && (
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="mt-1 text-[8px] md:text-[10px] uppercase font-bold tracking-[0.4em] text-white/30 whitespace-nowrap"
                >
                    Voice-First AI agent platform
                </motion.p>
            )}
        </div>
    );
}
