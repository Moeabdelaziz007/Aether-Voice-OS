"use client";
/**
 * Aether Voice OS — Live Agent Page.
 *
 * /live — Fullscreen auto-listening voice agent.
 * No buttons. Opens → requests mic → connects to Gemini → talks.
 * A single neon line reacts to your voice and the AI's voice.
 *
 * This is the Wispr Flow experience powered by Gemini.
 */

import { useEffect, useRef, useState } from "react";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useGeminiLive, type SessionStatus } from "@/hooks/useGeminiLive";
import AetherLine from "@/components/AetherLine";

// Map session status to line status
function toLineStatus(
    session: SessionStatus,
    pipeline: string
): "idle" | "listening" | "speaking" | "connecting" | "error" {
    if (session === "error" || pipeline === "error") return "error";
    if (session === "connecting" || pipeline === "starting") return "connecting";
    if (session === "speaking") return "speaking";
    if (session === "listening" || session === "connected") return "listening";
    return "idle";
}

const STATUS_LABELS: Record<string, string> = {
    idle: "Initializing...",
    connecting: "Connecting to Aether...",
    listening: "Listening",
    speaking: "Aether is speaking",
    error: "Connection error — reload to retry",
};

export default function LivePage() {
    const audio = useAudioPipeline();
    const gemini = useGeminiLive();
    const [initialized, setInitialized] = useState(false);
    const hasStarted = useRef(false);

    const lineStatus = toLineStatus(gemini.status, audio.state);

    // Auto-launch on page load
    useEffect(() => {
        if (hasStarted.current) return;
        hasStarted.current = true;

        const init = async () => {
            try {
                // Start audio pipeline (requests mic)
                await audio.start();
                // Connect to Gemini Live
                await gemini.connect();
                setInitialized(true);
            } catch (err) {
                console.error("Init error:", err);
            }
        };

        // Small delay to ensure page is rendered
        const timer = setTimeout(init, 500);
        return () => clearTimeout(timer);
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // Wire PCM chunks from mic → Gemini
    useEffect(() => {
        audio.onPCMChunk.current = (pcm: ArrayBuffer) => {
            gemini.sendAudio(pcm);
        };
    }, [audio, gemini]);

    // Wire audio responses from Gemini → speaker
    useEffect(() => {
        gemini.onAudioResponse.current = (audioData: ArrayBuffer) => {
            audio.playPCM(audioData);
        };
    }, [audio, gemini]);

    // Handle barge-in (interrupt)
    useEffect(() => {
        gemini.onInterrupt.current = () => {
            // Playback interruption is handled internally
            console.log("⚡ Interrupt — stopping playback");
        };
    }, [gemini]);

    return (
        <div
            style={{
                position: "fixed",
                inset: 0,
                backgroundColor: "#050508",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                overflow: "hidden",
                fontFamily:
                    "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
            }}
        >
            {/* Background radial glow */}
            <div
                style={{
                    position: "absolute",
                    inset: 0,
                    background:
                        lineStatus === "speaking"
                            ? "radial-gradient(ellipse 80% 50% at 50% 50%, rgba(188, 19, 254, 0.06) 0%, transparent 70%)"
                            : "radial-gradient(ellipse 80% 50% at 50% 50%, rgba(0, 243, 255, 0.04) 0%, transparent 70%)",
                    transition: "background 0.8s ease",
                    pointerEvents: "none",
                }}
            />

            {/* Title */}
            <div
                style={{
                    position: "absolute",
                    top: "10%",
                    textAlign: "center",
                    zIndex: 10,
                }}
            >
                <h1
                    style={{
                        fontSize: "1.1rem",
                        fontWeight: 300,
                        letterSpacing: "0.3em",
                        textTransform: "uppercase",
                        color: "rgba(255, 255, 255, 0.2)",
                        margin: 0,
                    }}
                >
                    Aether
                </h1>
            </div>

            {/* Main visualizer area */}
            <div
                style={{
                    width: "85%",
                    maxWidth: "900px",
                    height: "200px",
                    position: "relative",
                }}
            >
                <AetherLine
                    micLevel={audio.micLevel}
                    speakerLevel={audio.speakerLevel}
                    status={lineStatus}
                />
            </div>

            {/* Status text */}
            <div
                style={{
                    position: "absolute",
                    bottom: "12%",
                    textAlign: "center",
                    zIndex: 10,
                }}
            >
                <p
                    style={{
                        fontSize: "0.85rem",
                        fontWeight: 400,
                        letterSpacing: "0.15em",
                        color:
                            lineStatus === "error"
                                ? "rgba(255, 80, 80, 0.7)"
                                : lineStatus === "speaking"
                                    ? "rgba(188, 19, 254, 0.5)"
                                    : "rgba(255, 255, 255, 0.2)",
                        transition: "color 0.5s ease",
                        margin: 0,
                    }}
                >
                    {STATUS_LABELS[lineStatus] || "..."}
                </p>

                {/* Subtle breathing dot */}
                {lineStatus === "listening" && (
                    <div
                        style={{
                            width: 6,
                            height: 6,
                            borderRadius: "50%",
                            backgroundColor: "#00f3ff",
                            margin: "12px auto 0",
                            animation: "breathe 2s ease-in-out infinite",
                        }}
                    />
                )}
            </div>

            {/* Breathing animation */}
            <style>{`
        @keyframes breathe {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.3); }
        }
      `}</style>
        </div>
    );
}
