'use client';

/**
 * ThoughtEcho — Text Overlay Effect
 * 
 * Creates a ghostly echo/reverb visual effect for AI thoughts and transcriptions.
 * Features:
 * - Multiple text echo layers with staggered delays
 * - Gradient fade-out trails
 * - Blur and opacity decay per layer
 * - Audio-reactive amplitude modulation
 * - Customizable echo count and spacing
 */

import React, { useEffect, useRef, useState } from 'react';
import clsx from 'clsx';

interface ThoughtEchoProps {
    text: string;
    className?: string;
    echoCount?: number;
    echoDelay?: number; // ms between echoes
    decayRate?: number; // opacity reduction per echo
    blurAmount?: number; // base blur in pixels
    audioLevel?: number; // 0-1 for reactive modulation
    variant?: 'fade' | 'blur' | 'scale' | 'glitch';
    autoFade?: boolean; // Auto-fade echoes after animation
}

export function ThoughtEcho({
    text,
    className,
    echoCount = 3,
    echoDelay = 80,
    decayRate = 0.3,
    blurAmount = 2,
    audioLevel = 0,
    variant = 'fade',
    autoFade = true,
}: ThoughtEchoProps) {
    const [isAnimating, setIsAnimating] = useState(true);
    const containerRef = useRef<HTMLDivElement>(null);
    const previousTextRef = useRef<string>('');

    // Reset animation when text changes
    useEffect(() => {
        if (text !== previousTextRef.current) {
            setIsAnimating(false);
            
            // Force reflow
            if (containerRef.current) {
                void containerRef.current.offsetWidth;
            }
            
            setIsAnimating(true);
            previousTextRef.current = text;
        }
    }, [text]);

    // Generate echo layers
    const echoes = Array.from({ length: echoCount }, (_, i) => {
        const index = i + 1;
        const opacity = Math.max(0.1, 1 - (index * decayRate));
        const blur = blurAmount + (index * 0.5);
        const delay = index * echoDelay;
        const scale = 1 + (index * 0.02);
        
        return {
            id: index,
            opacity,
            blur,
            delay,
            scale,
            xOffset: index * 2,
            yOffset: index * 1,
        };
    });

    return (
        <div 
            ref={containerRef}
            className={clsx('thought-echo-container relative inline-block', className)}
        >
            {/* Main Text (Foreground) */}
            <div className="thought-echo-main relative z-10 text-white/95">
                {text}
            </div>

            {/* Echo Layers */}
            <div className="echo-layers absolute inset-0 z-0 pointer-events-none overflow-visible">
                {echoes.map((echo) => (
                    <div
                        key={echo.id}
                        className={clsx(
                            'echo-layer absolute top-0 left-0 whitespace-nowrap',
                            `variant-${variant}`
                        )}
                        style={{
                            opacity: isAnimating ? echo.opacity : (autoFade ? 0 : echo.opacity * 0.3),
                            filter: `blur(${echo.blur}px)`,
                            transform: `translate(${echo.xOffset}px, ${echo.yOffset}px) scale(${echo.scale})`,
                            transitionDelay: `${echo.delay}ms`,
                            color: `rgba(6, 182, 212, ${echo.opacity})`, // Cyan tint
                            textShadow: `0 0 ${echo.blur * 2}px rgba(6, 182, 212, ${echo.opacity * 0.8})`,
                        }}
                    >
                        {text}
                    </div>
                ))}
            </div>

            {/* Audio-Reactive Glow Overlay */}
            {audioLevel > 0 && (
                <div 
                    className="audio-reactive-glow absolute -inset-4 rounded-full pointer-events-none"
                    style={{
                        background: `radial-gradient(circle, rgba(6, 182, 212, ${audioLevel * 0.3}) 0%, transparent 70%)`,
                        opacity: audioLevel,
                        filter: `blur(${20 - audioLevel * 10}px)`,
                    }}
                />
            )}
        </div>
    );
}

/**
 * FloatingThought — Drifting echo bubbles for ambient thoughts
 */
export function FloatingThought({
    text,
    duration = 8,
    delay = 0,
    size = 'medium',
    className,
}: {
    text: string;
    duration?: number;
    delay?: number;
    size?: 'small' | 'medium' | 'large';
    className?: string;
}) {
    const sizeClasses = {
        small: 'text-xs opacity-40',
        medium: 'text-sm opacity-60',
        large: 'text-base opacity-80',
    };

    return (
        <div
            className={clsx('floating-thought absolute', sizeClasses[size], className)}
            style={{
                animation: `float-thought ${duration}s ease-in-out ${delay}s infinite`,
                textShadow: '0 0 20px rgba(6, 182, 212, 0.6)',
                color: 'rgba(6, 182, 212, 0.7)',
            }}
        >
            {text}
        </div>
    );
}

/**
 * WhisperTrail — Cascading text particles
 */
export function WhisperTrail({
    text,
    className,
}: {
    text: string;
    className?: string;
}) {
    const words = text.split(' ');
    
    return (
        <div className={clsx('whisper-trail flex flex-wrap gap-2', className)}>
            {words.map((word, index) => (
                <span
                    key={index}
                    className="whisper-word inline-block"
                    style={{
                        animation: `whisper-float 3s ease-out ${index * 0.2}s forwards`,
                        opacity: 0,
                        color: `rgba(168, 85, 247, ${0.8 - index * 0.1})`,
                        textShadow: `0 0 ${10 + index * 2}px rgba(168, 85, 247, 0.6)`,
                    }}
                >
                    {word}
                </span>
            ))}
        </div>
    );
}

export default ThoughtEcho;
