'use client';

import React from 'react';
import { useAetherStore } from '@/store/useAetherStore';

/**
 * BackgroundEngine — Renders SVG grain/noise texture for realistic "matte" appearance
 * Also optionally renders animated grid pattern for Quantum Cyan theme
 * Uses low opacity to avoid visual noise while adding depth
 */
export function BackgroundEngine() {
    const themeConfig = useAetherStore((s) => s.themeConfig);
    const showGrain = themeConfig.grainEnabled;

    return (
        <>
            {/* SVG Noise Filter for grain texture */}
            {showGrain && (
                <svg
                    style={{
                        position: 'fixed',
                        inset: 0,
                        width: '100%',
                        height: '100%',
                        pointerEvents: 'none',
                        zIndex: 1,
                    }}
                >
                    <defs>
                        {/* Perlin-like noise filter using feTurbulence */}
                        <filter id='noiseFilter'>
                            <feTurbulence
                                type='fractalNoise'
                                baseFrequency='0.9'
                                numOctaves='4'
                                result='noise'
                                seed='2'
                            />
                            {/* Reduce opacity to ~3-5% for subtle texture */}
                            <feColorMatrix
                                in='noise'
                                type='saturate'
                                values='0'
                            />
                            <feComponentTransfer>
                                <feFuncA type='linear' slope='0.04' />
                            </feComponentTransfer>
                            <feComposite in='SourceGraphic' in2='noise' operator='arithmetic' k1='0' k2='1' k3='1' k4='0' />
                        </filter>
                    </defs>

                    {/* Apply noise filter to entire viewport */}
                    <rect
                        width='100%'
                        height='100%'
                        filter='url(#noiseFilter)'
                        style={{
                            fill: 'rgba(255,255,255,0.02)',
                        }}
                    />
                </svg>
            )}

            {/* Optional animated grid pattern (visible in Quantum Cyan theme) */}
            {themeConfig.currentTheme === 'quantum-cyan' && (
                <svg
                    style={{
                        position: 'fixed',
                        inset: 0,
                        width: '100%',
                        height: '100%',
                        pointerEvents: 'none',
                        zIndex: 2,
                        opacity: 0.03,
                    }}
                >
                    <defs>
                        <pattern id='grid' width='40' height='40' patternUnits='userSpaceOnUse'>
                            <path
                                d='M 40 0 L 0 0 0 40'
                                fill='none'
                                stroke='#00E5FF'
                                strokeWidth='0.5'
                            />
                        </pattern>
                    </defs>
                    <rect width='100%' height='100%' fill='url(#grid)' />
                </svg>
            )}

            {/* Optional scanlines overlay (visible when scanlinesEnabled) */}
            {themeConfig.scanlinesEnabled && (
                <div
                    style={{
                        position: 'fixed',
                        inset: 0,
                        pointerEvents: 'none',
                        zIndex: 3,
                        background:
                            'linear-gradient(0deg, rgba(0, 0, 0, 0.15) 50%, transparent 50%)',
                        backgroundSize: '100% 3px',
                        mixBlendMode: 'multiply',
                        opacity: 0.5,
                    }}
                />
            )}
        </>
    );
}
