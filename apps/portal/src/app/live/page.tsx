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

import { useState, useEffect, useRef } from "react";
import { useAetherGateway, type GatewayStatus } from "@/hooks/useAetherGateway";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useAetherStore } from "@/store/useAetherStore";
import AetherLine from "@/components/AetherLine";

// Map session status to line status
function toLineStatus(
    status: GatewayStatus,
    engineState: string,
    pipeline: string
): "idle" | "listening" | "speaking" | "connecting" | "error" {
    if (status === "error" || pipeline === "error") return "error";
    if (status === "connecting" || status === "handshaking" || pipeline === "starting") return "connecting";
    if (engineState === "SPEAKING") return "speaking";
    if (engineState === "LISTENING" || status === "connected") return "listening";
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
    const gateway = useAetherGateway();
    const engineState = useAetherStore((s) => s.engineState);
    const [initialized, setInitialized] = useState(false);
    const hasStarted = useRef(false);
    const lastLatency = useRef(0);

    const lineStatus = toLineStatus(gateway.status, engineState, audio.state);

    // Auto-launch on page load
    useEffect(() => {
        if (hasStarted.current) return;
        hasStarted.current = true;

        const init = async () => {
            try {
                // Start audio pipeline (requests mic)
                await audio.start();
                // Connect to Aether Gateway
                await gateway.connect();
                setInitialized(true);
            } catch (err) {
                console.error("Init error:", err);
            }
        };

        // Small delay to ensure page is rendered
        const timer = setTimeout(init, 500);
        return () => clearTimeout(timer);
    }, []);

    // ─── Adaptive Vision Pulse ───────────────────────────────────
    const [visionInterval, setVisionInterval] = useState(1000); // 1 FPS default
    const visionTimerRef = useRef<NodeJS.Timeout | null>(null);

    // Monitor transcripts for trigger words
    useEffect(() => {
        const originalTranscript = gateway.onTranscript.current;
        gateway.onTranscript.current = (text, role) => {
            if (originalTranscript) originalTranscript(text, role);

            if (role === 'user') {
                const lowerText = text.toLowerCase();
                const triggers = ['look', 'see', 'this', 'show'];
                if (triggers.some(t => lowerText.includes(t))) {
                    console.log("🚀 Vision Pulse: Trigger detected! Increasing to 5 FPS.");
                    setVisionInterval(200); // 5 FPS

                    // Reset to 1 FPS after 10 seconds
                    setTimeout(() => {
                        console.log("🐢 Vision Pulse: Resetting to 1 FPS.");
                        setVisionInterval(1000);
                    }, 10000);
                }
            }
        };
    }, [gateway]);

    // Vision Capture Loop
    useEffect(() => {
        if (gateway.status !== 'connected') return;

        const captureFrame = async () => {
            // Note: In a production Electron app, this would call a native screenshot API.
            // Here we simulate the capture and send it to Gemini.
            // Use the consolidated gateway for vision frames
            try {
                // gateway.sendVisionFrame(mockBase64); 
            } catch (err) {
                console.error("Vision capture failed:", err);
            }

            visionTimerRef.current = setTimeout(captureFrame, visionInterval);
        };

        captureFrame();

        return () => {
            if (visionTimerRef.current) clearTimeout(visionTimerRef.current);
        };
    }, [gateway.status, visionInterval]);

    // Wire PCM chunks from mic → Gateway
    useEffect(() => {
        audio.onPCMChunk.current = (pcm: ArrayBuffer) => {
            gateway.sendAudio(pcm);
        };
    }, [audio, gateway]);

    // Wire audio responses from Gateway → speaker
    useEffect(() => {
        gateway.onAudioResponse.current = (audioData: ArrayBuffer) => {
            audio.playPCM(audioData);
        };
    }, [audio, gateway]);

    // Handle barge-in (interrupt)
    useEffect(() => {
        gateway.onInterrupt.current = () => {
            // Playback interruption is handled internally
            console.log("⚡ Interrupt — stopping playback");
        };
    }, [gateway]);

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
                <AetherLine />
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

            {/* Google Gemini attribution — visible during demo */}
            <div
                style={{
                    position: "absolute",
                    bottom: "3%",
                    left: "50%",
                    transform: "translateX(-50%)",
                    zIndex: 10,
                }}
            >
                <p
                    style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: "9px",
                        letterSpacing: "0.2em",
                        color: "rgba(255, 255, 255, 0.12)",
                        margin: 0,
                    }}
                >
                    Aether Voice OS · Powered by Gemini Live API
                </p>
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
