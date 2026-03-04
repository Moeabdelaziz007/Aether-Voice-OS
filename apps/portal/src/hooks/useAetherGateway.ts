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
    connect: () => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    sendVisionFrame: (base64: string) => void;
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
}

// ── Ed25519 Keypair (persisted in sessionStorage for tab-lifetime) ──
function getOrCreateKeypair(): nacl.SignKeyPair {
    const STORAGE_KEY = "aether_ed25519_seed";
    try {
        const stored = sessionStorage.getItem(STORAGE_KEY);
        if (stored) {
            const seed = new Uint8Array(JSON.parse(stored));
            return nacl.sign.keyPair.fromSeed(seed);
        }
    } catch { /* sessionStorage may not be available (SSR) */ }

    // Development seed (predictable "Architect" identity)
    const DEV_SEED = new Uint8Array([
        0xda, 0xee, 0x51, 0x93, 0x22, 0xd2, 0x1a, 0x56,
        0x5d, 0x6e, 0x76, 0xe1, 0xba, 0x92, 0x7c, 0xf6,
        0x61, 0x6e, 0x9e, 0x47, 0x72, 0x8a, 0x6b, 0x8b,
        0xa3, 0x3d, 0x90, 0x8d, 0xb2, 0x4f, 0x5f, 0x6c
    ]);

    try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(DEV_SEED)));
    } catch { /* ignore */ }

    return nacl.sign.keyPair.fromSeed(DEV_SEED);
}

function toHex(data: Uint8Array): string {
    return Array.from(data).map(b => b.toString(16).padStart(2, "0")).join("");
}

const DEFAULT_URL = process.env.NEXT_PUBLIC_AETHER_GATEWAY_URL || "ws://localhost:18789";

export function useAetherGateway(url = DEFAULT_URL): AetherGatewayReturn {
    const [status, setStatus] = useState<GatewayStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);
    const wsRef = useRef<WebSocket | null>(null);
    const store = useAetherStore();
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const keyPairRef = useRef<nacl.SignKeyPair | null>(null);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        setStatus("connecting");

        // Initialize keypair (persisted in sessionStorage)
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

                    // ── Handshake Challenge ──
                    if (msg.type === "challenge") {
                        const challengeBytes = new TextEncoder().encode(msg.challenge);
                        const signatureBytes = nacl.sign.detached(challengeBytes, kp.secretKey);
                        ws.send(JSON.stringify({
                            type: "response",
                            client_id: toHex(kp.publicKey),
                            signature: toHex(signatureBytes),
                            capabilities: ["audio_streaming", "telemetry", "vision"]
                        }));
                    }

                    // ── Handshake Ack ──
                    else if (msg.type === "ack") {
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

                    // ── Soul Handoff (Multi-agent switch) ──
                    else if (msg.type === "soul_handoff") {
                        store.setActiveSoul(msg.target_soul || msg.soul_name || "AetherCore");
                        store.addNeuralEvent({
                            fromAgent: msg.from_soul || "AetherCore",
                            toAgent: msg.target_soul || "Unknown",
                            task: msg.reason || "Soul handoff",
                            status: "active",
                        });
                        store.addSystemLog(`[Hive] Soul handoff → ${msg.target_soul}`);
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

    return { status, latencyMs, connect, disconnect, sendAudio, sendVisionFrame, onAudioResponse };
}

