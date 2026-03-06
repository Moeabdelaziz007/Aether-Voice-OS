"use client";

import { useRef } from "react";
import { useAetherGateway, type GatewayStatus } from "@/hooks/useAetherGateway";

export type SessionStatus =
  | "disconnected"
  | "connecting"
  | "connected"
  | "listening"
  | "speaking"
  | "thinking"
  | "error";

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
  sendToolResponse: (_callId: string, _result: Record<string, unknown>) => void;
  onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
  onInterrupt: React.MutableRefObject<(() => void) | null>;
  onTranscript: React.MutableRefObject<((text: string, role: "user" | "ai") => void) | null>;
  onToolCall: React.MutableRefObject<((toolCall: GeminiToolCall) => void) | null>;
}

function toSessionStatus(status: GatewayStatus): SessionStatus {
  if (status === "connected") return "listening";
  if (status === "handshaking") return "connecting";
  return status;
}

/**
 * @deprecated Use useAetherGateway directly for all new transport integrations.
 */
export function useGeminiLive(): GeminiLiveReturn {
  const gateway = useAetherGateway();
  const onToolCall = useRef<((toolCall: GeminiToolCall) => void) | null>(null);

  const onTranscript = {
    get current() {
      const current = gateway.onTranscript.current;
      if (!current) return null;
      return (text: string, role: "user" | "ai") => current(text, role === "ai" ? "agent" : role);
    },
    set current(handler: ((text: string, role: "user" | "ai") => void) | null) {
      if (!handler) {
        gateway.onTranscript.current = null;
        return;
      }
      gateway.onTranscript.current = (text, role) => {
        handler(text, role === "agent" ? "ai" : role);
      };
    },
  } as React.MutableRefObject<((text: string, role: "user" | "ai") => void) | null>;

  return {
    status: toSessionStatus(gateway.status),
    latencyMs: gateway.latencyMs,
    connect: gateway.connect,
    disconnect: gateway.disconnect,
    sendAudio: gateway.sendAudio,
    sendVisionFrame: gateway.sendVisionFrame,
    sendToolResponse: () => {},
    onAudioResponse: gateway.onAudioResponse,
    onInterrupt: gateway.onInterrupt,
    onTranscript,
    onToolCall,
  };
}
