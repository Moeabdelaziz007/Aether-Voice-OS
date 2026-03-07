'use client';

import React, { useEffect } from 'react';
import { useAetherStore } from '@/store/useAetherStore';
import type { ThemeType } from '@/store/useAetherStore';

/**
 * ThemeProvider — Manages CSS variable updates for theme switching
 * Updates :root element variables directly (zero React re-renders)
 * Syncs with Zustand store for persistence and multi-instance coordination
 */
export default function ThemeProvider({ children }: { children: React.ReactNode }) {
    const themeConfig = useAetherStore((s) => s.themeConfig);
    const visualSettings = useAetherStore((s) => s.visualSettings);

    /**
     * Apply theme changes to CSS variables on :root
     * This triggers instant DOM updates without component re-renders
     */
    useEffect(() => {
        const root = document.documentElement;

        // Apply theme class for complete color palette swap
        const themeClass = `theme-${themeConfig.currentTheme}`;
        root.className = themeClass;

        // Update dynamic CSS variables for glow and blur effects
        root.style.setProperty('--glow-intensity', String(themeConfig.glowIntensity));
        root.style.setProperty('--blur-light', `${themeConfig.blurIntensity}px`);
        root.style.setProperty('--blur-heavy', `${Math.min(themeConfig.blurIntensity + 12, 40)}px`);
        root.style.setProperty('--glow-color', themeConfig.accentColor);

        // Apply visual settings
        root.style.setProperty('--blur-heavy', `${visualSettings.blurHeavy}px`);
        root.style.setProperty('--glow-color', visualSettings.glowColor);
        root.style.setProperty('--bg-primary', visualSettings.backgroundColor);

        // Log theme change
        useAetherStore.getState().addTerminalLog(
            'THEME',
            `Applied ${themeConfig.currentTheme.replace(/-/g, ' ').toUpperCase()} theme`
        );
    }, [themeConfig, visualSettings]);

    return <>{children}</>;
}

/**
 * Hook to change theme and settings
 * Called by ThemeSettingsWidget or commands
 */
export function useTheme() {
    const themeConfig = useAetherStore((s) => s.themeConfig);
    const setThemeConfig = useAetherStore((s) => s.setThemeConfig);
    const setVisualSettings = useAetherStore((s) => s.setVisualSettings);

    return {
        currentTheme: themeConfig.currentTheme,
        accentColor: themeConfig.accentColor,
        glowIntensity: themeConfig.glowIntensity,
        blurIntensity: themeConfig.blurIntensity,
        grainEnabled: themeConfig.grainEnabled,
        scanlinesEnabled: themeConfig.scanlinesEnabled,
        typography: themeConfig.typography,

        // Methods
        setTheme: (theme: ThemeType) => setThemeConfig({ currentTheme: theme }),
        setAccentColor: (color: string) => setThemeConfig({ accentColor: color }),
        setGlowIntensity: (intensity: number) => setThemeConfig({ glowIntensity: Math.max(0, Math.min(1, intensity)) }),
        setBlurIntensity: (blur: number) => setThemeConfig({ blurIntensity: Math.max(3, Math.min(40, blur)) }),
        toggleGrain: () => setThemeConfig({ grainEnabled: !themeConfig.grainEnabled }),
        toggleScanlines: () => setThemeConfig({ scanlinesEnabled: !themeConfig.scanlinesEnabled }),
        setTypography: (type: 'monospace' | 'sans-serif') => setThemeConfig({ typography: type }),
        setVisualSettings,
    };
}
