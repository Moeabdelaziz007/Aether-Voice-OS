"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import nacl from "tweetnacl";
import { useAetherStore } from "../store/useAetherStore";

/**
 * Aether Voice OS — Aether Gateway Hook (V2).
 *
 * Manages the connection to the local Aether Gateway (Python backend).
 * Handles:
 *  - WebSocket lifecycle
 *  - Challenge-response handshake (Ed25519)
 *  - Binary audio routing (PCM)
 *  - Heartbeat/Tick synchronization + latency
 *  - ALL backend broadcast events (engine_state, transcript, etc.)
 *  - Vision frame forwarding
 */

export type GatewayStatus =
    | "disconnected"
    | "connecting"
    | "handshaking"
    | "connected"
    | "error";

interface AetherGatewayReturn {
    status: GatewayStatus;
    latencyMs: number;
    connect: (idToken?: string) => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    sendVisionFrame: (base64: string) => void;
    sendIntent: (input: string, level?: 1 | 2 | 3) => Promise<void>;
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
}

// ── Ed25519 Keypair (persisted in localStorage for cross-tab persistence) ──
function getOrCreateKeypair(): nacl.SignKeyPair {
    const STORAGE_KEY = "aether_ed25519_seed";
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            const seed = new Uint8Array(JSON.parse(stored));
            return nacl.sign.keyPair.fromSeed(seed);
        }
    } catch { /* localStorage may not be available (SSR) */ }

    // Generate random seed for production security
    const seed = nacl.randomBytes(32);

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(seed)));
    } catch { /* ignore */ }

    return nacl.sign.keyPair.fromSeed(seed);
}

function toHex(data: Uint8Array): string {
    return Array.from(data).map(b => b.toString(16).padStart(2, "0")).join("");
}

function fromHex(hex: string): Uint8Array {
    const normalized = hex.length % 2 === 0 ? hex : `0${hex}`;
    const bytes = new Uint8Array(normalized.length / 2);
    for (let i = 0; i < normalized.length; i += 2) {
        bytes[i / 2] = Number.parseInt(normalized.slice(i, i + 2), 16);
    }
    return bytes;
}

const DEFAULT_URL = process.env.NEXT_PUBLIC_AETHER_GATEWAY_URL || "ws://localhost:18789";

