'use client';

import React, { useEffect } from 'react';
import { useAetherStore } from '@/store/useAetherStore';
import { syncSkillsWithFallback, toggleSkill } from '@/app/actions/skillsActions';

/**
 * SkillsManagerWidget — Terminal-style toggle interface for skill management
 * Syncs with clawhib.ai API (with 800ms timeout + graceful fallback)
 * Displays active/offline skills as toggleable items
 */
export function SkillsManagerWidget() {
    const activeSkills = useAetherStore((s) => s.activeSkills);
    const skillsSyncStatus = useAetherStore((s) => s.skillsSyncStatus);
    const [isLoading, setIsLoading] = React.useState(false);

    // Initialize skills on mount
    useEffect(() => {
        const initializeSkills = async () => {
            setIsLoading(true);
            await syncSkillsWithFallback();
            setIsLoading(false);
        };
        initializeSkills();
    }, []);

    const handleToggleSkill = async (skillId: string) => {
        await toggleSkill(skillId);
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
            <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--log-skills)', fontWeight: 600, fontSize: '0.9rem' }}>
                    SKILLS MANAGER
                </span>
                <span style={{
                    fontSize: '0.75rem',
                    color: skillsSyncStatus === 'success' ? 'var(--log-success)' :
                           skillsSyncStatus === 'cached' ? 'var(--log-voice)' :
                           skillsSyncStatus === 'syncing' ? 'var(--log-sys)' : 'var(--log-error)',
                }}>
                    [{skillsSyncStatus.toUpperCase()}]
                </span>
            </div>

            {/* Skills list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {isLoading ? (
                    <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
                        Syncing skills...
                    </div>
                ) : activeSkills.length === 0 ? (
                    <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
                        No skills available.
                    </div>
                ) : (
                    activeSkills.map((skill) => (
                        <div
                            key={skill.id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem',
                                padding: '0.5rem',
                                cursor: 'pointer',
                                borderRadius: '4px',
                                background: 'transparent',
                                transition: 'background 0.2s ease',
                            }}
                            onClick={() => handleToggleSkill(skill.id)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.background = 'transparent';
                            }}
                        >
                            {/* Checkbox */}
                            <span style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '16px',
                                height: '16px',
                                border: '1px solid ' + (skill.enabled ? 'var(--log-success)' : 'rgba(255,255,255,0.3)'),
                                borderRadius: '2px',
                                background: skill.enabled ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                                color: 'var(--log-success)',
                                fontSize: '0.7rem',
                                fontWeight: 'bold',
                            }}>
                                {skill.enabled ? '✓' : ''}
                            </span>

                            {/* Skill name */}
                            <span style={{
                                color: skill.enabled ? 'var(--text-primary)' : 'var(--text-secondary)',
                                flex: 1,
                            }}>
                                {skill.name}
                            </span>

                            {/* Status badge */}
                            <span style={{
                                fontSize: '0.7rem',
                                color: skill.enabled ? 'var(--log-success)' : 'var(--text-dim)',
                            }}>
                                {skill.enabled ? '◆' : '◇'}
                            </span>
                        </div>
                    ))
                )}
            </div>

            {/* Footer note */}
            <div style={{ marginTop: '1rem', fontSize: '0.7rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                {skillsSyncStatus === 'cached' && 'Using cached skills (offline)'}
                {skillsSyncStatus === 'success' && 'Skills synchronized with clawhib.ai'}
                {skillsSyncStatus === 'failed' && 'Failed to sync skills'}
            </div>
        </div>
    );
}
