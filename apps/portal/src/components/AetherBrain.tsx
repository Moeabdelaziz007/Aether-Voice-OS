"use client";
/**
 * AetherBrain — The Invisible Conductor (V3 Ambient Intelligence).
 *
 * Wires the full multimodal pipeline:
 *   1. Audio capture (mic → PCM chunks via AudioWorklet)
 *   2. Client-side VAD gate (skip silence, save API quota)
 *   3. Gemini Live API (primary multimodal mode via WebSocket)
 *   4. Gapless audio playback (scheduled output queue)
 *   5. Barge-in interruption (instant stop + redirect)
 *   6. Vision Pulse (1 FPS screen capture → Gemini)
 *   7. Acoustic emotion trigger (frustration → priority context)
 *   8. Tool call dispatcher (Gemini tool calls → silent UI hints)
 *   9. Real-time telemetry feed to global store
 *
 * This component renders nothing — it IS the brain.
 */

import { useEffect, useRef, useCallback } from "react";
import { useAetherGateway } from "@/hooks/useAetherGateway";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useVisionPulse } from "@/hooks/useVisionPulse";
import { useAetherStore } from "@/store/useAetherStore";
import { useTelemetry } from "@/hooks/useTelemetry";
import { useAuth } from "@/hooks/useAuth";

// Client-side VAD threshold — below this, audio is silence
const VAD_RMS_THRESHOLD = 0.008;
const SILENCE_TIMEOUT_MS = 800;

// Acoustic emotion detection constants
const EMOTION_RMS_SPIKE = 0.06;      // Sharp RMS spike after quiet
const EMOTION_QUIET_THRESHOLD = 0.01; // What counts as "quiet"
const EMOTION_QUIET_DURATION = 2000;  // Quiet for 2s before spike = frustration

