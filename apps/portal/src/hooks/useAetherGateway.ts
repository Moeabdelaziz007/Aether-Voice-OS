"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import nacl from "tweetnacl";
import { useAetherStore } from "../store/useAetherStore";
import { routeGatewayMessage } from "@/lib/gatewayMessageRouter";

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
    sendIntent: (input: string, level?: 1 | 2 | 3) => Promise<void>;
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
    onInterrupt: React.MutableRefObject<(() => void) | null>;
    onTranscript: React.MutableRefObject<((text: string, role: "user" | "agent") => void) | null>;
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
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000];
const MAX_RETRIES = 3;

export function useAetherGateway(url = DEFAULT_URL): AetherGatewayReturn {
    const [status, setStatus] = useState<GatewayStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);
    const wsRef = useRef<WebSocket | null>(null);
    const store = useAetherStore();
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const onInterrupt = useRef<(() => void) | null>(null);
    const onTranscript = useRef<((text: string, role: "user" | "agent") => void) | null>(null);
    const keyPairRef = useRef<nacl.SignKeyPair | null>(null);
    const intentionalClose = useRef(false);
    const retryCount = useRef(0);
    const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const connectRef = useRef<(() => Promise<void>) | null>(null);

    const attemptReconnect = useCallback(() => {
        if (intentionalClose.current) return;
        if (retryCount.current >= MAX_RETRIES) {
            setStatus("error");
            return;
        }

        const delay = RECONNECT_DELAYS[Math.min(retryCount.current, RECONNECT_DELAYS.length - 1)];
        retryCount.current += 1;
        setStatus("connecting");

        retryTimer.current = setTimeout(() => {
            connectRef.current?.();
        }, delay);
    }, []);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        intentionalClose.current = false;
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
                retryCount.current = 0;
            };

            ws.onmessage = async (event) => {
                if (typeof event.data === "string") {
                    const msg = JSON.parse(event.data);

                    // ── Handshake Challenge ──
                    if (msg.type === "connect.challenge") {
                        const challengeBytes = fromHex(msg.challenge);
                        const signatureBytes = nacl.sign.detached(challengeBytes, kp.secretKey);
                        ws.send(JSON.stringify({
                            type: "connect.response",
                            client_id: toHex(kp.publicKey),
                            signature: toHex(signatureBytes),
                            capabilities: ["audio_streaming", "telemetry", "vision"]
                        }));
                    }

                    routeGatewayMessage(msg, {
                        store,
                        latencyMs,
                        setLatencyMs,
                        setStatus,
                        onInterrupt: onInterrupt.current ?? undefined,
                        onTranscript: onTranscript.current ?? undefined,
                    });
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
                wsRef.current = null;
                if (intentionalClose.current) {
                    setStatus("disconnected");
                    return;
                }

                attemptReconnect();
            };

        } catch (err) {
            console.error("Failed to connect to Gateway:", err);
            attemptReconnect();
        }
    }, [url, store, latencyMs, attemptReconnect]);

    useEffect(() => {
        connectRef.current = connect;
    }, [connect]);

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
        intentionalClose.current = true;
        if (retryTimer.current) {
            clearTimeout(retryTimer.current);
            retryTimer.current = null;
        }
        retryCount.current = 0;
        wsRef.current?.close();
        wsRef.current = null;
        setStatus("disconnected");
    }, []);

    useEffect(() => {
        return () => {
            disconnect();
        };
    }, [disconnect]);

    return { status, latencyMs, connect, disconnect, sendAudio, sendVisionFrame, sendIntent, onAudioResponse, onInterrupt, onTranscript };
}
