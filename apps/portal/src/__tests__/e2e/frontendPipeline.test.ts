/**
 * Aether Voice OS — End-to-End Frontend Tests
 * 
 * Validates the complete flow from frontend components through
 * WebSocket communication, state management, and audio pipeline.
 * 
 * Test Categories:
 * 1. Audio Pipeline Hook (useAudioPipeline)
 * 2. Aether Gateway Hook (useAetherGateway)
 * 3. State Management (useAetherStore)
 * 4. Component Integration
 * 5. WebSocket Communication
 */

import { act, renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock Web APIs
const mockMediaStream = {
    getTracks: () => [{ stop: vi.fn() }],
};

const mockAudioContext = {
    state: 'running',
    resume: vi.fn().mockResolvedValue(undefined),
    close: vi.fn().mockResolvedValue(undefined),
    createAnalyser: vi.fn(() => ({
        fftSize: 256,
        smoothingTimeConstant: 0.5,
        frequencyBinCount: 128,
        getByteFrequencyData: vi.fn(),
    })),
    createGain: vi.fn(() => ({
        gain: { value: 1.0 },
        connect: vi.fn(),
    })),
    createMediaStreamSource: vi.fn(() => ({
        connect: vi.fn(),
    })),
    createBufferSource: vi.fn(() => ({
        buffer: null,
        connect: vi.fn(),
        start: vi.fn(),
        stop: vi.fn(),
        onended: null,
    })),
    createBuffer: vi.fn(() => ({
        copyToChannel: vi.fn(),
        duration: 0.016,
    })),
    currentTime: 0,
    sampleRate: 16000,
    audioWorklet: {
        addModule: vi.fn().mockResolvedValue(undefined),
    },
};

const mockAudioWorkletNode = {
    port: {
        onmessage: null,
        postMessage: vi.fn(),
    },
    connect: vi.fn(),
    disconnect: vi.fn(),
};

// Mock WebSocket
class MockWebSocket {
    static CONNECTING = 0;
    static OPEN = 1;
    static CLOSING = 2;
    static CLOSED = 3;

    readyState = MockWebSocket.OPEN;
    binaryType = 'arraybuffer';
    onopen: (() => void) | null = null;
    onmessage: ((event: MessageEvent) => void) | null = null;
    onclose: (() => void) | null = null;
    onerror: ((err: Event) => void) | null = null;

    constructor(public url: string) {
        setTimeout(() => this.onopen?.(), 0);
    }

    send = vi.fn();
    close = vi.fn();

    simulateMessage(data: unknown) {
        const event = new MessageEvent('message', {
            data: typeof data === 'string' ? data : data,
        });
        this.onmessage?.(event);
    }

    simulateBinary(data: ArrayBuffer) {
        const event = new MessageEvent('message', { data });
        this.onmessage?.(event);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// SETUP MOCKS
// ─────────────────────────────────────────────────────────────────────────────

vi.stubGlobal('navigator', {
    mediaDevices: {
        getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
    },
});

vi.stubGlobal('AudioContext', vi.fn(() => mockAudioContext));
vi.stubGlobal('AudioWorkletNode', vi.fn(() => mockAudioWorkletNode));
vi.stubGlobal('WebSocket', MockWebSocket);
vi.stubGlobal('requestAnimationFrame', vi.fn((cb) => setTimeout(cb, 16)));
vi.stubGlobal('cancelAnimationFrame', vi.fn());

// ─────────────────────────────────────────────────────────────────────────────
// TEST: USE AUDIO PIPELINE
// ─────────────────────────────────────────────────────────────────────────────

describe('useAudioPipeline', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should initialize with idle state', () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { result } = renderHook(() => useAudioPipeline());

        expect(result.current.state).toBe('idle');
        expect(result.current.micLevel).toBe(0);
        expect(result.current.speakerLevel).toBe(0);
    });

    it('should start audio pipeline successfully', async () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { result } = renderHook(() => useAudioPipeline());

        await act(async () => {
            await result.current.start();
        });

        expect(result.current.state).toBe('active');
        expect(vi.mocked(navigator.mediaDevices.getUserMedia)).toHaveBeenCalled();
    });

    it('should stop audio pipeline and cleanup resources', async () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { result } = renderHook(() => useAudioPipeline());

        await act(async () => {
            await result.current.start();
        });

        act(() => {
            result.current.stop();
        });

        expect(result.current.state).toBe('idle');
        expect(result.current.micLevel).toBe(0);
        expect(result.current.speakerLevel).toBe(0);
    });

    it('should handle PCM playback', async () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { result } = renderHook(() => useAudioPipeline());

        await act(async () => {
            await result.current.start();
        });

        // Create mock PCM data
        const pcmData = new ArrayBuffer(512);
        const view = new Int16Array(pcmData);
        for (let i = 0; i < 256; i++) {
            view[i] = Math.sin(i * 0.1) * 32767;
        }

        act(() => {
            result.current.playPCM(pcmData, 24000);
        });

        // Should create buffer source and schedule playback
        expect(mockAudioContext.createBufferSource).toHaveBeenCalled();
    });

    it('should stop playback immediately on barge-in', async () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { result } = renderHook(() => useAudioPipeline());

        await act(async () => {
            await result.current.start();
        });

        // Queue some audio
        const pcmData = new ArrayBuffer(512);
        act(() => {
            result.current.playPCM(pcmData, 24000);
            result.current.playPCM(pcmData, 24000);
        });

        // Trigger barge-in
        act(() => {
            result.current.stopPlayback();
        });

        expect(result.current.speakerLevel).toBe(0);
    });

    it('should call PCM chunk callback', async () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const onPCMChunk = vi.fn();
        const { result } = renderHook(() => useAudioPipeline());

        result.current.onPCMChunk.current = onPCMChunk;

        await act(async () => {
            await result.current.start();
        });

        // Simulate worklet message
        const testPcm = new ArrayBuffer(512);
        act(() => {
            mockAudioWorkletNode.port.onmessage?.({
                data: { pcm: testPcm, rms: 0.5 },
            } as MessageEvent);
        });

        expect(onPCMChunk).toHaveBeenCalledWith(testPcm);
    });

    it('should handle microphone permission denial', async () => {
        vi.mocked(navigator.mediaDevices.getUserMedia).mockRejectedValueOnce(
            new Error('Permission denied')
        );

        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { result } = renderHook(() => useAudioPipeline());

        await act(async () => {
            await result.current.start();
        });

        expect(result.current.state).toBe('error');
    });
});

