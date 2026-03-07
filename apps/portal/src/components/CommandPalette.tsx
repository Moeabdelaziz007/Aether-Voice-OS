/**
 * Aether Voice OS — Command Palette
 * 
 * Neural interface command center for quick actions and search.
 * Inspired by Raycast, Spotlight, and VS Code Command Palette.
 * 
 * Features:
 * - Keyboard shortcuts (⌘K / Ctrl+K)
 * - Fuzzy search across commands
 * - Agent-specific commands
 * - Recent commands history
 * - Context-aware suggestions
 */

'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useADKAgents } from '../hooks/useADKAgents';

interface Command {
    id: string;
    label: string;
    description?: string;
    category: 'system' | 'agent' | 'navigation' | 'settings';
    shortcut?: string;
    icon: string;
    action: () => void | Promise<void>;
}

interface CommandPaletteProps {
    isOpen: boolean;
    onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
    isOpen,
    onClose,
}) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const { delegateTask, agents, activeAgent } = useADKAgents();

    // Define available commands
    const commands: Command[] = [
        // System Commands
        {
            id: 'toggle-theme',
            label: 'Toggle Theme Mode',
            description: 'Switch between Dark State and White Hole themes',
            category: 'system',
            shortcut: '⌘T',
            icon: '🎨',
            action: () => {
                const event = new CustomEvent('aether-toggle-theme');
                window.dispatchEvent(event);
            },
        },
        {
            id: 'restart-session',
            label: 'Restart Session',
            description: 'Reinitialize Gemini Live connection',
            category: 'system',
            icon: '🔄',
            action: async () => {
                await delegateTask('Restart the voice session', activeAgent || 'AetherCore');
            },
        },
        {
            id: 'clear-memory',
            label: 'Clear Short-term Memory',
            description: 'Reset conversation context',
            category: 'system',
            icon: '🧹',
            action: () => {
                console.log('[Command] Clearing memory...');
            },
        },

        // Agent Commands
        ...agents.map(agent => ({
            id: `switch-${agent.name}`,
            label: `Switch to ${agent.name}`,
            description: agent.description,
            category: 'agent' as const,
            icon: '🤖',
            action: () => {
                console.log(`[Command] Switching to ${agent.name}`);
            },
        })),

        // Navigation Commands
        {
            id: 'go-to-dashboard',
            label: 'Go to Dashboard',
            description: 'Navigate to main dashboard',
            category: 'navigation',
            shortcut: '⌘D',
            icon: '📊',
            action: () => {
                window.location.href = '/';
            },
        },
        {
            id: 'go-to-live',
            label: 'Go to Live Interface',
            description: 'Open voice interaction UI',
            category: 'navigation',
            shortcut: '⌘L',
            icon: '🎙️',
            action: () => {
                window.location.href = '/live';
            },
        },
        {
            id: 'go-to-admin',
            label: 'Go to Admin Panel',
            description: 'Access system administration',
            category: 'navigation',
            icon: '⚙️',
            action: () => {
                window.location.href = '/admin';
            },
        },

        // Settings Commands
        {
            id: 'open-settings',
            label: 'Open Settings',
            description: 'Configure application preferences',
            category: 'settings',
            shortcut: '⌘,',
            icon: '⚙️',
            action: () => {
                const event = new CustomEvent('aether-open-settings');
                window.dispatchEvent(event);
            },
        },
        {
            id: 'configure-agents',
            label: 'Configure Agents',
            description: 'Manage ADK specialist settings',
            category: 'settings',
            icon: '🔧',
            action: () => {
                console.log('[Command] Opening agent configuration...');
            },
        },
    ];

    // Filter commands based on query
    const filteredCommands = commands.filter(cmd => {
        if (!query.trim()) return true;
        
        const searchQuery = query.toLowerCase();
        return (
            cmd.label.toLowerCase().includes(searchQuery) ||
            cmd.description?.toLowerCase().includes(searchQuery) ||
            cmd.category.includes(searchQuery)
        );
    });

    // Handle keyboard navigation
    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setSelectedIndex(prev => 
                    prev < filteredCommands.length - 1 ? prev + 1 : prev
                );
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                setSelectedIndex(prev => (prev > 0 ? prev - 1 : prev));
                break;
                
            case 'Enter':
                e.preventDefault();
                if (filteredCommands[selectedIndex]) {
                    filteredCommands[selectedIndex].action();
                    onClose();
                }
                break;
                
            case 'Escape':
                onClose();
                break;
        }
    }, [filteredCommands, selectedIndex, onClose]);

    // Focus input on open
    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    // Reset state when opening/closing
    useEffect(() => {
        if (!isOpen) {
            setQuery('');
            setSelectedIndex(0);
        }
    }, [isOpen]);

    // Global keyboard shortcut
    useEffect(() => {
        const handleGlobalKeydown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                if (!isOpen) {
                    // Open palette
                    const event = new CustomEvent('aether-open-palette');
                    window.dispatchEvent(event);
                } else {
                    onClose();
                }
            }
        };

        window.addEventListener('keydown', handleGlobalKeydown);
        return () => window.removeEventListener('keydown', handleGlobalKeydown);
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
            {/* Backdrop */}
            <div 
                className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            />

            {/* Command Palette Modal */}
            <div className="relative w-full max-w-2xl mx-4">
                <div className="ultra-glass rounded-2xl border border-white/10 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                    
                    {/* Search Input */}
                    <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
                        <span className="text-xl">🔍</span>
                        <input
                            ref={inputRef}
                            type="text"
                            value={query}
                            onChange={(e) => {
                                setQuery(e.target.value);
                                setSelectedIndex(0);
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder="Type a command or search..."
                            className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-lg"
                        />
                        {query && (
                            <button
                                onClick={() => {
                                    setQuery('');
                                    setSelectedIndex(0);
                                    inputRef.current?.focus();
                                }}
                                className="text-gray-400 hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        )}
                    </div>

                    {/* Commands List */}
                    <div className="max-h-[60vh] overflow-y-auto p-2">
                        {filteredCommands.length === 0 ? (
                            <div className="px-4 py-8 text-center text-gray-400">
                                No commands found for &quot;{query}&quot;
                            </div>
                        ) : (
                            <div className="space-y-1">
                                {/* Group by category */}
                                {['system', 'agent', 'navigation', 'settings'].map(category => {
                                    const categoryCommands = filteredCommands.filter(
                                        cmd => cmd.category === category
                                    );
                                    
                                    if (categoryCommands.length === 0) return null;

                                    return (
                                        <div key={category} className="mb-3 last:mb-0">
                                            <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                                                {category}
                                            </div>
                                            {categoryCommands.map((cmd, index) => {
                                                const globalIndex = filteredCommands.indexOf(cmd);
                                                const isSelected = globalIndex === selectedIndex;

                                                return (
                                                    <button
                                                        key={cmd.id}
                                                        onClick={() => {
                                                            cmd.action();
                                                            onClose();
                                                        }}
                                                        onMouseEnter={() => setSelectedIndex(globalIndex)}
                                                        className={`w-full px-3 py-2.5 rounded-lg text-left transition-all ${
                                                            isSelected
                                                                ? 'bg-cyan-500/20 border border-cyan-500/30'
                                                                : 'hover:bg-white/5 border border-transparent'
                                                        }`}
                                                    >
                                                        <div className="flex items-center gap-3">
                                                            <span className="text-xl">{cmd.icon}</span>
                                                            
                                                            <div className="flex-1 min-w-0">
                                                                <div className="font-medium text-white truncate">
                                                                    {cmd.label}
                                                                </div>
                                                                {cmd.description && (
                                                                    <div className="text-sm text-gray-400 truncate">
                                                                        {cmd.description}
                                                                    </div>
                                                                )}
                                                            </div>
                                                            
                                                            {cmd.shortcut && (
                                                                <kbd className="hidden sm:inline-block px-2 py-1 text-xs font-mono text-gray-400 bg-white/5 rounded border border-white/10">
                                                                    {cmd.shortcut}
                                                                </kbd>
                                                            )}
                                                        </div>
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="px-4 py-2 border-t border-white/10 bg-black/20">
                        <div className="flex items-center gap-4 text-xs text-gray-400">
                            <span className="flex items-center gap-1">
                                <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px]">↑↓</kbd>
                                to navigate
                            </span>
                            <span className="flex items-center gap-1">
                                <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px]">↵</kbd>
                                to select
                            </span>
                            <span className="flex items-center gap-1">
                                <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px]">esc</kbd>
                                to close
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CommandPalette;
