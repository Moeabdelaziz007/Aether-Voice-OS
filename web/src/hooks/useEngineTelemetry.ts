'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useAetherStore } from '../store/useAetherStore';

/**
 * useEngineTelemetry
 *
 * Connects to the local Python WebSocket Server (port 8765 by default)
 * to receive real-time system logs, state machine transitions, and affective scores.
 */
export function useEngineTelemetry(url = 'ws://localhost:18789') {
    const store = useAetherStore();
    const wsRef = useRef<WebSocket | null>(null);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        try {
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('[Telemetry] Connected to Aether Gateway.');
                store.addSystemLog('[Telemetry] Local secure link established.');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    const payload = data.payload || {};

                    if (data.type === 'log') {
                        store.addSystemLog(`[Engine] ${payload.message || data.message}`);
                    }
                    else if (data.type === 'engine_state') {
                        store.setEngineState(payload.state || data.state);
                    }
                    else if (data.type === 'affective_score') {
                        // Advanced affective metrics
                        store.setTelemetry({
                            frustration: payload.frustration,
                            valence: payload.valence,
                            arousal: payload.arousal,
                            engagement: payload.engagement,
                            zen_mode: payload.zen_mode,
                            pitch: payload.pitch,
                            rate: payload.rate
                        }, store.latencyMs);
                    }
                    else if (data.type === 'mutation_event') {
                        store.setMutation(payload.mutation);
                        store.addSystemLog(`[Evolution] Mutation detected: ${payload.mutation.substring(0, 50)}...`);
                    }
                    else if (data.type === 'neural_event') {
                        store.addNeuralEvent({
                            fromAgent: payload.fromAgent,
                            toAgent: payload.toAgent,
                            task: payload.task,
                            status: payload.status
                        });
                    }
                    else if (data.type === 'vision_pulse') {
                        store.setVisionPulse(data.timestamp);
                    }
                } catch (e) {
                    console.error('[Telemetry] Failed to parse message', e);
                }
            };

            ws.onerror = (err) => {
                console.error('[Telemetry] WS Error:', err);
            };

            ws.onclose = () => {
                console.log('[Telemetry] Disconnected from Core Engine.');
                wsRef.current = null;
                // Optionally attemp reconnect?
            };
        } catch (err) {
            console.error('[Telemetry] Failed to connect to Engine:', err);
        }
    }, [url, store]);

    const disconnect = useCallback(() => {
        wsRef.current?.close();
        wsRef.current = null;
    }, []);

    useEffect(() => {
        connect();
        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return { connect, disconnect };
}