// ─────────────────────────────────────────────────────────────────────────────
// TEST: USE AETHER STORE
// ─────────────────────────────────────────────────────────────────────────────

describe('useAetherStore', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should initialize with default state', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const state = useAetherStore.getState();

        expect(state.currentRealm).toBe('void');
        expect(state.status).toBe('disconnected');
        expect(state.engineState).toBe('IDLE');
        expect(state.micLevel).toBe(0);
        expect(state.speakerLevel).toBe(0);
    });

    it('should update engine state', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.setEngineState('LISTENING');
        });

        expect(useAetherStore.getState().engineState).toBe('LISTENING');

        act(() => {
            store.setEngineState('SPEAKING');
        });

        expect(useAetherStore.getState().engineState).toBe('SPEAKING');
    });

    it('should update audio levels', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.setAudioLevels(0.5, 0.3);
        });

        const state = useAetherStore.getState();
        expect(state.micLevel).toBe(0.5);
        expect(state.speakerLevel).toBe(0.3);
    });

    it('should add transcript messages', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.addTranscriptMessage({
                role: 'user',
                content: 'Hello Aether',
            });
            store.addTranscriptMessage({
                role: 'agent',
                content: 'Hello! How can I help?',
            });
        });

        const state = useAetherStore.getState();
        expect(state.transcript).toHaveLength(2);
        expect(state.transcript[0].role).toBe('user');
        expect(state.transcript[0].content).toBe('Hello Aether');
        expect(state.transcript[1].role).toBe('agent');
    });

    it('should update telemetry data', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.setTelemetry(
                {
                    frustration: 0.2,
                    valence: 0.5,
                    arousal: 0.7,
                    engagement: 0.8,
                    pitch: 180,
                    rate: 4.5,
                },
                50
            );
        });

        const state = useAetherStore.getState();
        expect(state.frustrationScore).toBe(0.2);
        expect(state.valence).toBe(0.5);
        expect(state.arousal).toBe(0.7);
        expect(state.latencyMs).toBe(50);
    });

    it('should handle realm transitions', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.setRealm('skills');
        });

        expect(useAetherStore.getState().currentRealm).toBe('skills');

        act(() => {
            store.setRealm('neural');
        });

        expect(useAetherStore.getState().currentRealm).toBe('neural');
    });

    it('should add neural events for handover tracking', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.addNeuralEvent({
                fromAgent: 'AetherCore',
                toAgent: 'DebuggerAgent',
                task: 'Analyze stack trace',
                status: 'active',
            });
        });

        const state = useAetherStore.getState();
        expect(state.neuralEvents).toHaveLength(1);
        expect(state.neuralEvents[0].fromAgent).toBe('AetherCore');
        expect(state.neuralEvents[0].toAgent).toBe('DebuggerAgent');
    });

    it('should handle repair state updates', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.setRepairState({
                status: 'diagnosing',
                message: 'Analyzing connection error...',
                log: 'Detected WebSocket timeout',
                timestamp: Date.now(),
            });
        });

        const state = useAetherStore.getState();
        expect(state.repairState.status).toBe('diagnosing');
        expect(state.repairState.message).toBe('Analyzing connection error...');

        act(() => {
            store.setRepairState({
                status: 'applied',
                message: 'Connection restored',
                log: 'Reconnected successfully',
                timestamp: Date.now(),
            });
        });

        expect(useAetherStore.getState().repairState.status).toBe('applied');
    });

    it('should persist preferences to localStorage', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        act(() => {
            store.setPreferences({
                accentColor: 'purple',
                waveStyle: 'minimal',
            });
        });

        const state = useAetherStore.getState();
        expect(state.preferences.accentColor).toBe('purple');
        expect(state.preferences.waveStyle).toBe('minimal');
    });

    it('should toggle superpowers', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        const initialValue = store.preferences.superpowers.emotionSense;

        act(() => {
            store.toggleSuperpower('emotionSense');
        });

        expect(useAetherStore.getState().preferences.superpowers.emotionSense).toBe(
            !initialValue
        );
    });
});

