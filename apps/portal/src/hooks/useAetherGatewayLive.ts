"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import nacl from "tweetnacl";

export type SessionStatus =
    | "disconnected"
    | "connecting"
    | "connected"
    | "listening"
    | "speaking"
    | "thinking"
    | "error";

export interface GatewayToolCall {
    name: string;
    args: Record<string, unknown>;
    id: string;
}

interface AetherGatewayLiveReturn {
    status: SessionStatus;
    latencyMs: number;
    connect: () => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    sendToolResponse: (callId: string, result: Record<string, unknown>) => void;
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
    onInterrupt: React.MutableRefObject<(() => void) | null>;
    onTranscript: React.MutableRefObject<((text: string, role: "user" | "ai") => void) | null>;
    onToolCall: React.MutableRefObject<((toolCall: GatewayToolCall) => void) | null>;
}

const AETHER_GATEWAY_URL =
    process.env.NEXT_PUBLIC_AETHER_GATEWAY_URL || "ws://localhost:18789";

const PROTOCOL_VERSION = "2.1";
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000];
const MAX_RETRIES = 3;

function toHex(data: Uint8Array): string {
    return Array.from(data).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function fromHex(hex: string): Uint8Array {
    const normalized = hex.length % 2 === 0 ? hex : `0${hex}`;
    const bytes = new Uint8Array(normalized.length / 2);
    for (let i = 0; i < normalized.length; i += 2) {
        bytes[i / 2] = Number.parseInt(normalized.slice(i, i + 2), 16);
    }
    return bytes;
}

function decodeBase64ToBuffer(b64: string): ArrayBuffer {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

function getOrCreateKeypair(): nacl.SignKeyPair {
    const STORAGE_KEY = "aether_gateway_ed25519_seed";
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        const seed = new Uint8Array(JSON.parse(stored));
        return nacl.sign.keyPair.fromSeed(seed);
    }

    const seed = nacl.randomBytes(32);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(seed)));
    return nacl.sign.keyPair.fromSeed(seed);
}

