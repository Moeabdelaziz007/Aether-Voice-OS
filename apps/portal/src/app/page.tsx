"use client";
/**
 * AetherOS V2.5 — Unified Dashboard Portal
 *
 * A redesigned main page featuring:
 * - Collapsible sidebar navigation
 * - Smart Widget grid (Weather, Crypto, News, Stocks, Tasks, AI Chat)
 * - Integrated Voice Agent with 3D Orb
 * - Memory / Skills / Persona management panels
 * - Widget Store modal for adding/removing widgets
 * - Real-time engine telemetry
 *
 * Performance: Single WebGL context, lazy-loaded panels, CSS-driven animations
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
import Omnibar from "@/components/shared/Omnibar";
import NeuralBackground from "@/components/shared/NeuralBackground";

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
import RealmController from "@/components/realms/RealmController";

// Store
import { useAetherStore } from "@/store/useAetherStore";
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
    const engineState = useAetherStore((s) => s.engineState);
    const currentRealm = useAetherStore((s) => s.currentRealm);
    const orbitRegistry = useAetherStore((s) => s.orbitRegistry);
    const activeWidgets = useAetherStore((s) => s.activeWidgets);
    const applyWorkspaceState = useAetherStore((s) => s.applyWorkspaceState);
    const addWidget = useAetherStore((s) => s.addWidget);
    const setPreferences = useAetherStore((s) => s.setPreferences);

    const platformFeed = useAetherStore((s) => s.platformFeed);
    const pushToFeed = useAetherStore((s) => s.pushToFeed);

    const agentDNA = useForgeStore((s) => s.dna);
    const [activePanel, setActivePanel] = useState<SidebarPanel>('dashboard');

    // Onboarding Logic: If agent is not forged, force the Forge as the main phase
    useEffect(() => {
        if (!agentDNA.isForged) {
            setActivePanel('hub');
            useAetherStore.getState().setActiveHubView('forge');
        } else {
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

    // Wire voice commands & UI Sync
    useVoiceCommands();
    useUIStateSync();

    // Avatar config
    const avatarConfig = useMemo(() => {
        if (activePanel === 'voice' || activePanel === null) {
            switch (currentRealm) {
                case "void": return { size: "large" as const, variant: "immersive" as const };
                case "neural": return { size: "fullscreen" as const, variant: "immersive" as const };
                default: return { size: "medium" as const, variant: "detailed" as const };
            }
        }
        return { size: "medium" as const, variant: "detailed" as const };
    }, [currentRealm, activePanel]);

    // Drive CSS custom properties
    useEffect(() => {
        const root = document.documentElement;
        const rgb = ACCENT_RGB[preferences.accentColor] || ACCENT_RGB.green;
        root.style.setProperty("--accent-r", String(rgb[0]));
        root.style.setProperty("--accent-g", String(rgb[1]));
        root.style.setProperty("--accent-b", String(rgb[2]));
        root.style.setProperty("--glow-intensity", String(STATE_INTENSITY[engineState] ?? 0.2));
    }, [preferences.accentColor, engineState]);

    // Audio level CSS vars
    useEffect(() => {
        const root = document.documentElement;
        let rafId: number;
        const loop = () => {
            root.style.setProperty("--speaker-level", String(useAetherStore.getState().speakerLevel));
            root.style.setProperty("--mic-level", String(useAetherStore.getState().micLevel));
            rafId = requestAnimationFrame(loop);
        };
        rafId = requestAnimationFrame(loop);
        return () => cancelAnimationFrame(rafId);
    }, []);

    const toggleOmnibar = useCallback(() => setOmnibarOpen(prev => !prev), []);

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
            <LayoutGroup>
                {/* Theme & Visual System */}
                <BackgroundEngine />
                <NeuralBackground />
                <ParticleField count={15} />
                <div className="carbon-fiber-overlay" />

                {/* Sidebar Navigation */}
                <Sidebar
                    activePanel={activePanel}
                    onPanelChange={setActivePanel}
                    onOpenSettings={() => setSettingsOpen(true)}
                />

                {/* Main content area — offset by sidebar width */}
                <div className="ml-14 flex flex-col h-screen overflow-hidden">
                    {/* Top Bar */}
                    <TopBar
                        onOpenSettings={() => setSettingsOpen(true)}
                        onToggleOmnibar={toggleOmnibar}
                    />

                    {/* Main content */}
                    <main className="flex-1 overflow-y-auto overflow-x-hidden relative">
                        <AnimatePresence mode="wait">
                            {/* ── Dashboard View: Widget Grid ── */}
                            {showDashboard && (
                                <motion.div
                                    key="dashboard"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    transition={{ duration: 0.3 }}
                                    className="h-full"
                                >
                                    <WidgetGrid />
                                </motion.div>
                            )}

                            {/* ── Voice Agent View: Full Immersive 3D + Realms ── */}
                            {showVoiceView && (
                                <motion.div
                                    key="voice"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 0.5 }}
                                    className="fixed inset-0 ml-14"
                                >
                                    {/* 3D Scene */}
                                    <UnifiedScene
                                        avatarConfig={avatarConfig}
                                        showAvatar={true}
                                        showParticles={true}
                                        showConnections={true}
                                    />

                                    {/* Edge Glow */}
                                    <EdgeGlow />

                                    {/* HUD Frame */}
                                    <HUDContainer>
                                        <div className="relative w-full h-screen overflow-hidden">
                                            <OrbitalWorkspaceOverlay />
                                            <MirrorInteractionOverlay />
                                            <SystemFailure />
                                            <RealmController />
                                            <MissionControlHUD />
                                        </div>
                                    </HUDContainer>

                                    {/* Silent Hints */}
                                    <SilentHintsOverlay />

                                    {/* Generative UI Widgets */}
                                    <GenerativePortal />
                                </motion.div>
                            )}

                            {/* ── Management Panels: Memory / Skills / Persona ── */}
                            {showManagementPanel && (
                                <motion.div
                                    key={`panel-${activePanel}`}
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.3 }}
                                    className="max-w-2xl mx-auto p-6 h-full"
                                >
                                    {activePanel === 'memory' && <MemoryPanel />}
                                    {activePanel === 'skills' && <SkillsPanel />}
                                    {activePanel === 'persona' && <PersonaPanel />}
                                </motion.div>
                            )}

                            {/* ── Agent Hub View: Social Fabric & Discovery ── */}
                            {showHub && (
                                <motion.div
                                    key="hub"
                                    initial={{ opacity: 0, scale: 0.98 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 1.02 }}
                                    transition={{ duration: 0.3 }}
                                    className="h-full"
                                >
                                    <AgentHub />
                                </motion.div>
                            )}

                            {/* ── Terminal View ── */}
                            {showTerminal && (
                                <motion.div
                                    key="terminal"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="h-full"
                                >
                                    <TerminalFeed />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </main>
                </div>

                {/* Voice Orb Mini — Floating button on dashboard view */}
                {!showVoiceView && (
                    <VoiceOrbMini onActivate={() => setActivePanel('voice')} />
                )}

                {/* Powered By Strip */}
                <PoweredByStrip />

                {/* Omnibar — Global command entry */}
                <Omnibar />

                {/* Settings Hub Modal */}
                <SettingsHub isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />

                {/* Widget Store Modal */}
                <WidgetStoreModal />
            </LayoutGroup>
        </ThemeProvider>
    );
}
