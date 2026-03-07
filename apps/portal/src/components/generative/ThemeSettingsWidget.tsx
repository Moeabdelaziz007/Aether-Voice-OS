'use client';

import React from 'react';
import { useTheme } from '@/components/ThemeProvider';
import { useAetherStore } from '@/store/useAetherStore';
import type { ThemeType } from '@/store/useAetherStore';

/**
 * ThemeSettingsWidget — Grid-based control panel for theme and visual adjustments
 * Theme selector, accent color picker, blur/glow sliders, texture toggles
 * Real-time preview as sliders move
 */
export function ThemeSettingsWidget() {
    const theme = useTheme();
    const addTerminalLog = useAetherStore((s) => s.addTerminalLog);

    const THEME_NAMES: Record<ThemeType, string> = {
        'matrix-core': 'Matrix Core',
        'quantum-cyan': 'Quantum Cyan',
        'cyber-amber': 'Cyber Amber',
        'ghost-white': 'Ghost White',
    };

    const THEME_COLORS: Record<ThemeType, string> = {
        'matrix-core': '#00FF41',
        'quantum-cyan': '#00E5FF',
        'cyber-amber': '#FFB000',
        'ghost-white': '#FFFFFF',
    };

    const handleThemeChange = (newTheme: ThemeType) => {
        theme.setTheme(newTheme);
        addTerminalLog('THEME', `Applied ${THEME_NAMES[newTheme]} theme`);
    };

    const handleGlowChange = (newGlow: number) => {
        theme.setGlowIntensity(newGlow);
    };

    const handleBlurChange = (newBlur: number) => {
        theme.setBlurIntensity(newBlur);
    };

    return (
        <div
            style={{
                background: 'rgba(10, 10, 20, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1.5rem',
                fontFamily: 'var(--f-mono)',
                animation: 'terminal-line-in 0.4s ease-out',
                marginTop: '1rem',
            }}
        >
            {/* Header */}
            <div style={{ marginBottom: '1.5rem' }}>
                <span style={{ color: 'var(--log-theme)', fontWeight: 600, fontSize: '0.9rem' }}>
                    THEME SETTINGS
                </span>
            </div>

            {/* Theme Selector — Hexagonal swatches */}
            <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginBottom: '0.75rem' }}>
                    Theme:
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    {(Object.keys(THEME_NAMES) as ThemeType[]).map((themeKey) => (
                        <button
                            key={themeKey}
                            onClick={() => handleThemeChange(themeKey)}
                            style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: theme.currentTheme === themeKey ? '8px' : '6px',
                                background: THEME_COLORS[themeKey],
                                border: theme.currentTheme === themeKey
                                    ? '2px solid white'
                                    : '1px solid rgba(255,255,255,0.3)',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                opacity: 0.85,
                                position: 'relative',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.opacity = '1';
                                e.currentTarget.style.transform = 'scale(1.05)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.opacity = '0.85';
                                e.currentTarget.style.transform = 'scale(1)';
                            }}
                            title={THEME_NAMES[themeKey]}
                        />
                    ))}
                </div>
            </div>

            {/* Glow Intensity Slider */}
            <div style={{ marginBottom: '1.25rem' }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '0.5rem',
                }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                        Glow Intensity:
                    </span>
                    <span style={{ color: 'var(--log-theme)', fontSize: '0.8rem', fontWeight: 600 }}>
                        {(theme.glowIntensity * 100).toFixed(0)}%
                    </span>
                </div>
                <input
                    type='range'
                    min='0'
                    max='1'
                    step='0.1'
                    value={theme.glowIntensity}
                    onChange={(e) => handleGlowChange(parseFloat(e.target.value))}
                    style={{
                        width: '100%',
                        cursor: 'pointer',
                        accentColor: 'var(--log-theme)',
                    }}
                />
            </div>

            {/* Blur Intensity Slider */}
            <div style={{ marginBottom: '1.25rem' }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '0.5rem',
                }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                        Blur Intensity:
                    </span>
                    <span style={{ color: 'var(--log-theme)', fontSize: '0.8rem', fontWeight: 600 }}>
                        {theme.blurIntensity}px
                    </span>
                </div>
                <input
                    type='range'
                    min='3'
                    max='40'
                    step='1'
                    value={theme.blurIntensity}
                    onChange={(e) => handleBlurChange(parseInt(e.target.value))}
                    style={{
                        width: '100%',
                        cursor: 'pointer',
                        accentColor: 'var(--log-theme)',
                    }}
                />
            </div>

            {/* Toggle Switches */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {/* Grain Toggle */}
                <button
                    onClick={theme.toggleGrain}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '0.75rem',
                        background: theme.grainEnabled ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.05)',
                        border: theme.grainEnabled ? '1px solid rgba(6, 182, 212, 0.5)' : '1px solid rgba(255,255,255,0.15)',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.08)';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.background = theme.grainEnabled ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.05)';
                    }}
                >
                    <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '16px',
                        height: '16px',
                        border: '1px solid ' + (theme.grainEnabled ? 'var(--log-theme)' : 'rgba(255,255,255,0.3)'),
                        borderRadius: '2px',
                        background: theme.grainEnabled ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                        color: 'var(--log-theme)',
                        fontSize: '0.7rem',
                        fontWeight: 'bold',
                    }}>
                        {theme.grainEnabled ? '✓' : ''}
                    </span>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                        Grain Texture
                    </span>
                </button>

                {/* Scanlines Toggle */}
                <button
                    onClick={theme.toggleScanlines}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '0.75rem',
                        background: theme.scanlinesEnabled ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.05)',
                        border: theme.scanlinesEnabled ? '1px solid rgba(6, 182, 212, 0.5)' : '1px solid rgba(255,255,255,0.15)',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.08)';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.background = theme.scanlinesEnabled ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.05)';
                    }}
                >
                    <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '16px',
                        height: '16px',
                        border: '1px solid ' + (theme.scanlinesEnabled ? 'var(--log-theme)' : 'rgba(255,255,255,0.3)'),
                        borderRadius: '2px',
                        background: theme.scanlinesEnabled ? 'rgba(6, 182, 212, 0.3)' : 'transparent',
                        color: 'var(--log-theme)',
                        fontSize: '0.7rem',
                        fontWeight: 'bold',
                    }}>
                        {theme.scanlinesEnabled ? '✓' : ''}
                    </span>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                        Scanlines
                    </span>
                </button>
            </div>
        </div>
    );
}
