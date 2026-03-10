"use client";
/**
 * Aether Voice OS — Gemini Live Session Hook (V3 Multimodal).
 *
 * Manages the WebSocket connection to Gemini's Multimodal Live API.
 * Features:
 *   - Real-time PCM audio streaming (16kHz Int16 → base64)
 *   - Vision frame streaming (JPEG base64 at 1 FPS)
 *   - Tool call support for silent UI orchestration
 *   - Gapless audio response handling with base64 decode
 *   - Barge-in (interruption) support
 *   - Transcript extraction from model text parts
 *   - Real RTT latency measurement (rolling average)
 *   - Auto-reconnection with exponential backoff
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useAetherStore } from "../store/useAetherStore";
import { GeminiToolCall } from "../store/types";

export type SessionStatus =
    | "disconnected"
    | "connecting"
    | "connected"
    | "listening"
    | "speaking"
    | "thinking"
    | "error";

/** Tool call from Gemini */
export interface GeminiToolCall {
    name: string;
    args: Record<string, unknown>;
    id: string;
}

interface GeminiLiveReturn {
    status: SessionStatus;
    latencyMs: number;
    connect: () => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    sendVisionFrame: (b64Jpeg: string) => void;
    sendToolResponse: (callId: string, result: Record<string, unknown>) => void;
    onAudioResponse: React.MutableRefObject<
        ((audio: ArrayBuffer) => void) | null
    >;
    onInterrupt: React.MutableRefObject<(() => void) | null>;
    onTranscript: React.MutableRefObject<
        ((text: string, role: "user" | "ai") => void) | null
    >;
    onToolCall: React.MutableRefObject<
        ((toolCall: GeminiToolCall) => void) | null
    >;
}

// The Aether Gateway handles the direct connection to Google's API
const AETHER_GATEWAY_URL =
    process.env.NEXT_PUBLIC_AETHER_GATEWAY_URL || "ws://localhost:18789";

const MODEL = "models/gemini-2.5-flash-preview-native-audio-dialog";

// Reconnection constants
// Reconnection constants
const RECONNECT_DELAYS = [1000, 2000, 5000, 15000, 30000]; // Exponential backoff
const MAX_RETRIES = 5;

