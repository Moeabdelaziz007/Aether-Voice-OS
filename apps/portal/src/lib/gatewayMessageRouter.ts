import { useAetherStore } from "@/store/useAetherStore";

export interface GatewayMessageRouterContext {
  store: ReturnType<typeof useAetherStore.getState>;
  latencyMs: number;
  setLatencyMs: (latencyMs: number) => void;
  setStatus: (status: "disconnected" | "connecting" | "handshaking" | "connected" | "error") => void;
  onInterrupt?: () => void;
  onTranscript?: (text: string, role: "user" | "agent") => void;
}

export type GatewayMessage = Record<string, any>;

export function routeGatewayMessage(msg: GatewayMessage, ctx: GatewayMessageRouterContext): void {
  const handler = gatewayMessageHandlers[msg.type];
  if (!handler) {
    return;
  }

  handler(msg, ctx);
}

type GatewayMessageHandler = (msg: GatewayMessage, ctx: GatewayMessageRouterContext) => void;

export const gatewayMessageHandlers: Record<string, GatewayMessageHandler> = {
  "connect.ack": (_msg, ctx) => {
    ctx.setStatus("connected");
    ctx.store.setSessionStartTime(Date.now());
    ctx.store.addSystemLog("[Gateway] Authenticated successfully.");
  },

  error: (msg, ctx) => {
    ctx.store.addSystemLog(`[Gateway] Error: ${msg.message}`);
    if (msg.fatal) {
      ctx.setStatus("error");
    }
  },

  tick: (msg, ctx) => {
    const now = Date.now();
    const serverTime = Number(msg.timestamp || 0) * 1000;
    const measuredLatency = Math.abs(now - serverTime);
    ctx.setLatencyMs(measuredLatency);
    ctx.store.setLatencyMs(measuredLatency);
  },

  engine_state: (msg, ctx) => {
    ctx.store.setEngineState(msg.state);
    ctx.store.addSystemLog(`[Engine] State → ${msg.state}`);
  },

  transcript: (msg, ctx) => {
    const role = msg.role === "user" ? "user" : "agent";
    const content = msg.text || msg.content || "";

    ctx.store.addTranscriptMessage({ role, content });
    ctx.onTranscript?.(content, role);
  },

  interruption: (_msg, ctx) => {
    ctx.onInterrupt?.();
  },

  affective_score: (msg, ctx) => {
    ctx.store.setTelemetry(
      {
        frustration: msg.frustration,
        valence: msg.valence,
        arousal: msg.arousal,
        engagement: msg.engagement,
        pitch: msg.pitch,
        rate: msg.rate,
      },
      ctx.latencyMs,
    );
  },

  audio_telemetry: (msg) => {
    useAetherStore.getState().setAudioLevels(msg.payload?.rms || 0, msg.payload?.gain || 0);
  },

  repair_state: (msg) => {
    useAetherStore.getState().setRepairState({
      status: msg.payload?.status || msg.status || "diagnosing",
      message: msg.payload?.message || msg.message || "",
      log: msg.payload?.log || msg.log || "",
      timestamp: Date.now(),
    });
  },

  neural_event: (msg, ctx) => {
    ctx.store.addNeuralEvent({
      fromAgent: msg.from_agent || "AetherCore",
      toAgent: msg.to_agent || "Unknown",
      task: msg.task || msg.description || "",
      status: msg.status || "active",
    });
  },

  vision_pulse: (msg, ctx) => {
    ctx.store.setVisionPulse(msg.timestamp || new Date().toISOString());
    ctx.store.setVisionActive(true);
  },

  intent_update: (msg, ctx) => {
    if (msg.memory_update?.predicted_next_goal) {
      ctx.store.setPredictedGoal(msg.memory_update.predicted_next_goal);
    }
  },

  mutation_event: (msg, ctx) => {
    ctx.store.setMutation(msg.description || msg.mutation || "Unknown mutation");
  },

  tool_result: (msg, ctx) => {
    ctx.store.addSilentHint({
      id: crypto.randomUUID(),
      text: msg.tool_name || "Tool completed",
      code: msg.code,
      explanation: msg.result || msg.message,
      priority: msg.priority || "info",
      type: msg.code ? "code" : "hint",
      timestamp: Date.now(),
    });
    ctx.store.addSystemLog(`[Tool] ${msg.tool_name}: ${msg.status || "done"}`);
  },

  telemetry: (msg, ctx) => {
    if (msg.metric_name === "paralinguistics") {
      ctx.store.setTelemetry(
        {
          pitch: msg.metadata?.pitch_hz,
          spectralCentroid: msg.metadata?.spectral_centroid,
          frustration: msg.metadata?.frustration,
        },
        ctx.latencyMs,
      );
      ctx.store.setAudioLevels(msg.metadata?.volume || 0, ctx.store.speakerLevel);
    } else if (msg.metric_name === "noise_floor") {
      ctx.store.setTelemetry({ noiseFloor: msg.value }, ctx.latencyMs);
    }
  },

  soul_handoff: (msg, ctx) => {
    const target = msg.target_soul || msg.target_agent_id || "AetherCore";
    ctx.store.setActiveSoul(target);
    ctx.store.addNeuralEvent({
      fromAgent: msg.from_soul || msg.source_agent_id || "AetherCore",
      toAgent: target,
      task: msg.task_goal || msg.reason || "Context handover",
      status: "active",
    });
    ctx.store.addSystemLog(`[Hive] Handover → ${target}`);
  },

  handover: (msg, ctx) => {
    gatewayMessageHandlers.soul_handoff(msg, ctx);
  },
};
