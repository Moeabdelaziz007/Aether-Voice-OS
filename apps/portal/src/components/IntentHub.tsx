'use client';

/**
 * Intent Hub — Global Header Component
 * 
 * Central command center for AetherOS displaying:
 * - Current session state and mode
 * - Active agent indicators
 * - Quick action buttons
 * - System status telemetry
 */

import React, { useState } from 'react';
import { useTheme } from './ThemeProvider';
import { useMicroAnimations } from '@/hooks/useMicroAnimations';
import clsx from 'clsx';

interface IntentHubProps {
    className?: string;
}

interface AgentStatus {
    name: string;
    role: string;
    active: boolean;
    color: string;
}

export function IntentHub({ className }: IntentHubProps) {
    const { currentTheme, themeMode, toggleThemeMode } = useTheme();
    const { triggerHapticShake, applyMagneticEffect } = useMicroAnimations();
    const [showAgentDetails, setShowAgentDetails] = useState(false);

    // Mock agent data (would connect to real state in production)
    const agents: AgentStatus[] = [
        { name: 'Architect', role: 'Planning & Strategy', active: true, color: 'cyan' },
        { name: 'Coder', role: 'Implementation', active: false, color: 'blue' },
        { name: 'Debugger', role: 'Error Resolution', active: false, color: 'red' },
        { name: 'Optimizer', role: 'Performance', active: false, color: 'green' },
    ];

    const handleThemeToggle = () => {
        toggleThemeMode();
        // Haptic feedback would be triggered here in real implementation
    };

    return (
        <header
            className={clsx(
                'intent-hub',
                'fixed top-0 left-0 right-0 z-50',
                'ultra-glass',
                'border-b border-white/10',
                className
            )}
            style={{
                backdropFilter: 'blur(40px) saturate(1.5)',
                WebkitBackdropFilter: 'blur(40px) saturate(1.5)',
            }}
        >
            {/* Main Bar */}
            <div className="intent-hub-bar flex items-center justify-between px-6 py-3">
                {/* Left: Branding + Session State */}
                <div className="flex items-center gap-6">
                    {/* Logo */}
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 via-blue-500 to-purple-500 flex items-center justify-center shadow-lg">
                            <span className="text-white font-bold text-sm">A</span>
                        </div>
                        <div>
                            <h1 className="text-white font-semibold text-sm tracking-tight">AETHER OS</h1>
                            <p className="text-white/40 text-xs -mt-0.5">Neural Interface</p>
                        </div>
                    </div>

                    {/* Session State Indicator */}
                    <div className="flex items-center gap-2 pl-6 border-l border-white/10">
                        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                        <span className="text-white/80 text-xs font-medium">Session Active</span>
                    </div>
                </div>

                {/* Center: Active Agents */}
                <div className="flex items-center gap-2">
                    {agents.map((agent) => (
                        <div
                            key={agent.name}
                            className={clsx(
                                'agent-indicator relative px-3 py-1.5 rounded-lg border transition-all cursor-pointer',
                                'magnetic-hover interactive-element',
                                agent.active
                                    ? `bg-${agent.color}-500/20 border-${agent.color}-500/30`
                                    : 'bg-white/5 border-white/10 opacity-60'
                            )}
                            onMouseEnter={(e) => {
                                const rect = e.currentTarget.getBoundingClientRect();
                                applyMagneticEffect(e.currentTarget, rect.left + rect.width / 2, rect.top + rect.height / 2);
                            }}
                            onClick={(event) => {
                                triggerHapticShake(event.currentTarget as any, 'normal');
                                setShowAgentDetails(!showAgentDetails);
                            }}
                        >
                            <div className="flex items-center gap-2">
                                <div className={clsx(
                                    'w-1.5 h-1.5 rounded-full',
                                    agent.active ? `bg-${agent.color}-400` : 'bg-gray-500'
                                )} />
                                <span className="text-white/90 text-xs font-medium">{agent.name}</span>
                            </div>

                            {/* Tooltip */}
                            <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 px-2 py-1 bg-black/90 rounded text-xs text-white/90 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
                                {agent.role}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-3">
                    {/* Theme Toggle */}
                    <button
                        onClick={handleThemeToggle}
                        className={clsx(
                            'theme-toggle w-9 h-9 rounded-lg flex items-center justify-center',
                            'magnetic-hover interactive-element',
                            'bg-white/5 hover:bg-white/10',
                            'border border-white/10',
                            'transition-all'
                        )}
                        title={`Switch to ${themeMode === 'dark-state' ? 'White Hole' : 'Dark State'} mode`}
                    >
                        {themeMode === 'dark-state' ? (
                            <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                            </svg>
                        ) : (
                            <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                            </svg>
                        )}
                    </button>

                    {/* Settings Button */}
                    <button
                        className={clsx(
                            'settings-btn w-9 h-9 rounded-lg flex items-center justify-center',
                            'magnetic-hover interactive-element',
                            'bg-white/5 hover:bg-white/10',
                            'border border-white/10',
                            'transition-all'
                        )}
                        title="Open settings"
                    >
                        <svg className="w-5 h-5 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </button>

                    {/* User Avatar */}
                    <div className="user-avatar ml-2 w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center border-2 border-white/20 cursor-pointer hover:border-white/40 transition-all">
                        <span className="text-white text-xs font-semibold">U</span>
                    </div>
                </div>
            </div>

            {/* Expanded Agent Details Panel */}
            {showAgentDetails && (
                <div className="agent-details-panel absolute top-full left-0 right-0 mt-2 mx-6 p-4 rounded-xl ultra-glass border border-white/10 shadow-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="grid grid-cols-4 gap-4">
                        {agents.map((agent) => (
                            <div key={agent.name} className="text-center">
                                <div className={clsx(
                                    'w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center',
                                    `bg-${agent.color}-500/20 border-2 border-${agent.color}-500/30`
                                )}>
                                    <span className="text-white font-bold">{agent.name[0]}</span>
                                </div>
                                <div className="text-white/90 text-sm font-medium">{agent.name}</div>
                                <div className="text-white/50 text-xs mt-1">{agent.role}</div>
                                <div className={clsx(
                                    'mt-2 text-xs px-2 py-1 rounded inline-block',
                                    agent.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                                )}>
                                    {agent.active ? 'Active' : 'Idle'}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </header>
    );
}

export default IntentHub;