export function useAetherGatewayLive(): AetherGatewayLiveReturn {
    const [status, setStatus] = useState<SessionStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);

    const wsRef = useRef<WebSocket | null>(null);
    const intentionalClose = useRef(false);
    const retryCount = useRef(0);
    const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const keyPairRef = useRef<nacl.SignKeyPair | null>(null);

    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const onInterrupt = useRef<(() => void) | null>(null);
    const onTranscript = useRef<((text: string, role: "user" | "ai") => void) | null>(null);
    const onToolCall = useRef<((toolCall: GatewayToolCall) => void) | null>(null);

    const lastSendTime = useRef(0);
    const latencyHistory = useRef<number[]>([]);
    const waitingForResponse = useRef(false);

    const measureLatency = useCallback(() => {
        if (!waitingForResponse.current || lastSendTime.current <= 0) return;
        const rtt = performance.now() - lastSendTime.current;
        waitingForResponse.current = false;

        const history = latencyHistory.current;
        history.push(rtt);
        if (history.length > 10) history.shift();
        const avg = history.reduce((a, b) => a + b, 0) / history.length;
        setLatencyMs(Math.round(avg));
    }, []);

    const handleGatewayMessage = useCallback(
        (rawMsg: Record<string, unknown>) => {
            const msgType = String(rawMsg.type || "");
            const payload =
                rawMsg.payload && typeof rawMsg.payload === "object"
                    ? (rawMsg.payload as Record<string, unknown>)
                    : rawMsg;

            if (msgType === "connect.ack") {
                setStatus("connected");
                return;
            }

            if (msgType === "tick") {
                const ts = Number(rawMsg.timestamp || payload.timestamp || 0);
                if (ts > 0) {
                    const measuredLatency = Math.abs(Date.now() - ts * 1000);
                    setLatencyMs(Math.round(measuredLatency));
                }
                return;
            }

            if (msgType === "engine_state") {
                const state = String(payload.state || "").toUpperCase();
                if (state === "SPEAKING") setStatus("speaking");
                else if (state === "THINKING") setStatus("thinking");
                else if (state === "LISTENING") setStatus("listening");
                else if (state === "INTERRUPTED") onInterrupt.current?.();
                return;
            }

            if (msgType === "interrupt") {
                setStatus("listening");
                waitingForResponse.current = false;
                onInterrupt.current?.();
                return;
            }

            if (msgType === "transcript") {
                const text = String(payload.text || payload.content || "");
                const role = payload.role === "user" ? "user" : "ai";
                if (text) onTranscript.current?.(text, role);
                return;
            }

            if (msgType === "audio.chunk") {
                const data = payload.data;
                if (typeof data === "string") {
                    measureLatency();
                    onAudioResponse.current?.(decodeBase64ToBuffer(data));
                }
                return;
            }

            if (msgType === "tool.call") {
                const call: GatewayToolCall = {
                    id: String(payload.id || crypto.randomUUID()),
                    name: String(payload.name || "unknown_tool"),
                    args: (payload.args as Record<string, unknown>) || {},
                };
                onToolCall.current?.(call);
            }
        },
        [measureLatency]
    );

    const attemptReconnect = useCallback(() => {
        if (retryCount.current >= MAX_RETRIES) {
            setStatus("error");
            return;
        }

        const delay = RECONNECT_DELAYS[Math.min(retryCount.current, RECONNECT_DELAYS.length - 1)];
        retryCount.current += 1;
        setStatus("connecting");
        retryTimer.current = setTimeout(() => {
            void connect();
        }, delay);
    }, []);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        intentionalClose.current = false;
        setStatus("connecting");

        if (!keyPairRef.current) {
            keyPairRef.current = getOrCreateKeypair();
        }
        const kp = keyPairRef.current;

        const ws = new WebSocket(AETHER_GATEWAY_URL);
        ws.binaryType = "arraybuffer";
        wsRef.current = ws;

        ws.onmessage = (event: MessageEvent) => {
            if (typeof event.data === "string") {
                const msg = JSON.parse(event.data) as Record<string, unknown>;

                if (msg.type === "connect.challenge") {
                    const challengeBytes = fromHex(String(msg.challenge || ""));
                    const signatureBytes = nacl.sign.detached(challengeBytes, kp.secretKey);
                    ws.send(
                        JSON.stringify({
                            type: "connect.response",
                            version: PROTOCOL_VERSION,
                            client_id: toHex(kp.publicKey),
                            signature: toHex(signatureBytes),
                            capabilities: ["audio.input", "audio.output", "tools.client"],
                        })
                    );
                    return;
                }

                if (msg.type === "error") {
                    setStatus("error");
                    return;
                }

                handleGatewayMessage(msg);
            } else if (event.data instanceof ArrayBuffer) {
                measureLatency();
                onAudioResponse.current?.(event.data);
            }
        };

        ws.onerror = () => setStatus("error");
        ws.onclose = () => {
            wsRef.current = null;
            if (!intentionalClose.current) attemptReconnect();
            else setStatus("disconnected");
        };

        ws.onopen = () => {
            retryCount.current = 0;
        };
    }, [attemptReconnect, handleGatewayMessage, measureLatency]);

    const sendAudio = useCallback((pcm: ArrayBuffer) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) return;

        if (!waitingForResponse.current) {
            waitingForResponse.current = true;
            lastSendTime.current = performance.now();
        }

        const bytes = new Uint8Array(pcm);
        let b64 = "";
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
            b64 += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
        }

        ws.send(
            JSON.stringify({
                type: "audio.chunk",
                version: PROTOCOL_VERSION,
                payload: {
                    mime_type: "audio/pcm;rate=16000",
                    data: btoa(b64),
                },
            })
        );
    }, []);

    const sendToolResponse = useCallback((callId: string, result: Record<string, unknown>) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) return;

        ws.send(
            JSON.stringify({
                type: "tool_result",
                version: PROTOCOL_VERSION,
                payload: {
                    call_id: callId,
                    result,
                },
            })
        );
    }, []);

    const disconnect = useCallback(() => {
        intentionalClose.current = true;
        if (retryTimer.current) {
            clearTimeout(retryTimer.current);
            retryTimer.current = null;
        }
        wsRef.current?.close();
        wsRef.current = null;
        retryCount.current = 0;
        waitingForResponse.current = false;
        setStatus("disconnected");
    }, []);

    useEffect(() => () => disconnect(), [disconnect]);

    return {
        status,
        latencyMs,
        connect,
        disconnect,
        sendAudio,
        sendToolResponse,
        onAudioResponse,
        onInterrupt,
        onTranscript,
        onToolCall,
    };
}
