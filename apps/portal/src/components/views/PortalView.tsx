
import React from 'react';
import { motion, LayoutGroup, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import Sidebar, { SidebarPanel } from '../dashboard/Sidebar';
import TopBar from '../dashboard/TopBar';
import WidgetGrid from '../dashboard/WidgetGrid';
import WidgetStoreModal from '../dashboard/WidgetStoreModal';
import EdgeGlow from '../shared/EdgeGlow';
import PoweredByStrip from '../shared/PoweredByStrip';
import VoiceIntentBar from '../shared/VoiceIntentBar';
import NeuralBackground from '../shared/NeuralBackground';
import BackgroundEngine from '../utility/BackgroundEngine';
import ParticleField from '../shared/ParticleField';
import NotificationCenter from '../NotificationCenter';
import GemiGramHeader from '../landing/GemiGramHeader';
import VoiceOrbMini from '../dashboard/VoiceOrbMini';
import HUDContainer from '../HUD/HUDContainer';
import OrbitalWorkspaceOverlay from '../HUD/OrbitalWorkspaceOverlay';
import MirrorInteractionOverlay from '../HUD/MirrorInteractionOverlay';
import SystemFailure from '../HUD/SystemFailure';
import RealmController from '../realms/RealmController';
import MissionControlHUD from '../HUD/MissionControlHUD';
import SilentHintsOverlay from '../shared/SilentHintsOverlay';
import GenerativePortal from '../generative/GenerativePortal';
import MemoryPanel from '../management/MemoryPanel';
import SkillsPanel from '../management/SkillsPanel';
import PersonaPanel from '../management/PersonaPanel';
import AgentHub from '../management/AgentHub';
import TerminalFeed from '../TerminalFeed';
import { SettingsHub } from '../SettingsHub';

const UnifiedScene = dynamic(() => import('@/components/UnifiedScene'), {
    ssr: false,
    loading: () => <div className="fixed inset-0 bg-black" />,
});

interface PortalViewProps {
    themeClass: string;
    activePanel: SidebarPanel;
    setActivePanel: (panel: SidebarPanel) => void;
    setViewMode: (mode: 'landing' | 'portal') => void;
    avatarState: string;
    avatarConfig: any;
    settingsOpen: boolean;
    setSettingsOpen: (open: boolean) => void;
    toggleOmnibar: () => void;
}

export default function PortalView({
    themeClass,
    activePanel,
    setActivePanel,
    setViewMode,
    avatarState,
    avatarConfig,
    settingsOpen,
    setSettingsOpen,
    toggleOmnibar
}: PortalViewProps) {
    const showVoiceView = activePanel === 'voice';
    const showDashboard = activePanel === 'dashboard';
    const showHub = activePanel === 'hub';
    const showManagementPanel = ['memory', 'skills', 'persona'].includes(activePanel || '');
    const showTerminal = activePanel === 'terminal';

    return (
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
                <Sidebar
                    activePanel={activePanel}
                    onPanelChange={setActivePanel}
                    onOpenSettings={() => setSettingsOpen(true)}
                />

                <div className="ml-14 flex flex-col h-screen overflow-hidden">
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

                    <main className="flex-1 overflow-hidden relative">
                        <AnimatePresence mode="wait">
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
                                            <dynamic.CommunicationSanctum 
                                                agentName={avatarConfig?.name || "Aether Specialist"}
                                                agentAura={avatarConfig?.aura || "cyan"}
                                                emotionalState={avatarState === 'Listening' ? 'listening' : avatarState === 'Speaking' ? 'speaking' : 'thinking'}
                                            />
                                            <RealmController />
                                            <MissionControlHUD />
                                        </div>
                                    </HUDContainer>
                                    <SilentHintsOverlay />
                                    <GenerativePortal />
                                </motion.div>
                            )}

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
    );
}
