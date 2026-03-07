'use client';

import React, { useState } from 'react';
import { useAetherStore } from '@/store/useAetherStore';
import { updatePersona, PERSONA_PRESETS } from '@/app/actions/personaActions';

/**
 * PersonaConfigWidget — High-tech parameter tuning interface
 * Allows adjusting tone, formality, verbosity with real-time preview
 * Shows live system prompt updates in terminal
 */
export function PersonaConfigWidget() {
    const personaConfig = useAetherStore((s) => s.personaConfig);
    const [isUpdating, setIsUpdating] = useState(false);

    const handleConfigChange = async (key: string, value: string) => {
        setIsUpdating(true);
        const updates = { ...personaConfig, [key]: value };
        await updatePersona(updates);
        setIsUpdating(false);
    };

    const applyPreset = async (presetKey: keyof typeof PERSONA_PRESETS) => {
        setIsUpdating(true);
        const preset = PERSONA_PRESETS[presetKey];
        await updatePersona(preset);
        setIsUpdating(false);
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
            <div style={{ marginBottom: '1rem' }}>
                <span style={{ color: 'var(--log-persona)', fontWeight: 600, fontSize: '0.9rem' }}>
                    PERSONA CONFIG
                </span>
            </div>

            {/* Presets */}
            <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
                    Quick Presets:
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {Object.entries(PERSONA_PRESETS).map(([key, _]) => (
                        <button
                            key={key}
                            onClick={() => applyPreset(key as keyof typeof PERSONA_PRESETS)}
                            disabled={isUpdating}
                            style={{
                                padding: '0.4rem 0.8rem',
                                background: 'rgba(255,255,255,0.05)',
                                border: '1px solid rgba(255,255,255,0.15)',
                                borderRadius: '4px',
                                color: 'var(--text-secondary)',
                                fontSize: '0.75rem',
                                cursor: isUpdating ? 'not-allowed' : 'pointer',
                                transition: 'all 0.2s ease',
                                opacity: isUpdating ? 0.5 : 1,
                            }}
                            onMouseEnter={(e) => {
                                if (!isUpdating) e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                            }}
                        >
                            {key.replace(/_/g, ' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Configuration sliders */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {/* Tone */}
                <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                        Tone:
                        <span style={{ color: 'var(--log-persona)', marginLeft: '0.5rem', fontWeight: 600 }}>
                            {personaConfig.tone.toUpperCase()}
                        </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {['analytical', 'creative', 'neutral'].map((tone) => (
                            <button
                                key={tone}
                                onClick={() => handleConfigChange('tone', tone)}
                                disabled={isUpdating}
                                style={{
                                    flex: 1,
                                    padding: '0.5rem',
                                    background: personaConfig.tone === tone ? 'rgba(251, 113, 133, 0.2)' : 'rgba(255,255,255,0.05)',
                                    border: personaConfig.tone === tone ? '1px solid rgba(251, 113, 133, 0.5)' : '1px solid rgba(255,255,255,0.15)',
                                    borderRadius: '4px',
                                    color: personaConfig.tone === tone ? 'var(--log-persona)' : 'var(--text-secondary)',
                                    fontSize: '0.75rem',
                                    cursor: isUpdating ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.2s ease',
                                    opacity: isUpdating ? 0.5 : 1,
                                }}
                            >
                                {tone}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Formality */}
                <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                        Formality:
                        <span style={{ color: 'var(--log-persona)', marginLeft: '0.5rem', fontWeight: 600 }}>
                            {personaConfig.formality.toUpperCase()}
                        </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {['formal', 'casual', 'technical'].map((formality) => (
                            <button
                                key={formality}
                                onClick={() => handleConfigChange('formality', formality)}
                                disabled={isUpdating}
                                style={{
                                    flex: 1,
                                    padding: '0.5rem',
                                    background: personaConfig.formality === formality ? 'rgba(251, 113, 133, 0.2)' : 'rgba(255,255,255,0.05)',
                                    border: personaConfig.formality === formality ? '1px solid rgba(251, 113, 133, 0.5)' : '1px solid rgba(255,255,255,0.15)',
                                    borderRadius: '4px',
                                    color: personaConfig.formality === formality ? 'var(--log-persona)' : 'var(--text-secondary)',
                                    fontSize: '0.75rem',
                                    cursor: isUpdating ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.2s ease',
                                    opacity: isUpdating ? 0.5 : 1,
                                }}
                            >
                                {formality}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Verbosity */}
                <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                        Verbosity:
                        <span style={{ color: 'var(--log-persona)', marginLeft: '0.5rem', fontWeight: 600 }}>
                            {personaConfig.verbosity.toUpperCase()}
                        </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {['concise', 'balanced', 'verbose'].map((verbosity) => (
                            <button
                                key={verbosity}
                                onClick={() => handleConfigChange('verbosity', verbosity)}
                                disabled={isUpdating}
                                style={{
                                    flex: 1,
                                    padding: '0.5rem',
                                    background: personaConfig.verbosity === verbosity ? 'rgba(251, 113, 133, 0.2)' : 'rgba(255,255,255,0.05)',
                                    border: personaConfig.verbosity === verbosity ? '1px solid rgba(251, 113, 133, 0.5)' : '1px solid rgba(255,255,255,0.15)',
                                    borderRadius: '4px',
                                    color: personaConfig.verbosity === verbosity ? 'var(--log-persona)' : 'var(--text-secondary)',
                                    fontSize: '0.75rem',
                                    cursor: isUpdating ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.2s ease',
                                    opacity: isUpdating ? 0.5 : 1,
                                }}
                            >
                                {verbosity}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Status */}
            <div style={{ marginTop: '1rem', fontSize: '0.7rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                {isUpdating ? 'Updating persona...' : 'Changes applied in real-time'}
            </div>
        </div>
    );
}
