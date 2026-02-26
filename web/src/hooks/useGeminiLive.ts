"use client";
/**
 * Aether Voice OS — Gemini Live Session Hook.
 *
 * Manages the WebSocket connection to Gemini's Multimodal Live API.
 * Uses the official google-genai SDK pattern:
 *   - Opens a live session via WebSocket
 *   - Sends PCM audio chunks as realtime_input
 *   - Receives audio responses + handles interruptions (barge-in)
 *
 * Since the browser google-genai SDK is not yet publicly available
 * for Live sessions, we implement the WebSocket protocol directly
 * following the documented message format.
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type SessionStatus =
    | "disconnected"
    | "connecting"
    | "connected"
    | "listening"
    | "speaking"
    | "error";

interface GeminiLiveReturn {
    status: SessionStatus;
    connect: () => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    onAudioResponse: React.MutableRefObject<
        ((audio: ArrayBuffer) => void) | null
    >;
    onInterrupt: React.MutableRefObject<(() => void) | null>;
}

const GEMINI_WS_URL =
    "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent";

const API_KEY = process.env.NEXT_PUBLIC_GEMINI_KEY || "";
const MODEL = "models/gemini-2.5-flash-preview-native-audio-dialog";

export function useGeminiLive(): GeminiLiveReturn {
    const [status, setStatus] = useState<SessionStatus>("disconnected");
    const wsRef = useRef<WebSocket | null>(null);
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const onInterrupt = useRef<(() => void) | null>(null);
    const setupDone = useRef(false);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;
        setStatus("connecting");

        try {
            const url = `${GEMINI_WS_URL}?key=${API_KEY}`;
            const ws = new WebSocket(url);
            ws.binaryType = "arraybuffer";
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("✦ Gemini Live WebSocket opened");

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
                                        "and conversational for voice interaction.",
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
                setStatus("disconnected");
                wsRef.current = null;
                setupDone.current = false;
            };
        } catch (err) {
            console.error("Failed to connect:", err);
            setStatus("error");
        }
    }, []);

    const handleTextMessage = useCallback((msg: Record<string, unknown>) => {
        // Setup complete acknowledgement
        if (msg.setupComplete) {
            console.log("✦ Gemini Live session ready");
            setStatus("listening");
            setupDone.current = true;
            return;
        }

        // Server content with audio data
        const sc = msg.serverContent as Record<string, unknown> | undefined;
        if (sc) {
            // Model is speaking
            const modelTurn = sc.modelTurn as Record<string, unknown> | undefined;
            if (modelTurn?.parts) {
                setStatus("speaking");
                const parts = modelTurn.parts as Array<Record<string, unknown>>;
                for (const part of parts) {
                    const inlineData = part.inlineData as
                        | Record<string, unknown>
                        | undefined;
                    if (inlineData?.data) {
                        // Decode base64 audio
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
                }
            }

            // Turn complete — back to listening
            if (sc.turnComplete) {
                setStatus("listening");
            }

            // Interrupted (barge-in)
            if (sc.interrupted) {
                console.log("⚡ Barge-in detected");
                setStatus("listening");
                if (onInterrupt.current) {
                    onInterrupt.current();
                }
            }
        }
    }, []);

    const sendAudio = useCallback((pcm: ArrayBuffer) => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || !setupDone.current) return;

        // Encode PCM as base64
        const bytes = new Uint8Array(pcm);
        let b64 = "";
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
            b64 += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
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

    const disconnect = useCallback(() => {
        wsRef.current?.close();
        wsRef.current = null;
        setupDone.current = false;
        setStatus("disconnected");
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            disconnect();
        };
    }, [disconnect]);

    return { status, connect, disconnect, sendAudio, onAudioResponse, onInterrupt };
}