export function useGeminiLive(): GeminiLiveReturn {
    const [status, setStatus] = useState<SessionStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);

    const wsRef = useRef<WebSocket | null>(null);
    const setupDone = useRef(false);
    const intentionalClose = useRef(false);
    const retryCount = useRef(0);
    const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Callback refs for zero-rerender wiring
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const onInterrupt = useRef<(() => void) | null>(null);
    const onTranscript = useRef<
        ((text: string, role: "user" | "ai") => void) | null
    >(null);
    const onToolCall = useRef<
        ((toolCall: GeminiToolCall) => void) | null
    >(null);

    // Latency tracking
    const lastSendTime = useRef(0);
    const latencyHistory = useRef<number[]>([]);
    const waitingForResponse = useRef(false);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        intentionalClose.current = false;
        setStatus("connecting");

        try {
            // The Gateway URL doesn't need the API key; the kernel handles auth.
            const url = AETHER_GATEWAY_URL;
            const ws = new WebSocket(url);
            ws.binaryType = "arraybuffer";
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("✦ Gemini Live WebSocket opened");
                retryCount.current = 0; // Reset retries on successful connect

                // Send setup message with model config + tools
                const setup = {
                    setup: {
                        model: MODEL,
                        generation_config: {
                            response_modalities: ["AUDIO"],
                            speech_config: {
                                voice_config: {
                                    prebuilt_voice_config: {
                                        voice_name: "Aoede",
                                    },
                                },
                            },
                        },
                        system_instruction: {
                            parts: [
                                {
                                    text:
                                        "You are Aether — a calm, wise AI ambient companion with vision capabilities. " +
                                        "You can SEE the user's screen through periodic vision frames. " +
                                        "You speak clearly and concisely. You are helpful, warm, and deeply knowledgeable. " +
                                        "Keep responses short and conversational for voice interaction. " +
                                        "Never use markdown, bullet points, or formatting — speak naturally. " +
                                        "\n\nSILENT TOOLS: You have tools to show information on the user's screen " +
                                        "WITHOUT speaking. Use show_silent_hint to display a brief helpful hint " +
                                        "(e.g., spotted an error, a suggestion). Use show_code_suggestion for code fixes. " +
                                        "Use these tools proactively when you notice something in the screen — " +
                                        "you do NOT need to speak when using tools. The hint appears as a card on the UI.",
                                },
                            ],
                        },
                        tools: [
                            {
                                function_declarations: [
                                    {
                                        name: "show_silent_hint",
                                        description:
                                            "Display a silent hint card on the user's screen without speaking. " +
                                            "Use when you notice something helpful in the user's screen.",
                                        parameters: {
                                            type: "OBJECT",
                                            properties: {
                                                text: {
                                                    type: "STRING",
                                                    description: "The hint text to display (max 120 chars)",
                                                },
                                                priority: {
                                                    type: "STRING",
                                                    enum: ["info", "warning", "suggestion"],
                                                    description: "The priority level of the hint",
                                                },
                                            },
                                            required: ["text"],
                                        },
                                    },
                                    {
                                        name: "show_code_suggestion",
                                        description:
                                            "Display a code suggestion card on the user's screen. " +
                                            "Use when you spot a bug, improvement, or fix in the visible code.",
                                        parameters: {
                                            type: "OBJECT",
                                            properties: {
                                                title: {
                                                    type: "STRING",
                                                    description: "Short title for the suggestion",
                                                },
                                                code: {
                                                    type: "STRING",
                                                    description: "The code snippet or fix",
                                                },
                                                explanation: {
                                                    type: "STRING",
                                                    description: "Brief explanation of the suggestion",
                                                },
                                            },
                                            required: ["title", "code"],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                };

                ws.send(JSON.stringify(setup));
            };

            ws.onmessage = (event: MessageEvent) => {
                if (typeof event.data === "string") {
                    const msg = JSON.parse(event.data);
                    handleTextMessage(msg);
                } else if (event.data instanceof ArrayBuffer) {
                    // Raw audio bytes from Gemini
                    measureLatency();
                    if (onAudioResponse.current) {
                        onAudioResponse.current(event.data);
                    }
                }
            };

            ws.onerror = (err) => {
                console.error("Gemini WS error:", err);
                setStatus("error");
            };

            ws.onclose = (e) => {
                console.log("Gemini WS closed:", e.code, e.reason);
                wsRef.current = null;
                setupDone.current = false;

                if (!intentionalClose.current) {
                    // Unexpected close — attempt reconnection
                    attemptReconnect();
                } else {
                    setStatus("disconnected");
                }
            };
        } catch (err) {
            console.error("Failed to connect:", err);
            setStatus("error");
            attemptReconnect();
        }
    }, []);

    const handleTextMessage = useCallback(
        (msg: Record<string, any>) => {
            const messageHandlers: Record<string, (data: any) => void> = {
                setupComplete: () => {
                    console.log("✦ Gemini Live session ready");
                    setStatus("listening");
                    setupDone.current = true;
                },
                serverContent: (sc: any) => {
                    if (sc.modelTurn?.parts) {
                        setStatus("speaking");
                        for (const part of sc.modelTurn.parts) {
                            if (part.inlineData?.data) {
                                measureLatency();
                                const b64 = part.inlineData.data;
                                const binary = atob(b64);
                                const bytes = new Uint8Array(binary.length);
                                for (let i = 0; i < binary.length; i++) {
                                    bytes[i] = binary.charCodeAt(i);
                                }
                                onAudioResponse.current?.(bytes.buffer);
                            }

                            // ─── Real-time Transcript Overlay ────────────────
                            if (part.text) {
                                const setTranscriptStream = useAetherStore.getState().setTranscriptStream;
                                // If turn is complete, this is likely a 'final' part
                                if (sc.turnComplete) {
                                    setTranscriptStream({
                                        final: part.text,
                                        interim: '',
                                        confidence: sc.confidence || 1.0,
                                        latencyMs: lastLatency.current
                                    });
                                } else {
                                    setTranscriptStream({
                                        interim: part.text,
                                        confidence: sc.confidence || 1.0,
                                        latencyMs: lastLatency.current
                                    });
                                }

                                if (onTranscript.current) {
                                    onTranscript.current(part.text, "ai");
                                }
                            }
                        }
                    }
                    if (sc.turnComplete) {
                        setStatus("listening");
                        waitingForResponse.current = false;
                    }
                    if (sc.interrupted) {
                        console.log("⚡ Barge-in detected");
                        setStatus("listening");
                        waitingForResponse.current = false;
                        onInterrupt.current?.();
                    }
                },
                toolCall: (tc: any) => {
                    if (tc.functionCalls) {
                        for (const fc of tc.functionCalls) {
                            const call: GeminiToolCall = {
                                name: fc.name,
                                args: fc.args || {},
                                id: fc.id || crypto.randomUUID(),
                            };
                            console.log("🔧 Tool call:", call.name, call.args);
                            onToolCall.current?.(call);
                        }
                    }
                },
                clientContentId: (id: string) => {
                    console.log(`✅ Received Frame ACK: ${id}`);
                }
            };

            // O(1) Dispatch
            for (const [key, handler] of Object.entries(messageHandlers)) {
                if (msg[key]) {
                    handler(msg[key]);
                    return;
                }
            }

            logger.debug("Unhandled text message:", msg);
        },
        [measureLatency]
    );

    const sendAudio = useCallback((pcm: ArrayBuffer) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || !setupDone.current)
            return;

        // Mark send time for latency measurement
        if (!waitingForResponse.current) {
            lastSendTime.current = performance.now();
            waitingForResponse.current = true;
        }

        // Encode PCM as base64 (chunked to avoid stack overflow)
        const bytes = new Uint8Array(pcm);
        let b64 = "";
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
            b64 += String.fromCharCode(
                ...bytes.subarray(i, i + chunkSize)
            );
        }
        b64 = btoa(b64);

        const msg = {
            realtimeInput: {
                mediaChunks: [
                    {
                        mimeType: "audio/pcm;rate=16000",
                        data: b64,
                    },
                ],
            },
        };

        ws.send(JSON.stringify(msg));
    }, []);

    /** Send a vision frame (WebP base64) to Gemini */
    const sendVisionFrame = useCallback((b64WebP: string) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || !setupDone.current)
            return;

        // Add a frameId to track the vision frame
        const frameId = crypto.randomUUID();

        const msg = {
            realtimeInput: {
                mediaChunks: [
                    {
                        mimeType: "image/webp",
                        data: b64WebP,
                    },
                ],
                // Surface frame IDs in WS payload
                clientContentId: frameId
            },
        };

        ws.send(JSON.stringify(msg));
        console.log(`📸 Sent Vision Frame: ${frameId}`);
    }, []);

    /** Send a tool response back to Gemini after executing a tool call */
    const sendToolResponse = useCallback(
        (callId: string, result: Record<string, unknown>) => {
            const ws = wsRef.current;
            if (!ws || ws.readyState !== WebSocket.OPEN) return;

            const msg = {
                toolResponse: {
                    functionResponses: [
                        {
                            id: callId,
                            name: callId,
                            response: result,
                        },
                    ],
                },
            };

            ws.send(JSON.stringify(msg));
        },
        []
    );

    /** Calculate RTT and update rolling average */
    const measureLatency = useCallback(() => {
        if (
            waitingForResponse.current &&
            lastSendTime.current > 0
        ) {
            const rtt = performance.now() - lastSendTime.current;
            waitingForResponse.current = false;

            // Rolling average (keep last 10 measurements)
            const history = latencyHistory.current;
            history.push(rtt);
            if (history.length > 10) history.shift();

            const avg =
                history.reduce((a, b) => a + b, 0) / history.length;
            setLatencyMs(Math.round(avg));
        }
    }, []);

    /** Reconnect with exponential backoff */
    const attemptReconnect = useCallback(() => {
        if (retryCount.current >= MAX_RETRIES) {
            console.log("⚠ Max reconnection attempts reached");
            setStatus("error");
            return;
        }

        const delay =
            RECONNECT_DELAYS[
            Math.min(retryCount.current, RECONNECT_DELAYS.length - 1)
            ];
        retryCount.current += 1;

        console.log(
            `↻ Reconnecting in ${delay}ms (attempt ${retryCount.current}/${MAX_RETRIES})`
        );
        setStatus("connecting");

        retryTimer.current = setTimeout(() => {
            connect();
        }, delay);
    }, [connect]);

    const disconnect = useCallback(() => {
        intentionalClose.current = true;
        if (retryTimer.current) {
            clearTimeout(retryTimer.current);
            retryTimer.current = null;
        }
        wsRef.current?.close();
        wsRef.current = null;
        setupDone.current = false;
        retryCount.current = 0;
        waitingForResponse.current = false;
        setStatus("disconnected");
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            disconnect();
        };
    }, [disconnect]);

    return {
        status,
        latencyMs,
        connect,
        disconnect,
        sendAudio,
        sendVisionFrame,
        sendToolResponse,
        onAudioResponse,
        onInterrupt,
        onTranscript,
        onToolCall,
    };
}
