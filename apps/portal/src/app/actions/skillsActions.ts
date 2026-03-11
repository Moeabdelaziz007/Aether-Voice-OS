'use client';

import { useAetherStore } from '@/store/useAetherStore';
import type { Skill } from '@/store/useAetherStore';

// Mock skills data
const MOCK_SKILLS: Skill[] = [
    { id: 'coding', name: 'Coding Assistant', enabled: true, description: 'Code completion & debugging' },
    { id: 'debug', name: 'Debugger', enabled: true, description: 'Error diagnosis & fixes' },
    { id: 'arch', name: 'Architecture', enabled: false, description: 'System design guidance' },
    { id: 'devops', name: 'DevOps', enabled: false, description: 'Deployment & infrastructure' },
];

/**
 * Sync skills from clawhib.ai with 800ms timeout
 * Falls back to localStorage cached skills if timeout exceeded
 * Implements graceful degradation for zero-latency perception
 */
export async function syncSkillsWithFallback() {
    const store = useAetherStore.getState();
    
    try {
        store.setSkillsSyncStatus('syncing');
        store.addTerminalLog('SYS', 'Syncing with clawhib.ai...');

        // Create abort controller for 800ms timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 800);

        try {
            // In production, this would call actual clawhib.ai API
            // For now, simulate with mock data
            const response = await Promise.race([
                new Promise<Skill[]>((resolve) => {
                    // Simulate API delay (intentionally set to exceed 800ms in fallback scenario)
                    setTimeout(() => {
                        resolve(MOCK_SKILLS);
                    }, 200); // Normally quick, but can be configured
                }),
                new Promise<Skill[]>((_, reject) => {
                    setTimeout(() => reject(new Error('Timeout')), 800);
                }),
            ]);

            clearTimeout(timeoutId);

            // Success: Update store with fetched skills + cache
            store.setActiveSkills(response);
            store.setCachedSkills(response);
            store.setSkillsSyncStatus('success');
            store.addTerminalLog('SYS', 'clawhib.ai sync successful [SUCCESS]');

            return { success: true, skills: response, source: 'live' };
        } catch (timeoutError) {
            clearTimeout(timeoutId);

            // Timeout exceeded: Use cached skills
            store.setSkillsSyncStatus('cached');
            const cachedSkills = store.cachedSkills.length > 0 ? store.cachedSkills : MOCK_SKILLS;
            store.setActiveSkills(cachedSkills);
            store.addTerminalLog(
                'SYS',
                'clawhib.ai sync delayed. Using local cached skills. [OK]'
            );

            return { success: true, skills: cachedSkills, source: 'cached' };
        }
    } catch (error) {
        store.setSkillsSyncStatus('failed');
        
        // Final fallback: use whatever we have in cache
        const cachedSkills = store.cachedSkills.length > 0 ? store.cachedSkills : MOCK_SKILLS;
        store.setActiveSkills(cachedSkills);
        store.addTerminalLog('SYS', `Skills sync failed, using cache: ${String(error)}`);

        return { success: false, error: String(error), skills: cachedSkills, source: 'cache_fallback' };
    }
}

/**
 * Toggle skill enabled/disabled state
 */
export async function toggleSkill(skillId: string) {
    try {
        useAetherStore.getState().toggleSkill(skillId);
        useAetherStore.getState().addTerminalLog('SKILLS', `Skill ${skillId} toggled`);
        return { success: true };
    } catch (error) {
        useAetherStore.getState().addTerminalLog('ERROR', `Failed to toggle skill: ${String(error)}`);
        return { success: false, error: String(error) };
    }
}

/**
 * Get active skills (can be called to refresh UI)
 */
export async function getActiveSkills() {
    return useAetherStore.getState().activeSkills;
}

/**
 * Initialize skills on app load
 * Performs initial sync with fallback
 */
export async function initializeSkills() {
    return syncSkillsWithFallback();
}
