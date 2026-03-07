/**
 * useAetherStore — Real Unit Tests.
 *
 * Tests the Zustand store directly (no mocks needed — it's pure state logic).
 * Covers: silentHints CRUD, visionActive toggle, transcript, system logs.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useAetherStore } from '@/store/useAetherStore';

// Reset store between tests
beforeEach(() => {
    const store = useAetherStore.getState();
    store.setStatus('disconnected');
    store.setEngineState('IDLE');
    store.setVisionActive(false);
    store.clearTranscript();
    store.clearMissionLog();
    store.clearOrbitRegistry();
    store.clearPlanetNotes();
    store.clearMirrorFrameEvents();
    store.clearVoyagerLatencyRows();
    store.setFocusModeEnvironment(false);
    store.setOrbitalLayoutPreset('mid');
    store.focusOrbitPlanet(null);
    store.setWorkspaceGalaxy('Genesis');
    store.setTaskPulse(null);
    store.setSessionStartTime(null);
    store.setPreferences({ compactMissionHud: false, lowMotionMode: false });
    // Clear silent hints by dismissing all
    store.silentHints.forEach(h => store.dismissHint(h.id));
});

describe('useAetherStore', () => {
    // ─── Connection State ───────────────────────────────────────
    it('should initialize with disconnected status', () => {
        const state = useAetherStore.getState();
        expect(state.status).toBe('disconnected');
        expect(state.engineState).toBe('IDLE');
    });

    it('should transition through connection states', () => {
        const store = useAetherStore.getState();

        store.setStatus('connecting');
        expect(useAetherStore.getState().status).toBe('connecting');

        store.setStatus('listening');
        expect(useAetherStore.getState().status).toBe('listening');

        store.setEngineState('LISTENING');
        expect(useAetherStore.getState().engineState).toBe('LISTENING');

        store.setStatus('speaking');
        store.setEngineState('SPEAKING');
        expect(useAetherStore.getState().status).toBe('speaking');
        expect(useAetherStore.getState().engineState).toBe('SPEAKING');
    });

    // ─── Silent Hints (V3 Feature) ──────────────────────────────
    it('should add a silent hint', () => {
        const store = useAetherStore.getState();

        store.addSilentHint({
            id: 'hint-1',
            text: 'You have an unused import on line 5',
            priority: 'suggestion',
            type: 'hint',
            timestamp: Date.now(),
        });

        const hints = useAetherStore.getState().silentHints;
        expect(hints).toHaveLength(1);
        expect(hints[0].text).toBe('You have an unused import on line 5');
        expect(hints[0].priority).toBe('suggestion');
    });

    it('should add a code suggestion hint', () => {
        const store = useAetherStore.getState();

        store.addSilentHint({
            id: 'code-1',
            text: 'Missing semicolon',
            code: 'const x = 42;',
            explanation: 'Add semicolon after variable declaration',
            priority: 'warning',
            type: 'code',
            timestamp: Date.now(),
        });

        const hints = useAetherStore.getState().silentHints;
        expect(hints).toHaveLength(1);
        expect(hints[0].type).toBe('code');
        expect(hints[0].code).toBe('const x = 42;');
        expect(hints[0].explanation).toBe('Add semicolon after variable declaration');
    });

    it('should dismiss a hint by id', () => {
        const store = useAetherStore.getState();

        store.addSilentHint({
            id: 'hint-to-dismiss',
            text: 'Test hint',
            priority: 'info',
            type: 'hint',
            timestamp: Date.now(),
        });

        expect(useAetherStore.getState().silentHints).toHaveLength(1);

        store.dismissHint('hint-to-dismiss');
        expect(useAetherStore.getState().silentHints).toHaveLength(0);
    });

    it('should keep only last 10 hints', () => {
        const store = useAetherStore.getState();

        for (let i = 0; i < 15; i++) {
            store.addSilentHint({
                id: `hint-${i}`,
                text: `Hint ${i}`,
                priority: 'info',
                type: 'hint',
                timestamp: Date.now(),
            });
        }

        const hints = useAetherStore.getState().silentHints;
        expect(hints).toHaveLength(10);
        // Should keep the LAST 10 (ids 5-14)
        expect(hints[0].id).toBe('hint-5');
        expect(hints[9].id).toBe('hint-14');
    });

    // ─── Vision Active (V3 Feature) ─────────────────────────────
    it('should toggle vision active state', () => {
        const store = useAetherStore.getState();

        expect(store.visionActive).toBe(false);

        store.setVisionActive(true);
        expect(useAetherStore.getState().visionActive).toBe(true);

        store.setVisionActive(false);
        expect(useAetherStore.getState().visionActive).toBe(false);
    });

    // ─── Transcript ─────────────────────────────────────────────
    it('should add transcript messages with auto-generated id and timestamp', () => {
        const store = useAetherStore.getState();

        store.addTranscriptMessage({ role: 'user', content: 'Hello Aether' });
        store.addTranscriptMessage({ role: 'agent', content: 'Hello! How can I help?' });

        const transcript = useAetherStore.getState().transcript;
        expect(transcript).toHaveLength(2);
        expect(transcript[0].role).toBe('user');
        expect(transcript[0].content).toBe('Hello Aether');
        expect(transcript[0].id).toBeDefined();
        expect(transcript[0].timestamp).toBeGreaterThan(0);
        expect(transcript[1].role).toBe('agent');
    });

    it('should clear transcript', () => {
        const store = useAetherStore.getState();
        store.addTranscriptMessage({ role: 'user', content: 'Test' });
        expect(useAetherStore.getState().transcript).toHaveLength(1);

        store.clearTranscript();
        expect(useAetherStore.getState().transcript).toHaveLength(0);
    });

    // ─── System Logs ────────────────────────────────────────────
    it('should add system logs and cap at 50', () => {
        const store = useAetherStore.getState();

        for (let i = 0; i < 60; i++) {
            store.addSystemLog(`Log ${i}`);
        }

        const logs = useAetherStore.getState().systemLogs;
        expect(logs).toHaveLength(50);
        expect(logs[0]).toBe('Log 10');
        expect(logs[49]).toBe('Log 59');
    });

    // ─── Audio Levels ───────────────────────────────────────────
    it('should set audio levels', () => {
        const store = useAetherStore.getState();

        store.setAudioLevels(0.5, 0.8);
        const state = useAetherStore.getState();
        expect(state.micLevel).toBe(0.5);
        expect(state.speakerLevel).toBe(0.8);
    });

    // ─── Latency ────────────────────────────────────────────────
    it('should set latency', () => {
        const store = useAetherStore.getState();

        store.setLatencyMs(142);
        expect(useAetherStore.getState().latencyMs).toBe(142);
    });

    it('should persist cinematic avatar and mission signals', () => {
        const store = useAetherStore.getState();

        store.setWorkspaceGalaxy('gal-test');
        store.setAvatarCinematicState('EUREKA');
        store.setTaskPulse({
            taskId: 'task-777',
            phase: 'COMPLETED',
            action: 'verify_handover',
            vibe: 'success',
            thought: 'Validation path confirmed',
            intensity: 0.9,
            timestamp: Date.now(),
        });
        store.pushMissionLog({
            taskId: 'task-777',
            title: 'Handover completed',
            detail: 'Debugger confirmed final route',
            status: 'completed',
        });

        const state = useAetherStore.getState();
        expect(state.workspaceGalaxy).toBe('gal-test');
        expect(state.avatarCinematicState).toBe('EUREKA');
        expect(state.taskPulse?.phase).toBe('COMPLETED');
        expect(state.missionLog.length).toBeGreaterThan(0);
        expect(state.missionLog[state.missionLog.length - 1].title).toBe('Handover completed');
    });

    it('should apply workspace state updates into orbital registry', () => {
        const store = useAetherStore.getState();

        store.applyWorkspaceState({
            workspace_galaxy: 'gal-orbit',
            action: 'materialize_app',
            app_id: 'planet-notes',
            x: 140,
            y: 20,
            orbit_lane: 'mid',
        });
        store.applyWorkspaceState({
            action: 'focus_app',
            app_id: 'planet-notes',
            focused_app_id: 'planet-notes',
        });
        store.applyWorkspaceState({
            action: 'move_app',
            app_id: 'planet-notes',
            x: 80,
            y: 90,
        });

        const state = useAetherStore.getState();
        expect(state.workspaceGalaxy).toBe('gal-orbit');
        expect(state.focusedPlanetId).toBe('planet-notes');
        expect(state.focusModeEnvironment).toBe(true);
        expect(state.orbitRegistry['planet-notes']).toBeDefined();
        expect(state.orbitRegistry['planet-notes'].position.x).toBe(80);
        expect(state.orbitRegistry['planet-notes'].position.y).toBe(90);
        expect(state.orbitalLayoutPreset).toBe('mid');
    });

    it('should create update and delete notes planet entries', () => {
        const store = useAetherStore.getState();
        store.setTaskPulse({
            taskId: 'task-notes',
            phase: 'EXECUTING',
            action: 'draft_plan',
            vibe: 'typing',
            intensity: 0.6,
            timestamp: Date.now(),
        });
        store.setSessionStartTime(123456);

        const noteId = store.createPlanetNote({
            content: 'First crystal note',
            tag: 'research',
            taskId: 'task-notes',
            sessionId: '123456',
        });
        let state = useAetherStore.getState();
        expect(state.notesPlanet.length).toBe(1);
        expect(state.notesPlanet[0].taskId).toBe('task-notes');
        expect(state.notesPlanet[0].sessionId).toBe('123456');

        store.updatePlanetNote(noteId, { content: 'Updated crystal note' });
        state = useAetherStore.getState();
        expect(state.notesPlanet[0].content).toBe('Updated crystal note');

        store.deletePlanetNote(noteId);
        state = useAetherStore.getState();
        expect(state.notesPlanet.length).toBe(0);
    });

    // ─── Session Time ───────────────────────────────────────────
    it('should track session start time', () => {
        const store = useAetherStore.getState();
        const now = Date.now();

        store.setSessionStartTime(now);
        expect(useAetherStore.getState().sessionStartTime).toBe(now);

        store.setSessionStartTime(null);
        expect(useAetherStore.getState().sessionStartTime).toBeNull();
    });

    it('should append mirror frame events and voyager latency rows', () => {
        const store = useAetherStore.getState();
        store.addMirrorFrameEvent({
            action: 'click',
            eventKind: 'click',
            selector: '#run',
            latencyMs: 33,
        });
        store.pushVoyagerLatencyRow({
            label: 'click:run',
            latencyMs: 33,
            status: 'ok',
        });

        const state = useAetherStore.getState();
        expect(state.mirrorFrames.length).toBe(1);
        expect(state.voyagerLatencyRows.length).toBe(1);
        expect(state.mirrorFrames[0].eventKind).toBe('click');
    });

    it('should update cinematic preference toggles', () => {
        const store = useAetherStore.getState();
        store.setPreferences({ compactMissionHud: true, lowMotionMode: true });
        const state = useAetherStore.getState();
        expect(state.preferences.compactMissionHud).toBe(true);
        expect(state.preferences.lowMotionMode).toBe(true);
    });
});
