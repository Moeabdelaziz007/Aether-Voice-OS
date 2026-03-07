'use client';

/**
 * Acoustic Signal Intelligence UI — Audio Visualization System
 * 
 * Real-time indicators for voice activity detection, audio levels, and signal quality.
 * Features:
 * - VAD (Voice Activity Detection) indicator
 * - Audio waveform visualization
 * - Signal-to-noise ratio display
 * - Echo cancellation status
 * - Multi-channel audio monitoring
 */

import React, { useEffect, useRef, useState } from 'react';
import clsx from 'clsx';

interface AcousticSignalIndicatorProps {
    className?: string;
    audioLevel?: number; // 0-1
    isSpeaking?: boolean;
    vadConfidence?: number; // 0-1
    snr?: number; // Signal-to-noise ratio in dB
    echoCancelled?: boolean;
    channels?: Array<{ name: string; level: number }>;
}

export function AcousticSignalIndicator({
    className,
    audioLevel = 0,
    isSpeaking = false,
    vadConfidence = 0,
    snr = 0,
    echoCancelled = false,
    channels = [],
}: AcousticSignalIndicatorProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number>(0);

    // Animate waveform
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let phase = 0;

        const animate = () => {
            const width = canvas.width;
            const height = canvas.height;

            ctx.clearRect(0, 0, width, height);

            // Draw waveform
            ctx.beginPath();
            ctx.moveTo(0, height / 2);

            for (let x = 0; x < width; x++) {
                const normalizedX = x / width;
                const amplitude = audioLevel * (height / 2 - 4);
                const frequency = 0.05;
                const y = height / 2 + Math.sin(phase + normalizedX * frequency * Math.PI * 2) * amplitude;
                ctx.lineTo(x, y);
            }

            // Gradient stroke
            const gradient = ctx.createLinearGradient(0, 0, width, 0);
            gradient.addColorStop(0, 'rgba(6, 182, 212, 0.8)'); // Cyan
            gradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.8)'); // Blue
            gradient.addColorStop(1, 'rgba(168, 85, 247, 0.8)'); // Purple

            ctx.strokeStyle = gradient;
            ctx.lineWidth = 2;
            ctx.stroke();

            phase += 0.2;
            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(animationRef.current);
        };
    }, [audioLevel]);

    // Determine VAD state color
    const getVadColor = () => {
        if (vadConfidence > 0.7) return 'text-green-400 bg-green-500/20 border-green-500/30';
        if (vadConfidence > 0.4) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    };

    // Determine SNR quality
    const getSNRQuality = () => {
        if (snr > 20) return { label: 'Excellent', color: 'text-green-400' };
        if (snr > 10) return { label: 'Good', color: 'text-blue-400' };
        if (snr > 5) return { label: 'Fair', color: 'text-yellow-400' };
        return { label: 'Poor', color: 'text-red-400' };
    };

    const snrQuality = getSNRQuality();

    return (
        <div className={clsx('acoustic-signal-indicator ultra-glass rounded-xl p-4 border border-white/10', className)}>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    <span className="text-white/90 text-sm font-medium">Acoustic Signal Intelligence</span>
                </div>
                
                {/* Speaking Indicator */}
                <div className={clsx(
                    'speaking-badge px-2 py-1 rounded text-xs font-medium transition-all',
                    isSpeaking ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-gray-500/20 text-gray-400'
                )}>
                    {isSpeaking ? '🎤 Speaking' : '🔇 Silent'}
                </div>
            </div>

            {/* Waveform Display */}
            <div className="waveform-container mb-4 rounded-lg overflow-hidden bg-black/50 border border-white/10">
                <canvas
                    ref={canvasRef}
                    width={400}
                    height={80}
                    className="w-full h-20"
                />
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                {/* Audio Level */}
                <div className="metric-card p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="text-white/50 text-xs mb-1">Audio Level</div>
                    <div className="text-white/90 font-mono text-lg">{Math.round(audioLevel * 100)}%</div>
                    <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-100"
                            style={{ width: `${audioLevel * 100}%` }}
                        />
                    </div>
                </div>

                {/* VAD Confidence */}
                <div className={clsx('metric-card p-3 rounded-lg border transition-all', getVadColor())}>
                    <div className="text-white/70 text-xs mb-1">VAD Confidence</div>
                    <div className="font-mono text-lg">{Math.round(vadConfidence * 100)}%</div>
                    <div className="mt-2 flex items-center gap-1 text-xs">
                        <div className={clsx('w-1.5 h-1.5 rounded-full', vadConfidence > 0.5 ? 'bg-current animate-pulse' : 'bg-gray-500')} />
                        <span>{vadConfidence > 0.5 ? 'Voice Detected' : 'No Voice'}</span>
                    </div>
                </div>

                {/* SNR */}
                <div className="metric-card p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="text-white/50 text-xs mb-1">Signal-to-Noise</div>
                    <div className={clsx('font-mono text-lg', snrQuality.color)}>{snr.toFixed(1)} dB</div>
                    <div className={clsx('text-xs mt-2', snrQuality.color)}>{snrQuality.label}</div>
                </div>

                {/* Echo Cancellation */}
                <div className={clsx(
                    'metric-card p-3 rounded-lg border transition-all',
                    echoCancelled ? 'bg-green-500/20 border-green-500/30' : 'bg-gray-500/20 border-gray-500/30'
                )}>
                    <div className="text-white/70 text-xs mb-1">AEC Status</div>
                    <div className={clsx('font-mono text-sm', echoCancelled ? 'text-green-400' : 'text-gray-400')}>
                        {echoCancelled ? 'Active' : 'Inactive'}
                    </div>
                    <div className="mt-2 flex items-center gap-1 text-xs">
                        <div className={clsx('w-1.5 h-1.5 rounded-full', echoCancelled ? 'bg-green-400 animate-pulse' : 'bg-gray-500')} />
                        <span>{echoCancelled ? 'Echo Cancelled' : 'No AEC'}</span>
                    </div>
                </div>
            </div>

            {/* Multi-Channel Monitor */}
            {channels.length > 0 && (
                <div className="channels-section">
                    <div className="text-white/50 text-xs mb-2">Channel Levels</div>
                    <div className="grid gap-2">
                        {channels.map((channel) => (
                            <div key={channel.name} className="channel-row flex items-center gap-3">
                                <div className="text-white/70 text-xs w-16">{channel.name}</div>
                                <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-100"
                                        style={{ width: `${channel.level * 100}%` }}
                                    />
                                </div>
                                <div className="text-white/50 text-xs font-mono w-12 text-right">
                                    {Math.round(channel.level * 100)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

/**
 * Compact Voice Activity Indicator — Simplified version
 */
export function VoiceActivityBadge({ isSpeaking, confidence = 0 }: { isSpeaking: boolean; confidence?: number }) {
    return (
        <div className={clsx(
            'voice-activity-badge inline-flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all',
            isSpeaking 
                ? 'bg-cyan-500/20 border-cyan-500/30 text-cyan-400' 
                : 'bg-gray-500/20 border-gray-500/30 text-gray-400'
        )}>
            <div className={clsx(
                'w-2 h-2 rounded-full',
                isSpeaking ? 'bg-cyan-400 animate-pulse' : 'bg-gray-500'
            )} />
            <span className="text-xs font-medium">
                {isSpeaking ? `Voice Active (${Math.round(confidence * 100)}%)` : 'No Voice'}
            </span>
        </div>
    );
}

export default AcousticSignalIndicator;
