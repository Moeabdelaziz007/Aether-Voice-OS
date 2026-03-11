'use client';

import { useAetherStore } from '@/store/useAetherStore';
import type { PersonaConfig } from '@/store/useAetherStore';

/**
 * Build system prompt based on persona configuration
 * This is what gets sent to the LLM backend for instruction tuning
 */
export async function buildSystemPrompt(personaConfig: PersonaConfig): Promise<string> {
    const toneInstructions: Record<string, string> = {
        analytical: 'Approach problems systematically. Prioritize logic and evidence.',
        creative: 'Think outside the box. Explore novel solutions and perspectives.',
        neutral: 'Provide balanced, objective information without bias.',
    };

    const formalityInstructions: Record<string, string> = {
        formal: 'Use professional language. Maintain distance and formality.',
        casual: 'Be conversational and friendly. Use natural language.',
        technical: 'Use technical jargon appropriately. Assume some expertise.',
    };

    const verbosityInstructions: Record<string, string> = {
        concise: 'Keep responses brief. One sentence unless asked for more.',
        balanced: 'Balance brevity with clarity. Standard response length.',
        verbose: 'Provide detailed explanations. Include context and reasoning.',
    };

    const systemPrompt = `
You are an AI assistant with the following characteristics:
- Tone: ${toneInstructions[personaConfig.tone]}
- Formality: ${formalityInstructions[personaConfig.formality]}
- Verbosity: ${verbosityInstructions[personaConfig.verbosity]}
${personaConfig.customPrompt ? `- Custom instructions: ${personaConfig.customPrompt}` : ''}

Respond according to these guidelines in all interactions.
`.trim();

    return systemPrompt;
}

/**
 * Update persona configuration and log change to terminal
 */
export async function updatePersona(personaConfig: Partial<PersonaConfig>) {
    try {
        const store = useAetherStore.getState();
        const updated = { ...store.personaConfig, ...personaConfig };
        
        store.setPersonaConfig(updated);

        // Log persona change
        const desc = `${updated.tone} ${updated.formality}, ${updated.verbosity}`;
        store.addTerminalLog('PERSONA', `Updated to: ${desc}`);

        // Build and return new system prompt for backend
        const systemPrompt = await buildSystemPrompt(updated);

        return {
            success: true,
            personaConfig: updated,
            systemPrompt,
        };
    } catch (error) {
        useAetherStore.getState().addTerminalLog(
            'ERROR',
            `Failed to update persona: ${String(error)}`
        );
        return {
            success: false,
            error: String(error),
        };
    }
}

/**
 * Get current persona configuration
 */
export async function getPersonaConfig() {
    return useAetherStore.getState().personaConfig;
}

/**
 * Get current system prompt
 */
export async function getSystemPrompt() {
    const personaConfig = useAetherStore.getState().personaConfig;
    return await buildSystemPrompt(personaConfig);
}

/**
 * Preset personas for quick switching
 */
export const PERSONA_PRESETS = {
    analytical_engineer: {
        tone: 'analytical' as const,
        formality: 'technical' as const,
        verbosity: 'balanced' as const,
        customPrompt: 'Focus on technical details and system design.',
    },
    friendly_mentor: {
        tone: 'creative' as const,
        formality: 'casual' as const,
        verbosity: 'verbose' as const,
        customPrompt: 'Explain concepts thoroughly. Be encouraging and patient.',
    },
    concise_assistant: {
        tone: 'neutral' as const,
        formality: 'formal' as const,
        verbosity: 'concise' as const,
        customPrompt: 'Minimize response length while maintaining clarity.',
    },
} as const;

/**
 * Apply a preset persona
 */
export async function applyPersonaPreset(presetKey: keyof typeof PERSONA_PRESETS) {
    return updatePersona(PERSONA_PRESETS[presetKey]);
}
