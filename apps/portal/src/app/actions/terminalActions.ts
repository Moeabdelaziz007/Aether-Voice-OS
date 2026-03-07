'use server';

import { useAetherStore } from '@/store/useAetherStore';

/**
 * Process user intent and stream response logs to terminal feed
 * Handles mock agent processing with realistic delay simulation
 */
export async function processIntent(
    userInput: string,
    personaConfig?: { tone: string; formality: string; verbosity: string },
    activeSkills?: string[]
) {
    try {
        // Add voice log entry
        useAetherStore.getState().addTerminalLog('VOICE', userInput);

        // Simulate system processing
        await new Promise(resolve => setTimeout(resolve, 100));
        useAetherStore.getState().addTerminalLog(
            'SYS',
            `Processing with ${personaConfig?.tone || 'analytical'} ${personaConfig?.formality || 'formal'} persona...`
        );

        // Simulate skill sync if needed
        if (activeSkills && activeSkills.length > 0) {
            await new Promise(resolve => setTimeout(resolve, 50));
            useAetherStore.getState().addTerminalLog(
                'SKILLS',
                `Syncing active skills: [${activeSkills.join(', ')}]...`
            );
        }

        // Simulate agent response (in production, this would call Gemini Live API)
        await new Promise(resolve => setTimeout(resolve, 300));
        useAetherStore.getState().addTerminalLog('AGENT', `Responding to: "${userInput}"`);
        useAetherStore.getState().addTerminalLog('SUCCESS', 'Command executed successfully');

        return {
            success: true,
            message: 'Intent processed',
        };
    } catch (error) {
        useAetherStore.getState().addTerminalLog('ERROR', `Failed to process intent: ${String(error)}`);
        return {
            success: false,
            error: String(error),
        };
    }
}

/**
 * Stream agent response with typewriter effect support
 * Simulates Gemini Live streaming by yielding characters one at a time
 */
export async function* streamAgentResponse(prompt: string) {
    const mockResponse = `This is a simulated response to: "${prompt}". In production, this would be a real Gemini Live API stream.`;
    
    for (const char of mockResponse) {
        yield char;
        // Add small delay for typewriter effect perception
        await new Promise(resolve => setTimeout(resolve, 10));
    }
}

/**
 * Add log entry to terminal feed
 * Can be called from client components via useTransition for optimistic updates
 */
export async function addTerminalLogAction(
    level: 'SYS' | 'VOICE' | 'AGENT' | 'SUCCESS' | 'ERROR' | 'SKILLS' | 'PERSONA' | 'THEME',
    message: string,
    widgetId?: string
) {
    useAetherStore.getState().addTerminalLog(level, message, widgetId);
}
