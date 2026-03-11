"use client";
/**
 * AetherOS V2.5 — Unified Dashboard Portal
 *
 * An immersive single-page voice interface merged with a powerful dashboard.
 * - Collapsible sidebar navigation & Smart Widget grid
 * - Integrated Voice Agent with 3D Orb & Unified Scene
 * - Emotional Atmosphere System - UI responds to user emotions
 *
 * Performance: Single Canvas for all 3D elements, lazy-loaded panels.
 */

import { useEffect, useMemo, useState, useCallback } from "react";
import { LayoutGroup, motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";

// Dashboard components
import Sidebar, { type SidebarPanel } from "@/components/dashboard/Sidebar";
import TopBar from "@/components/dashboard/TopBar";
import WidgetGrid from "@/components/dashboard/WidgetGrid";
import WidgetStoreModal from "@/components/dashboard/WidgetStoreModal";

// Shared components
import EdgeGlow from "@/components/shared/EdgeGlow";
import ParticleField from "@/components/shared/ParticleField";
import SilentHintsOverlay from "@/components/shared/SilentHintsOverlay";
import PoweredByStrip from "@/components/shared/PoweredByStrip";
import VoiceIntentBar from "@/components/shared/VoiceIntentBar";
import NeuralBackground from "@/components/shared/NeuralBackground";
import { EmotionalAtmosphere, useEmotionalState } from "@/components/EmotionalAtmosphere";
import NotificationCenter from "@/components/NotificationCenter";

// Management panels
import MemoryPanel from "@/components/management/MemoryPanel";
import SkillsPanel from "@/components/management/SkillsPanel";
import PersonaPanel from "@/components/management/PersonaPanel";
import AgentHub from "@/components/management/AgentHub";

// Voice
import VoiceOrbMini from "@/components/dashboard/VoiceOrbMini";

// Other components
import { SettingsHub } from "@/components/SettingsHub";
import GenerativePortal from "@/components/generative/GenerativePortal";
import ThemeProvider from "@/components/ThemeProvider";
import BackgroundEngine from "@/components/utility/BackgroundEngine";
import TerminalFeed from "@/components/TerminalFeed";
import HUDContainer from "@/components/HUD/HUDContainer";
import MissionControlHUD from "@/components/HUD/MissionControlHUD";
import OrbitalWorkspaceOverlay from "@/components/HUD/OrbitalWorkspaceOverlay";
import MirrorInteractionOverlay from "@/components/HUD/MirrorInteractionOverlay";
import SystemFailure from "@/components/HUD/SystemFailure";
// Landing components
import GemiGramHeader from "@/components/landing/GemiGramHeader";
import GemiGramFooter from "@/components/landing/GemiGramFooter";
import GemiGramSplash from "@/components/landing/GemiGramSplash";
import NeuralIdentityGrid from "@/components/landing/NeuralIdentityGrid";
import VoiceSynthesisDashboard from "@/components/landing/VoiceSynthesisDashboard";

import RealmController from "@/components/realms/RealmController";
import SoulSwapAnimation from "@/components/SoulSwapAnimation";

// Store
import { useAetherStore } from "@/store/useAetherStore";
import { useForgeStore } from "@/store/useForgeStore";
import { useVoiceCommands } from "@/hooks/useVoiceCommands";
import { useUIStateSync } from "@/hooks/useUIStateSync";

// Dynamic 3D scene
const UnifiedScene = dynamic(() => import("@/components/UnifiedScene"), {
    ssr: false,
    loading: () => <div className="fixed inset-0 bg-black" />,
});

// Accent color palette
const ACCENT_RGB: Record<string, [number, number, number]> = {
    cyan: [0, 243, 255],
    purple: [188, 19, 254],
    amber: [245, 158, 11],
    emerald: [16, 185, 129],
    rose: [244, 63, 94],
    green: [57, 255, 20],
    blue: [59, 130, 246],
};

const STATE_INTENSITY: Record<string, number> = {
    IDLE: 0.2,
    LISTENING: 0.6,
    THINKING: 0.8,
    SPEAKING: 1.0,
    INTERRUPTING: 1.2,
};

export default function AetherPortal() {
    const preferences = useAetherStore((s) => s.preferences);
    const themeConfig = useAetherStore((s) => s.themeConfig);
    const engineState = useAetherStore((s) => s.engineState);
    const currentRealm = useAetherStore((s) => s.currentRealm);
    const orbitRegistry = useAetherStore((s) => s.orbitRegistry);
    const activeWidgets = useAetherStore((s) => s.activeWidgets);
    const applyWorkspaceState = useAetherStore((s) => s.applyWorkspaceState);
    const addWidget = useAetherStore((s) => s.addWidget);
    const setPreferences = useAetherStore((s) => s.setPreferences);

    const emotionSenseEnabled = useAetherStore((s) => s.preferences?.superpowers?.emotionSense ?? true);
    const platformFeed = useAetherStore((s) => s.platformFeed);
    const pushToFeed = useAetherStore((s) => s.pushToFeed);

    const agentDNA = useForgeStore((s) => s.dna);
    const [viewMode, setViewMode] = useState<'landing' | 'portal'>('landing');
    const [activePanel, setActivePanel] = useState<SidebarPanel>('dashboard');

    // E2E Onboarding: If agent is not forged, force the Forge; if forged, go to dashboard
    useEffect(() => {
        if (!agentDNA.isForged) {
            setActivePanel('hub');
            // useAetherStore.getState().setActiveHubView?.(.forge.);
        } else {
            // Agent is primed — transition to the Permanent Workspace
            if (activePanel === 'hub') {
                setActivePanel('dashboard');
            }
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
            pushToFeed({
                agentId: 'nexus-07',
                agentName: 'Nexus-7',
                action: 'Successfully optimized the Global Bus latency to 4.2ms.',
                detail: 'O(N) ring buffer logic applied to the neural telemetry stream.',
                type: 'task',
                auraLevel: 8
            });
        }
    }, [platformFeed, pushToFeed]);

    const [settingsOpen, setSettingsOpen] = useState(false);
    const [omnibarOpen, setOmnibarOpen] = useState(false);
    const [isSwapping, setIsSwapping] = useState(false);

    const handleEnterPortal = useCallback((targetPanel?: SidebarPanel) => {
        setIsSwapping(true);
        // Delay the actual view swap to allow the animation to flare
        setTimeout(() => {
            setViewMode('portal');
            if (targetPanel) setActivePanel(targetPanel);
        }, 800);

        // Reset swapping state after animation completes
        setTimeout(() => {
            setIsSwapping(false);
        }, 1500);
    }, []);

    const toggleOmnibar = useCallback(() => setOmnibarOpen(prev => !prev), []);
    const avatarState = useAetherStore((s) => s.avatarState);
    const themeClass = `theme-${themeConfig.currentTheme}`;
    const avatarConfig = { size: 'medium' as const, variant: 'detailed' as const };

    // Determine if we show Voice Agent view or Dashboard view
    const showVoiceView = activePanel === 'voice';
    const showDashboard = activePanel === 'dashboard';
    const showHub = activePanel === 'hub';
    const showManagementPanel = ['memory', 'skills', 'persona'].includes(activePanel || '');
    const showTerminal = activePanel === 'terminal';

    useEffect(() => {
        if (!showVoiceView) return;
        if (!orbitRegistry['planet-notes']) {
            applyWorkspaceState({
                action: 'materialize_app',
                app_id: 'planet-notes',
                x: 140,
                y: 10,
                orbit_lane: 'inner',
            });
        }
        const hasNotesWidget = activeWidgets.some((widget) => widget.type === 'notes_planet');
        if (!hasNotesWidget) {
            addWidget('notes_planet', { appId: 'planet-notes' });
        }
    }, [showVoiceView, orbitRegistry, activeWidgets, applyWorkspaceState, addWidget]);

    useEffect(() => {
        if (typeof window === "undefined") return;
        const params = new URLSearchParams(window.location.search);
        const compactHud = params.get("hud");
        const motion = params.get("motion");
        if (compactHud === "compact") {
            setPreferences({ compactMissionHud: true });
        }
        if (compactHud === "full") {
            setPreferences({ compactMissionHud: false });
        }
        if (motion === "low") {
            setPreferences({ lowMotionMode: true });
        }
        if (motion === "full") {
            setPreferences({ lowMotionMode: false });
        }
    }, [setPreferences]);

    return (
        <ThemeProvider>
                    <EmotionalAtmosphere showDebugOverlay={false}>
                        {/* ⚡ Cinematic Global Transition Layer - Placed outside view switching to avoid unmount flicker */}
                        <SoulSwapAnimation isVisible={isSwapping} />

                        <AnimatePresence mode="wait">
                            {/* The Portal Views */}

                            {viewMode === 'landing' ? (
                                <motion.div
                                    key="landing-view"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0, scale: 1.05, filter: 'blur(20px)' }}
                                    transition={{ duration: 0.8 }}
                                    className="relative min-h-screen bg-[#050505] text-white selection:bg-cyan-500/30 overflow-x-hidden"
                                >
                                    <BackgroundEngine />
                                    <NeuralBackground />
                                    <ParticleField count={40} />
                                    <div className="carbon-fiber-overlay fixed inset-0 opacity-20 pointer-events-none" />

                                    <GemiGramHeader />

                                    <main className="relative z-10">
                                        <GemiGramSplash
                                            onConnect={() => handleEnterPortal('dashboard')}
                                            onCreate={() => handleEnterPortal('hub')}
                                        />

                                        <NeuralIdentityGrid />

                                        <div className="py-20">
                                            <VoiceSynthesisDashboard />
                                        </div>
                                    </main>

                                    <GemiGramFooter />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="portal-view"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 0.8 }}
                                    className={`portal ${themeClass}`}
                                >
                                    <BackgroundEngine />
                                    <NeuralBackground />
                                    <ParticleField count={40} />
                                    <div className="carbon-fiber-overlay" />

                                    <NotificationCenter />
                                    <LayoutGroup>
                                        {/* Sidebar Navigation */}
                                        <Sidebar
                                            activePanel={activePanel}
                                            onPanelChange={setActivePanel}
                                            onOpenSettings={() => setSettingsOpen(true)}
                                        />

                                        <div className="ml-14 flex flex-col h-screen overflow-hidden">
                                            {/* Top Bar with Logo/Back button */}
                                            <div className="top-bar border-b border-white/5 bg-black/20 backdrop-blur-md flex justify-between items-center px-6 transition-all duration-300">
                                                <div className="flex items-center gap-6">
                                                    <button
                                                        onClick={() => setViewMode('landing')}
                                                        className="text-[10px] font-black uppercase tracking-[0.3em] text-white/30 hover:text-cyan-400 transition-all group flex items-center gap-2"
                                                    >
                                                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 opacity-0 group-hover:opacity-100 transition-all" />
                                                        Exit Portal
                                                    </button>
                                                    <div className="h-4 w-px bg-white/10" />
                                                    <div className="opacity-80 scale-90 origin-left">
                                                        <GemiGramHeader hideNav />
                                                    </div>
                                                </div>

                                                <div className="mode-indicators flex gap-2">
                                                    <div className={`mode-dot ${avatarState === 'Listening' ? 'active' : ''}`} data-mode="vision" />
                                                    <div className={`mode-dot ${avatarState === 'Speaking' ? 'active' : ''}`} data-mode="voice" />
                                                    <div className={`mode-dot ${avatarState === 'Thinking' ? 'active' : ''}`} data-mode="code" />
                                                </div>

                                                <TopBar
                                                    onOpenSettings={() => setSettingsOpen(true)}
                                                    onToggleOmnibar={toggleOmnibar}
                                                />
                                            </div>

                                            {/* Main content area */}
                                            <main className="flex-1 overflow-hidden relative">
                                                <AnimatePresence mode="wait">
                                                    {/* Unified 3D Scene (Always active in Portal) */}
                                                    <motion.div
                                                        key="unified-scene"
                                                        initial={{ opacity: 0 }}
                                                        animate={{ opacity: 1 }}
                                                        className="fixed inset-0 pointer-events-none"
                                                    >
                                                        <UnifiedScene
                                                            avatarConfig={avatarConfig}
                                                            showAvatar={true}
                                                            showParticles={true}
                                                            showConnections={true}
                                                        />
                                                    </motion.div>

                                                    {/* Dashboard Content */}
                                                    {showDashboard && (
                                                        <motion.div
                                                            key="dashboard"
                                                            initial={{ opacity: 0, y: 10 }}
                                                            animate={{ opacity: 1, y: 0 }}
                                                            exit={{ opacity: 0, y: -10 }}
                                                            transition={{ duration: 0.3 }}
                                                            className="h-full overflow-y-auto relative z-10"
                                                        >
                                                            <WidgetGrid />
                                                        </motion.div>
                                                    )}

                                                    {/* Voice Agent View: Full Immersive */}
                                                    {showVoiceView && (
                                                        <motion.div
                                                            key="voice"
                                                            initial={{ opacity: 0 }}
                                                            animate={{ opacity: 1 }}
                                                            exit={{ opacity: 0 }}
                                                            transition={{ duration: 0.5 }}
                                                            className="h-full relative z-10"
                                                        >
                                                            <HUDContainer>
                                                                <div className="relative w-full h-full overflow-hidden">
                                                                    <OrbitalWorkspaceOverlay />
                                                                    <MirrorInteractionOverlay />
                                                                    <SystemFailure />
                                                                    <RealmController />
                                                                    <MissionControlHUD />
                                                                </div>
                                                            </HUDContainer>
                                                            <SilentHintsOverlay />
                                                            <GenerativePortal />
                                                        </motion.div>
                                                    )}

                                                    {/* Management Panels */}
                                                    {showManagementPanel && (
                                                        <motion.div
                                                            key={`panel-${activePanel}`}
                                                            initial={{ opacity: 0, x: 20 }}
                                                            animate={{ opacity: 1, x: 0 }}
                                                            exit={{ opacity: 0, x: -20 }}
                                                            transition={{ duration: 0.3 }}
                                                            className="max-w-2xl mx-auto p-6 h-full overflow-y-auto relative z-10"
                                                        >
                                                            {activePanel === 'memory' && <MemoryPanel />}
                                                            {activePanel === 'skills' && <SkillsPanel />}
                                                            {activePanel === 'persona' && <PersonaPanel />}
                                                        </motion.div>
                                                    )}

                                                    {/* Agent Hub */}
                                                    {showHub && (
                                                        <motion.div
                                                            key="hub"
                                                            initial={{ opacity: 0, scale: 0.98 }}
                                                            animate={{ opacity: 1, scale: 1 }}
                                                            exit={{ opacity: 0, scale: 1.02 }}
                                                            transition={{ duration: 0.3 }}
                                                            className="h-full relative z-10"
                                                        >
                                                            <AgentHub />
                                                        </motion.div>
                                                    )}

                                                    {/* Terminal */}
                                                    {showTerminal && (
                                                        <motion.div
                                                            key="terminal"
                                                            initial={{ opacity: 0 }}
                                                            animate={{ opacity: 1 }}
                                                            exit={{ opacity: 0 }}
                                                            className="h-full relative z-10"
                                                        >
                                                            <TerminalFeed />
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </main>
                                        </div>

                                        {/* Shared Portal Elements */}
                                        {!showVoiceView && (
                                            <VoiceOrbMini onActivate={() => setActivePanel('voice')} />
                                        )}
                                        <PoweredByStrip />
                                        <VoiceIntentBar />
                                        <SettingsHub isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
                                        <WidgetStoreModal />
                                        <EdgeGlow />
                                    </LayoutGroup>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </EmotionalAtmosphere>
                </ThemeProvider>
            );
        }
