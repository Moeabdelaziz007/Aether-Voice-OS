'use client';

import { useEffect, useCallback } from 'react';
import { useAetherStore } from '../store/useAetherStore';
import { useAudioPipeline } from '../hooks/useAudioPipeline';
import { useAetherGateway } from '../hooks/useAetherGateway';
import { useEngineTelemetry } from '../hooks/useEngineTelemetry';

/**
 * AetherBrain
 *
 * This invisible component acts as the central conductor.
 * It connects the local Audio Pipeline (mic/speaker) to the
 * Gemini Live WebSocket and updates the global Zustand store in real-time.
 */
export function AetherBrain() {
    const store = useAetherStore();

    const {
        state: audioState,
        micLevel,
        speakerLevel,
        start: startAudio,
        stop: stopAudio,
        playPCM,
        onPCMChunk
    } = useAudioPipeline();

    const {
        status: gatewayStatus,
        connect: connectGateway,
        disconnect: disconnectGateway,
        sendAudio,
        onAudioResponse
    } = useAetherGateway();

    const { connect: connectTelemetry } = useEngineTelemetry();

    // 1. Sync Audio RMS to Global Store for UI visualizing
    useEffect(() => {
        store.setAudioLevels(micLevel, speakerLevel);
    }, [micLevel, speakerLevel, store]);

    // 2. Sync Global Status
    useEffect(() => {
        if (gatewayStatus === 'disconnected') store.setStatus('disconnected');
        else if (gatewayStatus === 'connecting' || gatewayStatus === 'handshaking') store.setStatus('connecting');
        else if (gatewayStatus === 'connected') store.setStatus('connected');
        else if (gatewayStatus === 'error') store.setStatus('error');
    }, [gatewayStatus, store]);

    // 3. Handle Connections gracefully based on store status triggers
    const initializeConnection = useCallback(async () => {
        try {
            store.addSystemLog('[Brain] Initializing Audio Pipeline...');
            await startAudio();

            store.addSystemLog('[Brain] Connecting to local Aether Gateway...');
            await connectGateway();

            store.addSystemLog('[Brain] Opening telemetry channel...');
            connectTelemetry();
        } catch (err) {
            store.addSystemLog('[Brain] Connection error occurred.');
            console.error(err);
            store.setStatus('error');
        }
    }, [startAudio, connectGateway, connectTelemetry, store]);

    const terminateConnection = useCallback(() => {
        store.addSystemLog('[Brain] Terminating connections...');
        stopAudio();
        disconnectGateway();
        store.setEngineState('IDLE');
    }, [stopAudio, disconnectGateway, store]);

    // Connect automatically if global status dictates
    /* In the future, this can listen to a specific trigger. For now, we expose
       a way to connect/disconnect via the store if needed. */

    // 4. Critical Pipeline Wiring
    useEffect(() => {
        // Pipe Mic PCM -> Gateway -> Engine -> Gemini
        onPCMChunk.current = (pcm: ArrayBuffer) => {
            if (gatewayStatus === 'connected') {
                sendAudio(pcm);
            }
        };

        // Pipe Gateway Audio -> Speaker
        onAudioResponse.current = (pcm: ArrayBuffer) => {
            // Aether Gateway sends processed PCM (usually 16kHz or 24kHz)
            playPCM(pcm, 16000); // Defaulting to 16kHz for Aether stream
        };

        // In the local Gateway model, interrupts and state transitions
        // come via useEngineTelemetry (which updates store.setEngineState).
    }, [onPCMChunk, onAudioResponse, gatewayStatus, sendAudio, playPCM, store]);

    // Provide cleanup
    useEffect(() => {
        return () => {
            terminateConnection();
        };
    }, [terminateConnection]);

    return null; // Invisible structural component
}
