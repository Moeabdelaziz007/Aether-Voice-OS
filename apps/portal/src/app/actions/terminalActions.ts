'use client';

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
    const logs: { level: any; message: string }[] = [];
    try {
        logs.push({ level: 'VOICE', message: userInput });

        // Simulate system processing
        await new Promise(resolve => setTimeout(resolve, 100));
        logs.push({
            level: 'SYS',
            message: `Processing with ${personaConfig?.tone || 'analytical'} ${personaConfig?.formality || 'formal'} persona...`
        });

        // Simulate skill sync if needed
        if (activeSkills && activeSkills.length > 0) {
            await new Promise(resolve => setTimeout(resolve, 50));
            logs.push({
                level: 'SKILLS',
                message: `Syncing active skills: [${activeSkills.join(', ')}]...`
            });
        }

        // Simulate agent response
        await new Promise(resolve => setTimeout(resolve, 300));
        logs.push({ level: 'AGENT', message: `Responding to: "${userInput}"` });
        logs.push({ level: 'SUCCESS', message: 'Command executed successfully' });

        return {
            success: true,
            logs,
            message: 'Intent processed',
        };
    } catch (error) {
        return {
            success: false,
            logs: [{ level: 'ERROR', message: `Failed to process intent: ${String(error)}` }],
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
