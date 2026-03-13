"use client";

import { useEffect, useState, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import ThemeProvider from "@/components/ThemeProvider";
import { EmotionalAtmosphere } from "@/components/EmotionalAtmosphere";
import SoulSwapAnimation from "@/components/SoulSwapAnimation";
import TelemetryHUD from "@/components/HUD/TelemetryHUD";

// Store & Hooks
import { useAetherStore } from "@/store/useAetherStore";
import { useForgeStore } from "@/store/useForgeStore";
import { SidebarPanel, AvatarConfig } from "@/store/types";

// Views
import LandingView from "@/components/views/LandingView";
import PortalView from "@/components/views/PortalView";

export default function AetherPortal() {
    // Global State
    const themeConfig = useAetherStore((s) => s.themeConfig);
    const setPreferences = useAetherStore((s) => s.setPreferences);
    const platformFeed = useAetherStore((s) => s.platformFeed);
    const pushToFeed = useAetherStore((s) => s.pushToFeed);
    const avatarState = useAetherStore((s) => s.avatarState);
    const agentDNA = useForgeStore((s) => s.dna);

    // Local UI State
    const [viewMode, setViewMode] = useState<'landing' | 'portal'>('landing');
    const [activePanel, setActivePanel] = useState<SidebarPanel | null>('dashboard');
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [omnibarOpen, setOmnibarOpen] = useState(false);
    const [isSwapping, setIsSwapping] = useState(false);

    // E2E Onboarding & Feed Initialization
    useEffect(() => {
        if (!agentDNA.isForged) {
            setActivePanel('hub');
        } else if (activePanel === 'hub') {
            setActivePanel('dashboard');
        }
    }, [agentDNA.isForged]);

    useEffect(() => {
        if (platformFeed.length === 0) {
            pushToFeed({
                agentId: 'forge-01',
                agentName: 'Aether Forge',
                action: 'Initialized the Gemigram Platform Social Fabric.',
                type: 'achievement',
                auraLevel: 10
            });
        }
    }, [platformFeed, pushToFeed]);

    // Handlers
    const handleEnterPortal = useCallback((targetPanel?: SidebarPanel) => {
        setIsSwapping(true);
        setTimeout(() => {
            setViewMode('portal');
            if (targetPanel) setActivePanel(targetPanel);
        }, 800);
        setTimeout(() => setIsSwapping(false), 1500);
    }, [setViewMode, setActivePanel]);

    const toggleOmnibar = useCallback(() => setOmnibarOpen(prev => !prev), []);
    const themeClass = `theme-${themeConfig.currentTheme}`;
    const avatarConfig: AvatarConfig = { size: 'medium', variant: 'detailed' };

    return (
        <ThemeProvider>
            <EmotionalAtmosphere showDebugOverlay={false}>
                <SoulSwapAnimation isVisible={isSwapping} />
                <AnimatePresence mode="wait">
                    {viewMode === 'landing' ? (
                        <LandingView onEnterPortal={handleEnterPortal} />
                    ) : (
                        <PortalView
                            themeClass={themeClass}
                            activePanel={activePanel as SidebarPanel}
                            setActivePanel={(panel) => setActivePanel(panel)}
                            setViewMode={setViewMode}
                            avatarState={avatarState}
                            avatarConfig={avatarConfig}
                            settingsOpen={settingsOpen}
                            setSettingsOpen={setSettingsOpen}
                            toggleOmnibar={toggleOmnibar}
                        />
                    )}
                </AnimatePresence>
                <TelemetryHUD />
            </EmotionalAtmosphere>
        </ThemeProvider>
    );
}
