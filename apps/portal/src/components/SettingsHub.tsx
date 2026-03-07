/**
 * Aether Voice OS — Settings & Customization Hub
 * 
 * Comprehensive settings center for theme, agents, audio, and preferences.
 * Features tabbed navigation with real-time preview and persistence.
 * 
 * Sections:
 * - Theme & Appearance (Dark State / White Hole)
 * - Agent Preferences (Specialist configuration)
 * - Audio & Video (Device selection)
 * - Keyboard Shortcuts (Custom bindings)
 * - User Profile (Identity & preferences)
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAetherStore } from '../store/useAetherStore';

interface SettingsHubProps {
    isOpen: boolean;
    onClose: () => void;
}

type SettingsTab = 'theme' | 'agents' | 'audio' | 'shortcuts' | 'profile';

export const SettingsHub: React.FC<SettingsHubProps> = ({
    isOpen,
    onClose,
}) => {
    const store = useAetherStore();
    const [activeTab, setActiveTab] = useState<SettingsTab>('theme');
    const [hasChanges, setHasChanges] = useState(false);

    // Local state for settings
    const [themeMode, setThemeMode] = useState<'dark-state' | 'white-hole'>('dark-state');
    const [glowIntensity, setGlowIntensity] = useState(0.5);
    const [autoRestartAgents, setAutoRestartAgents] = useState(true);
    const [enableNotifications, setEnableNotifications] = useState(true);
    const [audioInputDevice, setAudioInputDevice] = useState('default');
    const [audioOutputDevice, setAudioOutputDevice] = useState('default');

    // Reset state when opening/closing
    useEffect(() => {
        if (!isOpen) {
            setHasChanges(false);
        }
    }, [isOpen]);

    // Handle setting changes
    const handleSettingChange = (setter: React.Dispatch<React.SetStateAction<any>>) => {
        return (value: any) => {
            setter(value);
            setHasChanges(true);
        };
    };

    // Save all settings
    const handleSave = () => {
        // Apply theme
        document.documentElement.setAttribute('data-theme', themeMode);
        
        // Apply glow intensity
        document.documentElement.style.setProperty('--glow-intensity', glowIntensity.toString());
        
        // Persist to store
        store.setSettings({
            theme: themeMode,
            glowIntensity,
            autoRestartAgents,
            enableNotifications,
            audioInput: audioInputDevice,
            audioOutput: audioOutputDevice,
        });

        setHasChanges(false);
        onClose();
    };

    // Render tab content
    const renderTabContent = () => {
        switch (activeTab) {
            case 'theme':
                return <ThemeSettings {...{ themeMode, setThemeMode: handleSettingChange(setThemeMode), glowIntensity, setGlowIntensity: handleSettingChange(setGlowIntensity) }} />;
            case 'agents':
                return <AgentSettings {...{ autoRestartAgents, setAutoRestartAgents: handleSettingChange(setAutoRestartAgents) }} />;
            case 'audio':
                return <AudioSettings {...{ audioInputDevice, setAudioInputDevice: handleSettingChange(setAudioInputDevice), audioOutputDevice, setAudioOutputDevice: handleSettingChange(setAudioOutputDevice) }} />;
            case 'shortcuts':
                return <ShortcutsSettings />;
            case 'profile':
                return <ProfileSettings />;
            default:
                return null;
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div 
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Settings Modal */}
            <div className="relative w-full max-w-4xl mx-4 max-h-[85vh] overflow-hidden">
                <div className="ultra-glass rounded-2xl border border-white/10 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                    
                    {/* Header */}
                    <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-cyan-500/10 to-purple-500/10">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-2xl font-bold text-white">
                                    ⚙️ Settings & Customization
                                </h2>
                                <p className="text-sm text-gray-400 mt-1">
                                    Personalize your Aether experience
                                </p>
                            </div>
                            <button
                                onClick={onClose}
                                title="Close settings"
                                className="text-gray-400 hover:text-white transition-colors text-2xl"
                            >
                                ✕
                            </button>
                        </div>
                    </div>

                    {/* Tabs Navigation */}
                    <div className="flex border-b border-white/10 bg-black/20">
                        {[
                            { id: 'theme', label: 'Theme', icon: '🎨' },
                            { id: 'agents', label: 'Agents', icon: '🤖' },
                            { id: 'audio', label: 'Audio', icon: '🔊' },
                            { id: 'shortcuts', label: 'Shortcuts', icon: '⌨️' },
                            { id: 'profile', label: 'Profile', icon: '👤' },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as SettingsTab)}
                                className={`flex-1 px-4 py-3 text-sm font-medium transition-all ${
                                    activeTab === tab.id
                                        ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
                                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`}
                            >
                                <span className="mr-2">{tab.icon}</span>
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Tab Content */}
                    <div className="flex-1 overflow-y-auto p-6 max-h-[60vh]">
                        {renderTabContent()}
                    </div>

                    {/* Footer Actions */}
                    <div className="px-6 py-4 border-t border-white/10 bg-black/20 flex items-center justify-between">
                        <div className="text-sm text-gray-400">
                            {hasChanges ? (
                                <span className="text-yellow-400">●</span>
                            ) : (
                                <span className="text-green-400">✓</span>
                            )}
                            {' '}
                            {hasChanges ? 'Unsaved changes' : 'All changes saved'}
                        </div>
                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="button"
                                onClick={handleSave}
                                disabled={!hasChanges}
                                className="px-6 py-2 text-sm font-medium text-white bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// ──────────────────────────────────────────────────────────────────────────
