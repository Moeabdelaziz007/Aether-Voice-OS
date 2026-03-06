"use client";
/**
 * Aether Voice OS — Live Agent Page.
 */

import { useEffect, useRef, useState } from "react";
import { useAudioPipeline } from "@/hooks/useAudioPipeline";
import { useAetherGateway, type GatewayStatus } from "@/hooks/useAetherGateway";
import AetherLine from "@/components/AetherLine";

function toLineStatus(
  session: GatewayStatus,
  pipeline: string,
): "idle" | "listening" | "speaking" | "connecting" | "error" {
  if (session === "error" || pipeline === "error") return "error";
  if (session === "connecting" || session === "handshaking" || pipeline === "starting") return "connecting";
  if (pipeline === "active" && session === "connected") return "listening";
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
  const [initialized, setInitialized] = useState(false);
  const hasStarted = useRef(false);

  const lineStatus = toLineStatus(gateway.status, audio.state);

  useEffect(() => {
    if (hasStarted.current) return;
    hasStarted.current = true;

    const init = async () => {
      try {
        await audio.start();
        await gateway.connect();
        setInitialized(true);
      } catch (err) {
        console.error("Init error:", err);
      }
    };

    const timer = setTimeout(init, 500);
    return () => clearTimeout(timer);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!initialized) return;

    audio.onPCMChunk.current = (pcm: ArrayBuffer) => {
      gateway.sendAudio(pcm);
    };

    return () => {
      audio.onPCMChunk.current = null;
    };
  }, [audio, gateway, initialized]);

  useEffect(() => {
    gateway.onAudioResponse.current = (audioData: ArrayBuffer) => {
      audio.playPCM(audioData);
    };

    return () => {
      gateway.onAudioResponse.current = null;
    };
  }, [audio, gateway]);

  useEffect(() => {
    gateway.onInterrupt.current = () => {
      audio.stopPlayback();
    };

    return () => {
      gateway.onInterrupt.current = null;
    };
  }, [audio, gateway]);

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
          Aether Voice OS · Powered by Aether Gateway
        </p>
      </div>

      <style>{`
        @keyframes breathe {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.3); }
        }
      `}</style>
    </div>
  );
}
