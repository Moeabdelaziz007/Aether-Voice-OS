"use client";
/**
 * Aether Voice OS — Gemini Live Session Hook.
 *
 * Manages the WebSocket connection to Gemini's Multimodal Live API.
 * Features:
 *   - Real-time PCM audio streaming (16kHz Int16 → base64)
 *   - Gapless audio response handling with base64 decode
 *   - Barge-in (interruption) support
 *   - Transcript extraction from model text parts
 *   - Real RTT latency measurement (rolling average)
 *   - Auto-reconnection with exponential backoff
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type SessionStatus =
    | "disconnected"
    | "connecting"
    | "connected"
    | "listening"
    | "speaking"
    | "thinking"
    | "error";

interface GeminiLiveReturn {
    status: SessionStatus;
    latencyMs: number;
    connect: () => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    onAudioResponse: React.MutableRefObject<
        ((audio: ArrayBuffer) => void) | null
    >;
    onInterrupt: React.MutableRefObject<(() => void) | null>;
    onTranscript: React.MutableRefObject<
        ((text: string, role: "user" | "ai") => void) | null
    >;
}

const GEMINI_WS_URL =
    "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent";

const API_KEY = process.env.NEXT_PUBLIC_GEMINI_KEY || "";
const MODEL = "models/gemini-2.5-flash-preview-native-audio-dialog";

// Reconnection constants
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000]; // Exponential backoff
const MAX_RETRIES = 3;

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

    // Latency tracking
    const lastSendTime = useRef(0);
    const latencyHistory = useRef<number[]>([]);
    const waitingForResponse = useRef(false);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        intentionalClose.current = false;
        setStatus("connecting");

        try {
            const url = `${GEMINI_WS_URL}?key=${API_KEY}`;
            const ws = new WebSocket(url);
            ws.binaryType = "arraybuffer";
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("✦ Gemini Live WebSocket opened");
                retryCount.current = 0; // Reset retries on successful connect

                // Send setup message with model config
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
                                        "You are Aether — a calm, wise AI voice companion. " +
                                        "You speak clearly and concisely. You are helpful, " +
                                        "warm, and deeply knowledgeable. Keep responses short " +
                                        "and conversational for voice interaction. " +
                                        "Never use markdown, bullet points, or formatting — " +
                                        "speak naturally as in a real conversation.",
                                },
                            ],
                        },
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
        (msg: Record<string, unknown>) => {
            // Setup complete acknowledgement
            if (msg.setupComplete) {
                console.log("✦ Gemini Live session ready");
                setStatus("listening");
                setupDone.current = true;
                return;
            }

            // Server content with audio/text data
            const sc = msg.serverContent as
                | Record<string, unknown>
                | undefined;
            if (sc) {
                const modelTurn = sc.modelTurn as
                    | Record<string, unknown>
                    | undefined;
                if (modelTurn?.parts) {
                    setStatus("speaking");
                    const parts = modelTurn.parts as Array<
                        Record<string, unknown>
                    >;

                    for (const part of parts) {
                        // Handle audio data
                        const inlineData = part.inlineData as
                            | Record<string, unknown>
                            | undefined;
                        if (inlineData?.data) {
                            measureLatency();
                            const b64 = inlineData.data as string;
                            const binary = atob(b64);
                            const bytes = new Uint8Array(binary.length);
                            for (let i = 0; i < binary.length; i++) {
                                bytes[i] = binary.charCodeAt(i);
                            }
                            if (onAudioResponse.current) {
                                onAudioResponse.current(bytes.buffer);
                            }
                        }

                        // Handle text transcript
                        if (part.text && typeof part.text === "string") {
                            if (onTranscript.current) {
                                onTranscript.current(
                                    part.text as string,
                                    "ai"
                                );
                            }
                        }
                    }
                }

                // Turn complete — back to listening
                if (sc.turnComplete) {
                    setStatus("listening");
                    waitingForResponse.current = false;
                }

                // Interrupted (barge-in)
                if (sc.interrupted) {
                    console.log("⚡ Barge-in detected");
                    setStatus("listening");
                    waitingForResponse.current = false;
                    if (onInterrupt.current) {
                        onInterrupt.current();
                    }
                }
            }
        },
        []
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
        onAudioResponse,
        onInterrupt,
        onTranscript,
    };
}