// Theme Settings Panel
// ──────────────────────────────────────────────────────────────────────────

const ThemeSettings: React.FC<{
    themeMode: 'dark-state' | 'white-hole';
    setThemeMode: (value: 'dark-state' | 'white-hole') => void;
    glowIntensity: number;
    setGlowIntensity: (value: number) => void;
}> = ({ themeMode, setThemeMode, glowIntensity, setGlowIntensity }) => {
    return (
        <div className="space-y-6">
            {/* Theme Mode Selection */}
            <div>
                <h3 className="text-lg font-semibold text-white mb-4">
                    Theme Mode
                </h3>
                <div className="grid grid-cols-2 gap-4">
                    <button
                        onClick={() => setThemeMode('dark-state')}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${
                            themeMode === 'dark-state'
                                ? 'border-cyan-500 bg-cyan-500/10'
                                : 'border-white/10 bg-white/5 hover:border-white/20'
                        }`}
                    >
                        <div className="text-2xl mb-2">🌑</div>
                        <div className="font-medium text-white">Dark State</div>
                        <div className="text-xs text-gray-400 mt-1">
                            Default industrial sci-fi theme
                        </div>
                    </button>
                    <button
                        onClick={() => setThemeMode('white-hole')}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${
                            themeMode === 'white-hole'
                                ? 'border-purple-500 bg-purple-500/10'
                                : 'border-white/10 bg-white/5 hover:border-white/20'
                        }`}
                    >
                        <div className="text-2xl mb-2">⚪</div>
                        <div className="font-medium text-white">White Hole</div>
                        <div className="text-xs text-gray-400 mt-1">
                            Bright minimalist alternative
                        </div>
                    </button>
                </div>
            </div>

            {/* Glow Intensity Slider */}
            <div>
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-white">
                        Bioluminescent Glow Intensity
                    </h3>
                    <span className="text-sm text-cyan-400 font-mono">
                        {(glowIntensity * 100).toFixed(0)}%
                    </span>
                </div>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={glowIntensity}
                    onChange={(e) => setGlowIntensity(parseFloat(e.target.value))}
                    aria-label="Glow intensity slider"
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-2">
                    <span>Subtle</span>
                    <span>Balanced</span>
                    <span>Intense</span>
                </div>
            </div>

            {/* Preview */}
            <div className="p-4 rounded-lg bg-gradient-to-br from-cyan-500/10 to-purple-500/10 border border-white/10">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Preview</h4>
                <div className="flex items-center gap-3">
                    <div 
                        className="w-12 h-12 rounded-full"
                        style={{
                            boxShadow: `0 0 ${20 + glowIntensity * 40}px rgba(6, 182, 212, ${0.4 + glowIntensity * 0.4})`,
                            background: `linear-gradient(135deg, #06B6D4, #0891b2)`,
                        }}
                    />
                    <span className="text-sm text-gray-400">
                        Glow effect preview
                    </span>
                </div>
            </div>
        </div>
    );
};

// ──────────────────────────────────────────────────────────────────────────
// Agent Settings Panel
// ──────────────────────────────────────────────────────────────────────────

