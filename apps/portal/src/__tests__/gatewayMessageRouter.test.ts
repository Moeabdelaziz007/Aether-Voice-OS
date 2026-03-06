import { describe, expect, it, vi } from "vitest";
import { gatewayMessageHandlers, routeGatewayMessage } from "@/lib/gatewayMessageRouter";

function createContext() {
  const store = {
    setSessionStartTime: vi.fn(),
    addSystemLog: vi.fn(),
    setLatencyMs: vi.fn(),
    setEngineState: vi.fn(),
    addTranscriptMessage: vi.fn(),
    setTelemetry: vi.fn(),
    addNeuralEvent: vi.fn(),
    setVisionPulse: vi.fn(),
    setVisionActive: vi.fn(),
    setPredictedGoal: vi.fn(),
    setMutation: vi.fn(),
    addSilentHint: vi.fn(),
    setAudioLevels: vi.fn(),
    setActiveSoul: vi.fn(),
    speakerLevel: 0,
  } as any;

  return {
    store,
    latencyMs: 42,
    setLatencyMs: vi.fn(),
    setStatus: vi.fn(),
    onInterrupt: vi.fn(),
    onTranscript: vi.fn(),
  };
}

describe("gatewayMessageRouter", () => {
  it("routes handshake ack", () => {
    const ctx = createContext();
    routeGatewayMessage({ type: "connect.ack" }, ctx as any);

    expect(ctx.setStatus).toHaveBeenCalledWith("connected");
    expect(ctx.store.setSessionStartTime).toHaveBeenCalled();
  });

  it("routes transcript payload", () => {
    const ctx = createContext();
    routeGatewayMessage({ type: "transcript", role: "user", text: "hello" }, ctx as any);

    expect(ctx.store.addTranscriptMessage).toHaveBeenCalledWith({ role: "user", content: "hello" });
    expect(ctx.onTranscript).toHaveBeenCalledWith("hello", "user");
  });

  it("routes interruption event", () => {
    const ctx = createContext();
    routeGatewayMessage({ type: "interruption" }, ctx as any);
    expect(ctx.onInterrupt).toHaveBeenCalled();
  });

  it("routes tick event to latency", () => {
    const ctx = createContext();
    const nowSec = Math.floor(Date.now() / 1000);
    routeGatewayMessage({ type: "tick", timestamp: nowSec }, ctx as any);

    expect(ctx.setLatencyMs).toHaveBeenCalled();
    expect(ctx.store.setLatencyMs).toHaveBeenCalled();
  });

  it("exports a stable handler registry", () => {
    expect(gatewayMessageHandlers["engine_state"]).toBeTypeOf("function");
    expect(gatewayMessageHandlers["tool_result"]).toBeTypeOf("function");
  });
});
