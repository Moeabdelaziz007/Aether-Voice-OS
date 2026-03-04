"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import nacl from "tweetnacl";
import { useAetherStore } from "../store/useAetherStore";

/**
 * Aether Voice OS — Aether Gateway Hook.
 *
 * Manages the connection to the local Aether Gateway (Python backend).
 * Handles:
 *  - WebSocket lifecycle
 *  - Challenge-response handshake (Ed25519)
 *  - Binary audio routing (PCM)
 *  - Heartbeat/Tick synchronization
 */

export type GatewayStatus =
    | "disconnected"
    | "connecting"
    | "handshaking"
    | "connected"
    | "error";

interface AetherGatewayReturn {
    status: GatewayStatus;
    connect: () => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
}

// Development credentials (Ephemeral Keypair for local auth)
// Seeded for predictable "Architect" identity in local dev
const DEV_SEED = new Uint8Array([
    0xda, 0xee, 0x51, 0x93, 0x22, 0xd2, 0x1a, 0x56, 0x5d, 0x6e, 0x76, 0xe1, 0xba, 0x92, 0x7c, 0xf6,
    0x61, 0x6e, 0x9e, 0x47, 0x72, 0x8a, 0x6b, 0x8b, 0xa3, 0x3d, 0x90, 0x8d, 0xb2, 0x4f, 0x5f, 0x6c
]);
const keyPair = nacl.sign.keyPair.fromSeed(DEV_SEED);
const DEV_SECRET_KEY = keyPair.secretKey;
const DEV_PUBLIC_KEY = keyPair.publicKey;

function toHex(data: Uint8Array): string {
    return Array.from(data).map(b => b.toString(16).padStart(2, "0")).join("");
}

export function useAetherGateway(url = "ws://localhost:18789"): AetherGatewayReturn {
    const [status, setStatus] = useState<GatewayStatus>("disconnected");
    const wsRef = useRef<WebSocket | null>(null);
    const store = useAetherStore();
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        setStatus("connecting");

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

                    // 1. Handshake Challenge
                    if (msg.type === "challenge") {
                        console.log("✦ Received handshake challenge:", msg.challenge);

                        // Sign the challenge string
                        const challengeBytes = new TextEncoder().encode(msg.challenge);
                        const signatureBytes = nacl.sign.detached(challengeBytes, DEV_SECRET_KEY);

                        const response = {
                            type: "response",
                            client_id: toHex(DEV_PUBLIC_KEY),
                            signature: toHex(signatureBytes),
                            capabilities: ["audio_streaming", "telemetry"]
                        };
                        ws.send(JSON.stringify(response));
                    }

                    // 2. Handshake Success (Ack)
                    else if (msg.type === "ack") {
                        console.log("✦ Gateway Handshake Successful");
                        setStatus("connected");
                        store.addSystemLog("[Gateway] Authenticated successfully.");
                    }

                    // 3. Error
                    else if (msg.type === "error") {
                        console.error("Gateway error:", msg.message);
                        store.addSystemLog(`[Gateway] Error: ${msg.message}`);
                        if (msg.fatal) setStatus("error");
                    }

                    // 4. Tick (Heartbeat)
                    else if (msg.type === "tick") {
                        // Optional: measure latency
                        const now = Date.now();
                        const serverTime = msg.timestamp * 1000;
                        // store.setTelemetry({}, now - serverTime);
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
    }, [url, store]);

    const sendAudio = useCallback((pcm: ArrayBuffer) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || status !== "connected") return;

        // Send raw binary
        ws.send(pcm);
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

    return { status, connect, disconnect, sendAudio, onAudioResponse };
}