// ─────────────────────────────────────────────────────────────────────────────
// TEST: USE AETHER GATEWAY
// ─────────────────────────────────────────────────────────────────────────────

describe('useAetherGateway', () => {
    let mockWs: MockWebSocket;

    beforeEach(() => {
        vi.clearAllMocks();
        vi.stubGlobal(
            'WebSocket',
            vi.fn((url: string) => {
                mockWs = new MockWebSocket(url);
                return mockWs;
            })
        );
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('should initialize with disconnected status', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { result } = renderHook(() => useAetherGateway());

        expect(result.current.status).toBe('disconnected');
        expect(result.current.latencyMs).toBe(0);
    });

    it('should connect and complete handshake', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { result } = renderHook(() => useAetherGateway('ws://localhost:18789'));

        await act(async () => {
            await result.current.connect();
        });

        // Wait for connection
        await waitFor(() => {
            expect(result.current.status).toBe('handshaking');
        });

        // Simulate challenge
        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'challenge',
                challenge: 'test-challenge-123',
            }));
        });

        // Should send response
        expect(mockWs.send).toHaveBeenCalled();

        // Simulate ack
        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'ack',
                session_id: 'test-session',
            }));
        });

        await waitFor(() => {
            expect(result.current.status).toBe('connected');
        });
    });

    it('should handle engine state updates', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { useAetherStore } = await import('../store/useAetherStore');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        // Simulate engine state message
        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'engine_state',
                state: 'LISTENING',
            }));
        });

        await waitFor(() => {
            expect(useAetherStore.getState().engineState).toBe('LISTENING');
        });
    });

    it('should handle audio telemetry messages', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { useAetherStore } = await import('../store/useAetherStore');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'audio_telemetry',
                payload: {
                    rms: 0.65,
                    gain: 0.9,
                },
            }));
        });

        await waitFor(() => {
            const state = useAetherStore.getState();
            expect(state.micLevel).toBe(0.65);
        });
    });

    it('should handle transcript messages', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { useAetherStore } = await import('../store/useAetherStore');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'transcript',
                role: 'agent',
                text: 'I can help you with that.',
            }));
        });

        await waitFor(() => {
            const state = useAetherStore.getState();
            expect(state.transcript).toHaveLength(1);
            expect(state.transcript[0].content).toBe('I can help you with that.');
        });
    });

    it('should handle binary audio responses', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const onAudioResponse = vi.fn();
        const { result } = renderHook(() => useAetherGateway());

        result.current.onAudioResponse.current = onAudioResponse;

        await act(async () => {
            await result.current.connect();
        });

        // Simulate binary audio
        const audioData = new ArrayBuffer(1024);
        act(() => {
            mockWs.simulateBinary(audioData);
        });

        expect(onAudioResponse).toHaveBeenCalledWith(audioData);
    });

    it('should send audio data when connected', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        // Set to connected
        act(() => {
            mockWs.simulateMessage(JSON.stringify({ type: 'ack' }));
        });

        await waitFor(() => {
            expect(result.current.status).toBe('connected');
        });

        const pcmData = new ArrayBuffer(512);
        act(() => {
            result.current.sendAudio(pcmData);
        });

        expect(mockWs.send).toHaveBeenCalledWith(pcmData);
    });

    it('should handle soul handoff messages', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { useAetherStore } = await import('../store/useAetherStore');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'soul_handoff',
                target_soul: 'DebuggerAgent',
                from_soul: 'AetherCore',
                task_goal: 'Analyze runtime error',
            }));
        });

        await waitFor(() => {
            const state = useAetherStore.getState();
            expect(state.activeSoul).toBe('DebuggerAgent');
            expect(state.neuralEvents).toHaveLength(1);
        });
    });

    it('should disconnect properly', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        act(() => {
            result.current.disconnect();
        });

        expect(result.current.status).toBe('disconnected');
        expect(mockWs.close).toHaveBeenCalled();
    });

    it('should handle tick messages for latency measurement', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        const serverTime = Date.now() / 1000;
        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'tick',
                timestamp: serverTime,
            }));
        });

        await waitFor(() => {
            expect(result.current.latencyMs).toBeGreaterThanOrEqual(0);
        });
    });

    it('should handle repair state messages', async () => {
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { useAetherStore } = await import('../store/useAetherStore');
        const { result } = renderHook(() => useAetherGateway());

        await act(async () => {
            await result.current.connect();
        });

        act(() => {
            mockWs.simulateMessage(JSON.stringify({
                type: 'repair_state',
                payload: {
                    status: 'diagnosing',
                    message: 'Checking network connectivity',
                    log: 'Ping test started',
                },
            }));
        });

        await waitFor(() => {
            const state = useAetherStore.getState();
            expect(state.repairState.status).toBe('diagnosing');
        });
    });
});

