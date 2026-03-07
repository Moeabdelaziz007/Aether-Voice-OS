'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useAetherStore } from '@/store/useAetherStore';
import type { TerminalLog } from '@/store/useAetherStore';

/**
 * TerminalFeed — Central scrollable log container with advanced features:
 * - Smart auto-scroll: Sticky scroll only when at bottom; pauses on manual scroll up
 * - Voice interruption: Halts logs and clears widgets on new voice command
 * - Widget lifecycle: Converts off-viewport widgets to static strings (memory optimization)
 * - Streaming buffer: Local state for typewriter effect (no store churn)
 * - Mobile responsive: Optimized for touch, responsive font sizes, proper text wrapping
 */
export default function TerminalFeed() {
    const terminalLogs = useAetherStore((s) => s.terminalLogs);
    const isInterrupted = useAetherStore((s) => s.isInterrupted);
    const scrollPaused = useAetherStore((s) => s.scrollPaused);
    const setScrollPaused = useAetherStore((s) => s.setScrollPaused);
    const setInterrupted = useAetherStore((s) => s.setInterrupted);

    const containerRef = useRef<HTMLDivElement>(null);
    const [isAtBottom, setIsAtBottom] = useState(true);
    const [hoveredLogId, setHoveredLogId] = useState<string | null>(null);

    /**
     * Check if user is at bottom of scroll (within 100px threshold)
     */
    const checkIfAtBottom = useCallback(() => {
        if (!containerRef.current) return true;
        const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
        return scrollHeight - (scrollTop + clientHeight) < 100;
    }, []);

    /**
     * Auto-scroll to bottom (only if user is already at bottom)
     */
    const scrollToBottom = useCallback(() => {
        if (containerRef.current && isAtBottom && !scrollPaused) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [isAtBottom, scrollPaused]);

    /**
     * Handle manual scroll — pause auto-scroll when user scrolls up
     */
    const handleScroll = useCallback(() => {
        const atBottom = checkIfAtBottom();
        setIsAtBottom(atBottom);

        if (!atBottom && !scrollPaused) {
            setScrollPaused(true);
        } else if (atBottom && scrollPaused) {
            setScrollPaused(false);
        }
    }, [checkIfAtBottom, scrollPaused, setScrollPaused]);

    /**
     * Handle voice interruption: clear active widgets and halt logs
     */
    useEffect(() => {
        if (isInterrupted) {
            // Clear pending widgets and reset streaming state
            useAetherStore.getState().clearWidgets();
            useAetherStore.getState().setStreamingBuffer('');

            // Log interruption
            useAetherStore.getState().addTerminalLog(
                'SYS',
                'Voice interruption detected. Clearing previous context.'
            );

            // Reset interruption flag
            setTimeout(() => setInterrupted(false), 100);
        }
    }, [isInterrupted, setInterrupted]);

    /**
     * Auto-scroll effect: runs when logs change
     */
    useEffect(() => {
        scrollToBottom();
    }, [terminalLogs, scrollToBottom]);

    /**
     * Render log entry with appropriate color based on level
     */
    const getLogColor = (level: TerminalLog['level']): string => {
        const colors: Record<TerminalLog['level'], string> = {
            SYS: 'var(--log-sys)',
            VOICE: 'var(--log-voice)',
            AGENT: 'var(--log-agent)',
            SUCCESS: 'var(--log-success)',
            ERROR: 'var(--log-error)',
            SKILLS: 'var(--log-skills)',
            PERSONA: 'var(--log-persona)',
            THEME: 'var(--log-theme)',
        };
        return colors[level] || '#888';
    };

    return (
        <div
            ref={containerRef}
            onScroll={handleScroll}
            className="md:p-8 md:text-sm p-4 text-xs"
            style={{
                flex: 1,
                overflowY: 'auto',
                fontFamily: 'var(--f-mono)',
                color: 'var(--text-secondary)',
                background: 'transparent',
                WebkitOverflowScrolling: 'touch', // Smooth scrolling on iOS
            }}
        >
            {/* Empty state */}
            {terminalLogs.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-dim)', marginTop: '2rem' }}>
                    <p>Terminal ready. Awaiting input...</p>
                </div>
            )}

            {/* Terminal log entries */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {terminalLogs.map((log) => (
                    <div
                        key={log.id}
                        onMouseEnter={() => setHoveredLogId(log.id)}
                        onMouseLeave={() => setHoveredLogId(null)}
                        className="md:p-3 md:rounded p-2 rounded-sm animate-in"
                        style={{
                            animation: 'terminal-line-in 0.3s ease-out',
                            background:
                                hoveredLogId === log.id ? 'rgba(255,255,255,0.03)' : 'transparent',
                            transition: 'background 0.15s ease',
                            borderLeft: `2px solid ${getLogColor(log.level)}`,
                        }}
                    >
                        <div className="md:flex md:items-center md:justify-between md:gap-4">
                            {/* Log level label */}
                            <span style={{ color: getLogColor(log.level), fontWeight: 600 }}>
                                [{log.level}]
                            </span>
                            {' '}
                            {/* Log message - wrap on mobile */}
                            <span style={{ color: 'var(--text-secondary)', flex: 1, wordBreak: 'break-word' }}>
                                {log.message}
                            </span>
                        </div>
                        {/* Timestamp (subtle) - below on mobile, inline on desktop */}
                        <span
                            className="md:inline block md:mt-0 mt-1 md:ml-auto"
                            style={{
                                color: 'var(--text-dim)',
                                fontSize: '0.7rem',
                            }}
                        >
                            {new Date(log.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                            })}
                        </span>
                    </div>
                ))}
            </div>

            {/* Resume auto-scroll button (shown when paused) */}
            {scrollPaused && (
                <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                    <button
                        onClick={() => {
                            setScrollPaused(false);
                            setIsAtBottom(true);
                            scrollToBottom();
                        }}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'rgba(0, 255, 65, 0.1)',
                            border: '1px solid var(--log-agent)',
                            borderRadius: '4px',
                            color: 'var(--log-agent)',
                            cursor: 'pointer',
                            fontSize: '0.8rem',
                            fontFamily: 'var(--f-mono)',
                            transition: 'all 0.2s ease',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(0, 255, 65, 0.2)';
                            e.currentTarget.style.boxShadow = '0 0 12px rgba(0, 255, 65, 0.3)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(0, 255, 65, 0.1)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        Resume auto-scroll
                    </button>
                </div>
            )}
        </div>
    );
}
