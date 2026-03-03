"use client";
/**
 * AetherBrain — The Invisible Conductor.
 *
 * Wires the voice pipeline:
 *   1. Audio capture (mic → PCM chunks via AudioWorklet)
 *   2. Client-side VAD gate (skip silence, save API quota)
 *   3. Gemini Live API (primary voice mode via WebSocket)
 *   4. Gapless audio playback (scheduled output queue)
 *   5. Barge-in interruption (instant stop + redirect)
 *   6. Real-time telemetry feed to global store
 *
 * This component renders nothing — it IS the brain.
 */

import { useEffect, useRef, useCallback } from "react";
import { useGeminiLive } from "@/hooks/useGeminiLive";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useAetherStore } from "@/store/useAetherStore";

// Client-side VAD threshold — below this, audio is silence
const VAD_RMS_THRESHOLD = 0.008;
const SILENCE_TIMEOUT_MS = 800; // Allow one chunk after this much silence (for end-of-turn)

export default function AetherBrain() {
    const store = useAetherStore();
    const pipeline = useAudioPipeline();
    const gemini = useGeminiLive();

    // Silence tracking for client-side VAD
    const silenceStartRef = useRef(0);
    const isSpeakingRef = useRef(false);
    const lastRmsRef = useRef(0);

    // ─── 1. Connect/Disconnect on status changes ───────────────────
    useEffect(() => {
        if (store.status === "connecting") {
            const boot = async () => {
                await pipeline.start();
                await gemini.connect();
                store.setConnectionMode("gemini");
                store.setSessionStartTime(Date.now());
                store.addSystemLog("[Brain] Gemini Live session booting...");
            };
            boot().catch((err) => {
                console.error("Boot failed:", err);
                store.setStatus("error");
                store.addSystemLog(`[Brain] Boot failed: ${err}`);
            });
        }
    }, [store.status]); // eslint-disable-line react-hooks/exhaustive-deps

    // ─── 2. Sync Gemini status → store ─────────────────────────────
    useEffect(() => {
        const statusMap: Record<string, { status: typeof store.status; engine: typeof store.engineState }> = {
            disconnected: { status: "disconnected", engine: "IDLE" },
            connecting: { status: "connecting", engine: "IDLE" },
            connected: { status: "connected", engine: "IDLE" },
            listening: { status: "listening", engine: "LISTENING" },
            thinking: { status: "connected", engine: "THINKING" },
            speaking: { status: "speaking", engine: "SPEAKING" },
            error: { status: "error", engine: "IDLE" },
        };

        const mapped = statusMap[gemini.status];
        if (mapped) {
            store.setStatus(mapped.status);
            store.setEngineState(mapped.engine);
        }
    }, [gemini.status]); // eslint-disable-line react-hooks/exhaustive-deps

    // ─── 3. Pipe audio PCM → Gemini (with client-side VAD gate) ────
    const handlePCMChunk = useCallback(
        (pcm: ArrayBuffer) => {
            const rms = lastRmsRef.current;

            if (rms >= VAD_RMS_THRESHOLD) {
                // User is speaking — send to Gemini
                isSpeakingRef.current = true;
                silenceStartRef.current = 0;
                gemini.sendAudio(pcm);
            } else {
                // Silence detected
                if (isSpeakingRef.current) {
                    // Was speaking, now silent — start silence timer
                    if (silenceStartRef.current === 0) {
                        silenceStartRef.current = performance.now();
                    }

                    const silenceDuration =
                        performance.now() - silenceStartRef.current;

                    if (silenceDuration < SILENCE_TIMEOUT_MS) {
                        // Still within grace period — send (may be trailing speech)
                        gemini.sendAudio(pcm);
                    } else {
                        // Silence exceeded threshold — stop sending
                        isSpeakingRef.current = false;
                    }
                }
                // If user was NOT speaking, don't send silence → saves API quota
            }
        },
        [gemini]
    );

    // Wire the PCM callback
    useEffect(() => {
        const originalCallback = pipeline.onPCMChunk.current;
        pipeline.onPCMChunk.current = (pcm: ArrayBuffer) => {
            // The worklet sends {pcm, rms} objects but the hook unpacks them
            // We capture RMS from store.micLevel (set by the pipeline)
            lastRmsRef.current = store.micLevel;
            handlePCMChunk(pcm);
        };
        return () => {
            pipeline.onPCMChunk.current = originalCallback;
        };
    }, [handlePCMChunk, pipeline, store.micLevel]);

    // ─── 4. Pipe Gemini audio → gapless playback ───────────────────
    useEffect(() => {
        gemini.onAudioResponse.current = (audio: ArrayBuffer) => {
            pipeline.playPCM(audio, 24000);
        };
        return () => {
            gemini.onAudioResponse.current = null;
        };
    }, [gemini, pipeline]);

    // ─── 5. Barge-in: Gemini interrupts → stop playback ────────────
    useEffect(() => {
        gemini.onInterrupt.current = () => {
            pipeline.stopPlayback();
            store.setEngineState("INTERRUPTING");
            store.addSystemLog("[Brain] ⚡ Barge-in — playback stopped");
        };
        return () => {
            gemini.onInterrupt.current = null;
        };
    }, [gemini, pipeline, store]);

    // ─── 6. Transcript extraction → store ──────────────────────────
    useEffect(() => {
        gemini.onTranscript.current = (text: string, role: "user" | "ai") => {
            store.addTranscriptMessage({
                role: role === "ai" ? "agent" : "user",
                content: text,
            });
        };
        return () => {
            gemini.onTranscript.current = null;
        };
    }, [gemini, store]);

    // ─── 7. Real-time audio levels → store ─────────────────────────
    useEffect(() => {
        if (pipeline.state !== "active") return;

        const interval = setInterval(() => {
            store.setAudioLevels(pipeline.micLevel, pipeline.speakerLevel);
        }, 50); // 20Hz update rate

        return () => clearInterval(interval);
    }, [pipeline.state, pipeline.micLevel, pipeline.speakerLevel, store]);

    // ─── 8. Real latency → store ───────────────────────────────────
    useEffect(() => {
        if (gemini.latencyMs > 0) {
            store.setLatencyMs(gemini.latencyMs);
        }
    }, [gemini.latencyMs, store]);

    // ─── 9. Cleanup on disconnect ──────────────────────────────────
    useEffect(() => {
        if (store.status === "disconnected") {
            pipeline.stop();
            gemini.disconnect();
            store.setSessionStartTime(null);
        }
    }, [store.status]); // eslint-disable-line react-hooks/exhaustive-deps

    return null; // Invisible component — the brain renders nothing
}