export function useAetherGateway(url = DEFAULT_URL): AetherGatewayReturn {
    const [status, setStatus] = useState<GatewayStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);
    const wsRef = useRef<WebSocket | null>(null);
    const store = useAetherStore();
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const keyPairRef = useRef<nacl.SignKeyPair | null>(null);

    const connect = useCallback(async (idToken?: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        setStatus("connecting");

        // Initialize keypair (persisted in local storage)
        if (!keyPairRef.current) {
            keyPairRef.current = getOrCreateKeypair();
        }
        const kp = keyPairRef.current;

        try {
            const ws = new WebSocket(url);
            ws.binaryType = "arraybuffer";
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("✦ Aether Gateway connection opened");
                setStatus("handshaking");
            };

            ws.onmessage = async (event) => {
                if (typeof event.data === "string") {
                    const msg = JSON.parse(event.data);
                    const getCinematicPayload = () => {
                        const payload = msg.payload ?? msg;
                        const protocolVersion = Number(
                            payload?.protocol_version ?? payload?.protocolVersion ?? msg?.protocol_version ?? msg?.protocolVersion ?? 1
                        );
                        if (!Number.isFinite(protocolVersion) || protocolVersion !== 1) {
                            store.addSystemLog(`[Protocol] Ignored ${msg.type} with version ${String(protocolVersion)}`);
                            return null;
                        }
                        return payload;
                    };

                    // ── Handshake Challenge ──
                    if (msg.type === "connect.challenge") {
                        const challengeBytes = fromHex(msg.challenge);
                        const signatureBytes = nacl.sign.detached(challengeBytes, kp.secretKey);
                        ws.send(JSON.stringify({
                            type: "connect.response",
                            client_id: toHex(kp.publicKey),
                            signature: toHex(signatureBytes),
                            id_token: idToken, // Inject Firebase ID Token
                            capabilities: ["audio_streaming", "telemetry", "vision"]
                        }));
                    }

                    // ── Handshake Ack ──
                    else if (msg.type === "connect.ack") {
                        console.log("✦ Gateway Handshake Successful");
                        setStatus("connected");
                        store.setSessionStartTime(Date.now());
                        store.addSystemLog("[Gateway] Authenticated successfully.");
                    }

                    // ── Error ──
                    else if (msg.type === "error") {
                        console.error("Gateway error:", msg.message);
                        store.addSystemLog(`[Gateway] Error: ${msg.message}`);
                        if (msg.fatal) setStatus("error");
                    }

                    // ── Tick (Heartbeat + Latency) ──
                    else if (msg.type === "tick") {
                        const now = Date.now();
                        const serverTime = msg.timestamp * 1000;
                        const measuredLatency = Math.abs(now - serverTime);
                        setLatencyMs(measuredLatency);
                        store.setLatencyMs(measuredLatency);
                    }

                    // ── Engine State (LISTENING, SPEAKING, THINKING, etc.) ──
                    else if (msg.type === "engine_state") {
                        store.setEngineState(msg.state);
                        store.addSystemLog(`[Engine] State → ${msg.state}`);
                    }

                    // ── Transcript (User/Agent speech segments) ──
                    else if (msg.type === "transcript") {
                        store.addTranscriptMessage({
                            role: msg.role === "user" ? "user" : "agent",
                            content: msg.text || msg.content || "",
                        });
                    }

                    // ── Affective Score (Thalamic Gate telemetry) ──
                    else if (msg.type === "affective_score") {
                        store.setTelemetry({
                            frustration: msg.frustration,
                            valence: msg.valence,
                            arousal: msg.arousal,
                            engagement: msg.engagement,
                            pitch: msg.pitch,
                            rate: msg.rate,
                        }, latencyMs);
                    }

                    // ── Audio Telemetry (Thalamic Gate VAD/RMS/Gain) ──
                    else if (msg.type === "audio_telemetry") {
                        // Directly update store for high-frequency updates
                        useAetherStore.getState().setAudioLevels(msg.payload.rms || 0, msg.payload.gain || 0);
                    }

                    // ── Repair State (Watchdog → Frontend healing) ──
                    else if (msg.type === "repair_state") {
                        useAetherStore.getState().setRepairState({
                            status: msg.payload?.status || msg.status || 'diagnosing',
                            message: msg.payload?.message || msg.message || '',
                            log: msg.payload?.log || msg.log || '',
                            timestamp: Date.now(),
                        });
                    }

                    // ── Neural Event (Hive agent activity) ──
                    else if (msg.type === "neural_event") {
                        store.addNeuralEvent({
                            fromAgent: msg.from_agent || "AetherCore",
                            toAgent: msg.to_agent || "Unknown",
                            task: msg.task || msg.description || "",
                            status: msg.status || "active",
                        });
                    }

                    // ── Vision Pulse (Screen capture acknowledgment) ──
                    else if (msg.type === "vision_pulse") {
                        store.setVisionPulse(msg.timestamp || new Date().toISOString());
                        store.setVisionActive(true);
                    }

                    // ── Intent Update (V1.1 Lifecycle) ──
                    else if (msg.type === "intent_update") {
                        if (msg.memory_update?.predicted_next_goal) {
                            store.setPredictedGoal(msg.memory_update.predicted_next_goal);
                        }
                    }

                    // ── Mutation Event (Code/file changes) ──
                    else if (msg.type === "mutation_event") {
                        store.setMutation(msg.description || msg.mutation || "Unknown mutation");
                    }

                    // ── Tool Result (Silent hints, code suggestions) ──
                    else if (msg.type === "tool_result") {
                        store.addSilentHint({
                            id: crypto.randomUUID(),
                            text: msg.tool_name || "Tool completed",
                            code: msg.code,
                            explanation: msg.result || msg.message,
                            priority: msg.priority || "info",
                            type: msg.code ? "code" : "hint",
                            timestamp: Date.now(),
                        });
                        store.addSystemLog(`[Tool] ${msg.tool_name}: ${msg.status || "done"}`);
                    }

                    // ── Cinematic Task Pulse (Visual Task Execution Director) ──
                    else if (msg.type === "task_pulse") {
                        const payload = getCinematicPayload();
                        if (!payload) return;
                        const taskId = payload.task_id || payload.taskId || "task-unknown";
                        const pulse = {
                            taskId,
                            phase: payload.phase || "EXECUTING",
                            action: payload.action || "task_execution",
                            vibe: payload.vibe || "focusing",
                            thought: payload.thought || "",
                            avatarTarget: payload.avatar_target || payload.avatarTarget || "center",
                            intensity: Number(payload.intensity ?? 0.6),
                            latencyMs: payload.latency_ms || payload.latencyMs,
                            timestamp: Date.now(),
                        } as const;

                        store.setTaskPulse(pulse);
                        store.setAvatarCinematicState(payload.avatar_state || payload.avatarState || "EXECUTING");
                        store.pushMissionLog({
                            taskId,
                            title: payload.action || "Neural Operation",
                            detail: payload.thought || payload.message || "",
                            status: payload.phase === "FAILED" ? "failed" : payload.phase === "COMPLETED" ? "completed" : "in-progress",
                        });
                    }

                    // ── Avatar State Stream (Embodied Agent) ──
                    else if (msg.type === "avatar_state") {
                        const payload = getCinematicPayload();
                        if (!payload) return;
                        const nextState = payload.state || payload.avatar_state || "IDLE";
                        store.setAvatarCinematicState(nextState);
                        if (payload.reason) {
                            store.addSystemLog(`[Avatar] ${nextState} — ${payload.reason}`);
                        }
                    }

                    // ── Workspace Galaxy State ──
                    else if (msg.type === "workspace_state") {
                        const payload = getCinematicPayload();
                        if (!payload) return;
                        store.applyWorkspaceState(payload);
                    }

                    // ── Mission Log Line ──
                    else if (msg.type === "task_timeline_item") {
                        const payload = getCinematicPayload();
                        if (!payload) return;
                        store.pushMissionLog({
                            taskId: payload.task_id || payload.taskId || undefined,
                            title: payload.title || "Mission Step",
                            detail: payload.detail || payload.description || "",
                            status: payload.status || "in-progress",
                        });
                    }

                    // ── Affected / Paralinguistics Telemetry (Alpha Kernel V2) ──
                    else if (msg.type === "telemetry") {
                        if (msg.metric_name === "paralinguistics") {
                            store.setTelemetry({
                                pitch: msg.metadata?.pitch_hz,
                                spectralCentroid: msg.metadata?.spectral_centroid,
                                frustration: msg.metadata?.frustration,
                            }, latencyMs);
                            store.setAudioLevels(msg.metadata?.volume || 0, store.speakerLevel);
                        } else if (msg.metric_name === "noise_floor") {
                            store.setTelemetry({ noiseFloor: msg.value }, latencyMs);
                        }
                    }

                    // ── Soul Handoff (Multi-agent switch) ──
                    else if (msg.type === "soul_handoff" || msg.type === "handover") {
                        const target = msg.target_soul || msg.target_agent_id || "AetherCore";
                        store.setActiveSoul(target);
                        store.addNeuralEvent({
                            fromAgent: msg.from_soul || msg.source_agent_id || "AetherCore",
                            toAgent: target,
                            task: msg.task_goal || msg.reason || "Context handover",
                            status: "active",
                        });
                        store.addSystemLog(`[Hive] Handover → ${target}`);
                    }
                }
                else if (event.data instanceof ArrayBuffer) {
                    // Raw audio bytes from Aether backend (Gemini -> Engine -> Gateway)
                    if (onAudioResponse.current) {
                        onAudioResponse.current(event.data);
                    }
                }
            };

            ws.onerror = (err) => {
                console.error("Gateway WS error:", err);
                setStatus("error");
            };

            ws.onclose = () => {
                console.log("Gateway WS closed");
                setStatus("disconnected");
                wsRef.current = null;
            };

        } catch (err) {
            console.error("Failed to connect to Gateway:", err);
            setStatus("error");
        }
    }, [url, store, latencyMs]);

    const sendAudio = useCallback((pcm: ArrayBuffer) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || status !== "connected") return;
        ws.send(pcm);
    }, [status]);

    const sendIntent = useCallback(async (input: string, level: 1 | 2 | 3 = 1) => {
        const ws = wsRef.current;
        const kp = keyPairRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || status !== "connected" || !kp) return;

        const intent_id = crypto.randomUUID();
        const payload = {
            raw_input: input,
            timestamp_ms: Date.now(),
            user_context: {
                active_file: "portal/main",
                cursor_line: 0
            }
        };

        // V1.1 Signature: Sign the SHA-256 hash of the entire payload string
        const payloadStr = JSON.stringify(payload);
        const encoder = new TextEncoder();
        const msgUint8 = encoder.encode(payloadStr);
        const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
        const hashArray = new Uint8Array(hashBuffer);

        const signature = nacl.sign.detached(hashArray, kp.secretKey);

        ws.send(JSON.stringify({
            type: "INTENT",
            version: "1.1",
            intent_id,
            level,
            source: "text",
            payload,
            signature: toHex(signature),
            memory_context: {
                last_intent_id: localStorage.getItem("aether_last_intent_id") || undefined,
                session_depth: 0
            }
        }));

        localStorage.setItem("aether_last_intent_id", intent_id);
    }, [status]);

    const sendVisionFrame = useCallback((base64: string) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || status !== "connected") return;
        ws.send(JSON.stringify({
            type: "vision_frame",
            data: base64,
            timestamp: Date.now(),
        }));
    }, [status]);

    const disconnect = useCallback(() => {
        wsRef.current?.close();
        wsRef.current = null;
        setStatus("disconnected");
    }, []);

    useEffect(() => {
        return () => {
            disconnect();
        };
    }, [disconnect]);

    return { status, latencyMs, connect, disconnect, sendAudio, sendVisionFrame, sendIntent, onAudioResponse };
}
