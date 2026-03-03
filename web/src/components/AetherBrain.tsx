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
import { useGeminiLive, type GeminiToolCall } from "@/hooks/useGeminiLive";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useVisionPulse } from "@/hooks/useVisionPulse";
import { useAetherStore } from "@/store/useAetherStore";

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
    const gemini = useGeminiLive();
    const vision = useVisionPulse();

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
                await gemini.connect();
                store.setConnectionMode("gemini");
                store.setSessionStartTime(Date.now());
                store.addSystemLog("[Brain] Gemini Live session booting...");

                // Auto-start vision capture after connection
                try {
                    await vision.startCapture();
                    store.setVisionActive(true);
                    store.addSystemLog("[Brain] 👁 Vision Pulse activated");
                } catch {
                    store.addSystemLog("[Brain] Vision capture skipped (no permission)");
                }
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

    // ─── 6.5 Vision Pulse → Gemini (1 FPS screen frames) ──────────
    useEffect(() => {
        if (vision.latestFrame && gemini.status === "listening") {
            gemini.sendVisionFrame(vision.latestFrame);
        }
    }, [vision.latestFrame, gemini]); // eslint-disable-line react-hooks/exhaustive-deps

    // ─── 7. Real-time audio levels → store ─────────────────────────
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
                        gemini.sendVisionFrame(vision.latestFrame);
                    }
                    store.addSystemLog("[Brain] 😤 Emotion spike → priority vision injected");
                }
                wasQuietRef.current = false;
            } else {
                wasQuietRef.current = false;
            }
        }, 50); // 20Hz update rate

        return () => clearInterval(interval);
    }, [pipeline.state, pipeline.micLevel, pipeline.speakerLevel, store, gemini, vision]);

    // ─── 8. Real latency → store ───────────────────────────────────
    useEffect(() => {
        if (gemini.latencyMs > 0) {
            store.setLatencyMs(gemini.latencyMs);
        }
    }, [gemini.latencyMs, store]);

    // ─── 9. Tool Call Dispatcher → Silent UI Hints ─────────────────
    useEffect(() => {
        gemini.onToolCall.current = (call: GeminiToolCall) => {
            const { name, args, id } = call;

            if (name === "show_silent_hint" || name === "show_code_suggestion") {
                store.addSilentHint({
                    id: crypto.randomUUID(),
                    text: (args.text as string) || (args.title as string) || "",
                    code: args.code as string | undefined,
                    explanation: args.explanation as string | undefined,
                    priority:
                        (args.priority as "info" | "warning" | "suggestion") ||
                        (name === "show_code_suggestion" ? "suggestion" : "info"),
                    type: name === "show_code_suggestion" ? "code" : "hint",
                    timestamp: Date.now(),
                });
                store.addSystemLog(`[Brain] 🔧 Silent ${name}: ${args.text || args.title}`);
            }

            // Send tool response back to Gemini
            gemini.sendToolResponse(id, { success: true, displayed: true });
        };

        return () => {
            gemini.onToolCall.current = null;
        };
    }, [gemini, store]);

    // ─── 10. Cleanup on disconnect ─────────────────────────────────
    useEffect(() => {
        if (store.status === "disconnected") {
            pipeline.stop();
            gemini.disconnect();
            vision.stopCapture();
            store.setVisionActive(false);
            store.setSessionStartTime(null);
        }
    }, [store.status]); // eslint-disable-line react-hooks/exhaustive-deps

    return null; // Invisible component — the brain renders nothing
}
