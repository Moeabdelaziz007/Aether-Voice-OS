'use client';

import { useEffect, useCallback, useRef } from 'react';
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
    // Extract individual setters to avoid the whole store object changing reference
    const setAudioLevels = useAetherStore(state => state.setAudioLevels);
    const setStatus = useAetherStore(state => state.setStatus);
    const addSystemLog = useAetherStore(state => state.addSystemLog);
    const setEngineState = useAetherStore(state => state.setEngineState);

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

    // Refs to prevent dependency cycles in callbacks
    const isTerminating = useRef(false);

    // 1. Sync Audio RMS to Global Store for UI visualizing
    useEffect(() => {
        setAudioLevels(micLevel, speakerLevel);
    }, [micLevel, speakerLevel, setAudioLevels]);

    // 2. Sync Global Status
    useEffect(() => {
        if (gatewayStatus === 'disconnected') setStatus('disconnected');
        else if (gatewayStatus === 'connecting' || gatewayStatus === 'handshaking') setStatus('connecting');
        else if (gatewayStatus === 'connected') setStatus('connected');
        else if (gatewayStatus === 'error') setStatus('error');
    }, [gatewayStatus, setStatus]);

    // 3. Handle Connections gracefully based on store status triggers
    // Initialize connection (currently unused directly by component logic, but exposed)
    const initializeConnection = useCallback(async () => {
        try {
            addSystemLog('[Brain] Initializing Audio Pipeline...');
            await startAudio();

            addSystemLog('[Brain] Connecting to local Aether Gateway...');
            await connectGateway();

            addSystemLog('[Brain] Opening telemetry channel...');
            connectTelemetry();
        } catch (err) {
            addSystemLog('[Brain] Connection error occurred.');
            console.error(err);
            setStatus('error');
        }
    }, [startAudio, connectGateway, connectTelemetry, addSystemLog, setStatus]);

    // Ref prevent infinite unmount loop
    const terminateConnection = useCallback(() => {
        if (isTerminating.current) return;
        isTerminating.current = true;

        addSystemLog('[Brain] Terminating connections...');
        stopAudio();
        disconnectGateway();
        setEngineState('IDLE');

        // Reset after a short delay to allow reconnection later
        setTimeout(() => { isTerminating.current = false; }, 500);
    }, [stopAudio, disconnectGateway, addSystemLog, setEngineState]);

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
    }, [onPCMChunk, onAudioResponse, gatewayStatus, sendAudio, playPCM]);

    // Provide cleanup
    useEffect(() => {
        return () => {
            // Only run terminateConnection logic if component is unmounting to avoid hot-reload loops
            terminateConnection();
        };
    }, [terminateConnection]);

    return null; // Invisible structural component
}