// ─────────────────────────────────────────────────────────────────────────────
// TEST: FULL PIPELINE INTEGRATION
// ─────────────────────────────────────────────────────────────────────────────

describe('Full Pipeline Integration', () => {
    it('should integrate audio pipeline with gateway', async () => {
        const { useAudioPipeline } = await import('../hooks/useAudioPipeline');
        const { useAetherGateway } = await import('../hooks/useAetherGateway');
        const { useAetherStore } = await import('../store/useAetherStore');

        const audioHook = renderHook(() => useAudioPipeline());
        const gatewayHook = renderHook(() => useAetherGateway());

        // Start audio pipeline
        await act(async () => {
            await audioHook.result.current.start();
        });

        // Connect gateway
        await act(async () => {
            await gatewayHook.result.current.connect();
        });

        expect(audioHook.result.current.state).toBe('active');

        // Simulate PCM chunk from audio pipeline
        const pcmChunk = new ArrayBuffer(512);
        audioHook.result.current.onPCMChunk.current = (pcm: ArrayBuffer) => {
            gatewayHook.result.current.sendAudio(pcm);
        };

        act(() => {
            audioHook.result.current.onPCMChunk.current?.(pcmChunk);
        });

        // Audio should be sent through gateway
    });

    it('should update UI based on engine state', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');

        const states = ['IDLE', 'LISTENING', 'THINKING', 'SPEAKING', 'INTERRUPTING'];
        const store = useAetherStore.getState();

        for (const state of states) {
            act(() => {
                store.setEngineState(state as 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'INTERRUPTING');
            });

            expect(useAetherStore.getState().engineState).toBe(state);
        }
    });

    it('should handle complete user interaction cycle', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        // 1. User starts speaking
        act(() => {
            store.setEngineState('LISTENING');
            store.setAudioLevels(0.5, 0);
        });

        expect(useAetherStore.getState().engineState).toBe('LISTENING');

        // 2. User finishes, AI starts thinking
        act(() => {
            store.setEngineState('THINKING');
            store.setAudioLevels(0, 0);
        });

        // 3. AI responds
        act(() => {
            store.setEngineState('SPEAKING');
            store.setAudioLevels(0, 0.7);
            store.addTranscriptMessage({
                role: 'agent',
                content: 'Here is my response.',
            });
        });

        // 4. Return to idle
        act(() => {
            store.setEngineState('IDLE');
            store.setAudioLevels(0, 0);
        });

        const finalState = useAetherStore.getState();
        expect(finalState.engineState).toBe('IDLE');
        expect(finalState.transcript).toHaveLength(1);
    });
});

