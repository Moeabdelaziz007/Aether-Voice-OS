'use client';

import { useEffect, useCallback } from 'react';
import { useAetherStore } from '../store/useAetherStore';
import { useAudioPipeline } from '../hooks/useAudioPipeline';
import { useGeminiLive } from '../hooks/useGeminiLive';

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
        status: geminiStatus,
        connect: connectGemini,
        disconnect: disconnectGemini,
        sendAudio,
        onAudioResponse,
        onInterrupt
    } = useGeminiLive();

    // 1. Sync Audio RMS to Global Store for UI visualizing
    useEffect(() => {
        store.setAudioLevels(micLevel, speakerLevel);
    }, [micLevel, speakerLevel, store]);

    // 2. Sync Global Status
    useEffect(() => {
        if (geminiStatus === 'disconnected') store.setStatus('disconnected');
        else if (geminiStatus === 'connecting') store.setStatus('connecting');
        else store.setStatus('connected');

        // Map Gemini statuses to EngineState for parity
        if (geminiStatus === 'listening') store.setEngineState('LISTENING');
        if (geminiStatus === 'speaking') store.setEngineState('SPEAKING');
    }, [geminiStatus, store]);

    // 3. Handle Connections gracefully based on store status triggers
    const initializeConnection = useCallback(async () => {
        try {
            store.addSystemLog('[Brain] Initializing Audio Pipeline...');
            await startAudio();

            store.addSystemLog('[Brain] Connecting to Gemini Live Network...');
            await connectGemini();
        } catch (err) {
            store.addSystemLog('[Brain] Connection error occurred.');
            console.error(err);
            store.setStatus('error');
        }
    }, [startAudio, connectGemini, store]);

    const terminateConnection = useCallback(() => {
        store.addSystemLog('[Brain] Terminating connections...');
        stopAudio();
        disconnectGemini();
        store.setEngineState('IDLE');
    }, [stopAudio, disconnectGemini, store]);

    // Connect automatically if global status dictates
    /* In the future, this can listen to a specific trigger. For now, we expose
       a way to connect/disconnect via the store if needed. */

    // 4. Critical Pipeline Wiring
    useEffect(() => {
        // Pipe Mic PCM -> Gemini
        onPCMChunk.current = (pcm: ArrayBuffer) => {
            if (geminiStatus === 'listening' || geminiStatus === 'speaking') {
                sendAudio(pcm);
            }
        };

        // Pipe Gemini Audio -> Speaker
        onAudioResponse.current = (pcm: ArrayBuffer) => {
            // Assuming Gemini output is 24kHz
            playPCM(pcm, 24000);
        };

        // Handle Interruptions (Barge-ins)
        onInterrupt.current = () => {
            store.setEngineState('INTERRUPTING');
            store.addSystemLog('[Brain] ⚡ Barge-in detected, halting current output.');
        };
    }, [onPCMChunk, onAudioResponse, onInterrupt, geminiStatus, sendAudio, playPCM, store]);

    // Provide cleanup
    useEffect(() => {
        return () => {
            terminateConnection();
        };
    }, [terminateConnection]);

    return null; // Invisible structural component
}