export default function AetherBrain() {
    const store = useAetherStore();
    const pipeline = useAudioPipeline();
    // Use the local Aether Gateway instead of direct Gemini connection
    const { getToken } = useAuth();
    const gateway = useAetherGateway();
    const vision = useVisionPulse();
    const { addLog } = useTelemetry();

    // Silence tracking for client-side VAD
    const silenceStartRef = useRef(0);
    const isSpeakingRef = useRef(false);
    const lastRmsRef = useRef(0);

    // Acoustic emotion tracking
    const quietStartRef = useRef(0);
    const wasQuietRef = useRef(false);

    // ─── 1. Connect/Disconnect on status changes ───────────────────
    useEffect(() => {
        if (store.status === "connecting") {
            const boot = async () => {
                await pipeline.start();
                const idToken = await getToken();
                await gateway.connect(idToken || undefined);
                store.setConnectionMode("gateway");
                store.setSessionStartTime(Date.now());
                store.addSystemLog("[Brain] Aether Gateway session booting...");
                addLog("Aether Gateway session booting", "info", "CORE");

                // Auto-start vision capture after connection
                try {
                    await vision.startCapture();
                    store.setVisionActive(true);
                    store.addSystemLog("[Brain] 👁 Vision Pulse activated");
                    addLog("Vision Pulse initialized (1 FPS)", "success", "VISION");
                } catch {
                    store.addSystemLog("[Brain] Vision capture skipped (no permission)");
                    addLog("Vision capture denied/error", "error", "VISION");
                }
            };
            boot().catch((err) => {
                console.error("Boot failed:", err);
                store.setStatus("error");
                store.addSystemLog(`[Brain] Boot failed: ${err}`);
            });
        }
    }, [store, pipeline, gateway, vision, getToken, addLog]);

    // ─── 2. Sync Gateway status → store ─────────────────────────────
    useEffect(() => {
        const statusMap: Record<string, { status: typeof store.status; engine: typeof store.engineState }> = {
            disconnected: { status: "disconnected", engine: "IDLE" },
            connecting: { status: "connecting", engine: "IDLE" },
            handshaking: { status: "connecting", engine: "THINKING" },
            connected: { status: "connected", engine: "LISTENING" }, // Ready to receive audio
            error: { status: "error", engine: "IDLE" },
        };

        const mapped = statusMap[gateway.status];
        if (mapped) {
            store.setStatus(mapped.status);
            store.setEngineState(mapped.engine);
        }
    }, [gateway.status, store]);

    // ─── 3. Pipe audio PCM → Gateway (with client-side VAD gate) ────
    const handlePCMChunk = useCallback(
        (pcm: ArrayBuffer) => {
            const rms = lastRmsRef.current;

            if (rms >= VAD_RMS_THRESHOLD) {
                // User is speaking — send to Gateway
                isSpeakingRef.current = true;
                silenceStartRef.current = 0;
                gateway.sendAudio(pcm);
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
                        gateway.sendAudio(pcm);
                    } else {
                        // Silence exceeded threshold — stop sending
                        isSpeakingRef.current = false;
                    }
                }
                // If user was NOT speaking, don't send silence → saves API quota
            }
        },
        [gateway]
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

    // ─── 4. Pipe Gateway audio → gapless playback ───────────────────
    useEffect(() => {
        gateway.onAudioResponse.current = (audio: ArrayBuffer) => {
            pipeline.playPCM(audio, 24000);
        };
        return () => {
            gateway.onAudioResponse.current = null;
        };
    }, [gateway, pipeline]);

    // ─── 5. Barge-in & Transcripts: Handled by Gateway payload routing (WIP integration) ────

    // ─── 6.5 Vision Pulse → Gateway (1 FPS screen frames) ──────────
    useEffect(() => {
        if (vision.latestFrame && gateway.status === "connected") {
            gateway.sendVisionFrame(vision.latestFrame);
        }
    }, [vision.latestFrame, gateway]);

    // ─── 7. Real-time Voice-Reactive UI via Web Audio API ──────────────
    useEffect(() => {
        let audioContext: AudioContext;
        let analyser: AnalyserNode;
        let microphone: MediaStreamAudioSourceNode;
        let dataArray: Uint8Array;
        let reqId: number;

        const startAnalyser = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
                audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                microphone = audioContext.createMediaStreamSource(stream);
                microphone.connect(analyser);

                analyser.fftSize = 256;
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);

                const renderFrame = () => {
                    reqId = requestAnimationFrame(renderFrame);
                    analyser.getByteFrequencyData(dataArray as any);

                    // Calculate volume (average of frequencies)
                    let sum = 0;
                    for (let i = 0; i < bufferLength; i++) {
                        sum += dataArray[i];
                    }
                    const volume = sum / bufferLength; // 0-255

                    // Normalize volume to 0.0 - 1.0 and scale it for the CSS property
                    const normalizedVol = volume / 255;
                    const glowIntensity = Math.min(1.0, 0.2 + (normalizedVol * 2.5));

                    document.documentElement.style.setProperty('--neon-glow-intensity', glowIntensity.toString());
                    document.documentElement.style.setProperty('--neon-glow-pulse', `${glowIntensity * 20}px`);
                };

                renderFrame();
            } catch (err) {
                console.error("Audio analyser failed:", err);
            }
        };

        if (pipeline.state === "active") {
            startAnalyser();
        }

        return () => {
            if (reqId) cancelAnimationFrame(reqId);
            if (audioContext && audioContext.state !== "closed") {
                audioContext.close();
            }
        };
    }, [pipeline.state]);

    // ─── 7.5 Store Audio Levels & Emotion Trigger ──────────────────────
    useEffect(() => {
        if (pipeline.state !== "active") return;

        const interval = setInterval(() => {
            store.setAudioLevels(pipeline.micLevel, pipeline.speakerLevel);

            // ─── Acoustic Emotion Trigger ─────────────────────
            const rms = pipeline.micLevel;
            if (rms < EMOTION_QUIET_THRESHOLD) {
                // User is quiet
                if (!wasQuietRef.current) {
                    quietStartRef.current = performance.now();
                    wasQuietRef.current = true;
                }
            } else if (rms > EMOTION_RMS_SPIKE && wasQuietRef.current) {
                // Sharp spike after quiet period
                const quietDuration = performance.now() - quietStartRef.current;
                if (quietDuration > EMOTION_QUIET_DURATION) {
                    // Frustration pattern detected → send priority vision frame
                    console.log("😤 Emotion spike detected — injecting priority vision");
                    if (vision.latestFrame) {
                        gateway.sendVisionFrame(vision.latestFrame);
                    }
                    store.addSystemLog("[Brain] 😤 Emotion spike → priority vision injected");
                    addLog("Emotion spike detected. Vision priority High.", "action", "BIO");
                }
                wasQuietRef.current = false;
            } else {
                wasQuietRef.current = false;
            }
        }, 50); // 20Hz update rate

        return () => clearInterval(interval);
    }, [pipeline.state, pipeline.micLevel, pipeline.speakerLevel, store, gateway, vision]);

    // ─── 8. Real latency → store (from Gateway V2 tick measurement) ──
    useEffect(() => {
        if (gateway.latencyMs > 0) {
            store.setLatencyMs(gateway.latencyMs);
        }
    }, [gateway.latencyMs, store]);

    // ─── 9. Tool Call Dispatcher — Now handled by Gateway V2 event routing ──
    // All tool_result and soul_handoff events are routed directly to the store
    // by useAetherGateway V2. No additional wiring needed here.

    // ─── 10. Cleanup on disconnect ─────────────────────────────────
    useEffect(() => {
        if (store.status === "disconnected") {
            pipeline.stop();
            gateway.disconnect();
            vision.stopCapture();
            store.setVisionActive(false);
            store.setSessionStartTime(null);
        }
    }, [store, pipeline, gateway, vision]);

    return null; // Invisible component — the brain renders nothing
}