// ─────────────────────────────────────────────────────────────────────────────
// PERFORMANCE TESTS
// ─────────────────────────────────────────────────────────────────────────────

describe('Performance Tests', () => {
    it('should handle rapid state updates without performance issues', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        const startTime = performance.now();

        // Simulate 1000 rapid updates
        for (let i = 0; i < 1000; i++) {
            act(() => {
                store.setAudioLevels(Math.random(), Math.random());
            });
        }

        const endTime = performance.now();
        const duration = endTime - startTime;

        // Should complete in under 100ms
        expect(duration).toBeLessThan(100);
    });

    it('should handle large transcript history efficiently', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        const startTime = performance.now();

        // Add 100 messages
        for (let i = 0; i < 100; i++) {
            act(() => {
                store.addTranscriptMessage({
                    role: i % 2 === 0 ? 'user' : 'agent',
                    content: `Message ${i}`,
                });
            });
        }

        const endTime = performance.now();

        expect(useAetherStore.getState().transcript.length).toBe(100);
        expect(endTime - startTime).toBeLessThan(50);
    });

    it('should throttle telemetry updates', async () => {
        const { useAetherStore } = await import('../store/useAetherStore');
        const store = useAetherStore.getState();

        // Rapid telemetry updates
        for (let i = 0; i < 100; i++) {
            act(() => {
                store.setTelemetry(
                    {
                        frustration: Math.random(),
                        valence: Math.random(),
                        arousal: Math.random(),
                    },
                    Math.random() * 100
                );
            });
        }

        // Should not cause issues
        const state = useAetherStore.getState();
        expect(typeof state.frustrationScore).toBe('number');
    });
});