const AgentSettings: React.FC<{
    autoRestartAgents: boolean;
    setAutoRestartAgents: (value: boolean) => void;
}> = ({ autoRestartAgents, setAutoRestartAgents }) => {
    return (
        <div className="space-y-6">
            {/* Auto Restart Toggle */}
            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
                <div>
                    <h3 className="font-medium text-white">Auto-Restart Agents</h3>
                    <p className="text-sm text-gray-400 mt-1">
                        Automatically restart specialist agents on failure
                    </p>
                </div>
                <button
                    onClick={() => setAutoRestartAgents(!autoRestartAgents)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                        autoRestartAgents ? 'bg-green-500' : 'bg-gray-600'
                    }`}
                >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                        autoRestartAgents ? 'translate-x-6' : 'translate-x-0.5'
                    }`} />
                </button>
            </div>

            {/* Agent Status Info */}
            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                <h4 className="text-sm font-medium text-blue-400 mb-2">
                    ℹ️ Active Specialists
                </h4>
                <div className="space-y-2 text-sm text-gray-300">
                    <div className="flex justify-between">
                        <span>AetherCore (Root)</span>
                        <span className="text-green-400">● Active</span>
                    </div>
                    <div className="flex justify-between">
                        <span>ArchitectAgent</span>
                        <span className="text-green-400">● Available</span>
                    </div>
                    <div className="flex justify-between">
                        <span>DebuggerAgent</span>
                        <span className="text-green-400">● Available</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

// ──────────────────────────────────────────────────────────────────────────
// Audio Settings Panel
// ──────────────────────────────────────────────────────────────────────────

const AudioSettings: React.FC<{
    audioInputDevice: string;
    setAudioInputDevice: (value: string) => void;
    audioOutputDevice: string;
    setAudioOutputDevice: (value: string) => void;
}> = ({ audioInputDevice, setAudioInputDevice, audioOutputDevice, setAudioOutputDevice }) => {
    return (
        <div className="space-y-6">
            {/* Input Device */}
            <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    🎤 Microphone Input
                </label>
                <select
                    value={audioInputDevice}
                    onChange={(e) => setAudioInputDevice(e.target.value)}
                    aria-label="Microphone input device selection"
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white outline-none focus:border-cyan-500/50 transition-colors"
                >
                    <option value="default">Default (System)</option>
                    <option value="builtin">Built-in Microphone</option>
                    <option value="usb">USB Microphone</option>
                    <option value="bluetooth">Bluetooth Device</option>
                </select>
            </div>

            {/* Output Device */}
            <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    🔊 Speaker Output
                </label>
                <select
                    value={audioOutputDevice}
                    onChange={(e) => setAudioOutputDevice(e.target.value)}
                    aria-label="Speaker output device selection"
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white outline-none focus:border-cyan-500/50 transition-colors"
                >
                    <option value="default">Default (System)</option>
                    <option value="builtin">Built-in Speakers</option>
                    <option value="headphones">Headphones</option>
                    <option value="bluetooth">Bluetooth Device</option>
                </select>
            </div>

            {/* Test Buttons */}
            <div className="flex gap-3">
                <button className="flex-1 px-4 py-2 text-sm font-medium text-white bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                    Test Microphone
                </button>
                <button className="flex-1 px-4 py-2 text-sm font-medium text-white bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                    Test Speakers
                </button>
            </div>
        </div>
    );
};

// ──────────────────────────────────────────────────────────────────────────
// Shortcuts Settings Panel
// ──────────────────────────────────────────────────────────────────────────

const ShortcutsSettings: React.FC = () => {
    const shortcuts = [
        { action: 'Open Command Palette', shortcut: '⌘K / Ctrl+K' },
        { action: 'Toggle Theme', shortcut: '⌘T' },
        { action: 'Go to Dashboard', shortcut: '⌘D' },
        { action: 'Go to Live Interface', shortcut: '⌘L' },
        { action: 'Open Settings', shortcut: '⌘,' },
        { action: 'Restart Session', shortcut: '⌘R' },
    ];

    return (
        <div className="space-y-4">
            {shortcuts.map((item, index) => (
                <div 
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10"
                >
                    <span className="text-white">{item.action}</span>
                    <kbd className="px-3 py-1.5 text-sm font-mono text-gray-300 bg-black/30 rounded border border-white/10">
                        {item.shortcut}
                    </kbd>
                </div>
            ))}
            
            <div className="mt-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                <p className="text-sm text-yellow-400">
                    💡 Tip: Press <kbd className="px-2 py-0.5 bg-black/30 rounded">⌘K</kbd> anywhere 
                    to quickly access commands without memorizing shortcuts.
                </p>
            </div>
        </div>
    );
};

// ──────────────────────────────────────────────────────────────────────────
// Profile Settings Panel
// ──────────────────────────────────────────────────────────────────────────

const ProfileSettings: React.FC = () => {
    return (
        <div className="space-y-6">
            {/* User Info */}
            <div className="flex items-center gap-4 p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-2xl font-bold text-white">
                    MA
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-white">Mohamed Hossameldin</h3>
                    <p className="text-sm text-gray-400">AI Systems Engineer</p>
                    <p className="text-xs text-cyan-400 mt-1">@cryptojoker710</p>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-center">
                    <div className="text-2xl font-bold text-cyan-400">94%</div>
                    <div className="text-xs text-gray-400 mt-1">Completion</div>
                </div>
                <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30 text-center">
                    <div className="text-2xl font-bold text-purple-400">35</div>
                    <div className="text-xs text-gray-400 mt-1">Tasks Done</div>
                </div>
                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30 text-center">
                    <div className="text-2xl font-bold text-green-400">100%</div>
                    <div className="text-xs text-gray-400 mt-1">Backend Verified</div>
                </div>
            </div>

            {/* Account Actions */}
            <div className="space-y-2">
                <button className="w-full px-4 py-2 text-sm font-medium text-white bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-left">
                    Export Configuration
                </button>
                <button className="w-full px-4 py-2 text-sm font-medium text-white bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-left">
                    Import Configuration
                </button>
                <button className="w-full px-4 py-2 text-sm font-medium text-red-400 bg-red-500/10 rounded-lg hover:bg-red-500/20 transition-colors text-left">
                    Reset All Settings
                </button>
            </div>
        </div>
    );
};

export default SettingsHub;
