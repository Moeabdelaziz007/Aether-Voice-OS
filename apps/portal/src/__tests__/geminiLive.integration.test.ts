import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useAetherGateway } from "@/hooks/useAetherGateway";

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  static OPEN = 1;
  static CLOSED = 3;

  readyState = 0;
  binaryType = "blob";
  sent: Array<string | ArrayBuffer> = [];

  onopen: ((ev: Event) => void) | null = null;
  onmessage: ((ev: MessageEvent) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;

  constructor(_url: string) {
    MockWebSocket.instances.push(this);
  }

  send(data: string | ArrayBuffer) {
    this.sent.push(data);
  }

  open() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.({} as Event);
  }

  close(code = 1000, reason = "closed") {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({ code, reason } as CloseEvent);
  }

  emitJson(data: Record<string, unknown>) {
    this.onmessage?.({ data: JSON.stringify(data) } as MessageEvent);
  }

  emitAudio(data: ArrayBuffer) {
    this.onmessage?.({ data } as MessageEvent);
  }
}

describe("Aether gateway integration", () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", MockWebSocket as any);
  });

  it("covers handshake, reconnect, transcript, audio and interruption using one hook API", async () => {
    const { result } = renderHook(() => useAetherGateway("ws://localhost:9999"));

    await act(async () => {
      await result.current.connect();
    });

    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.open();
      ws.emitJson({ type: "connect.challenge", challenge: "00" });
      ws.emitJson({ type: "connect.ack" });
    });

    expect(result.current.status).toBe("connected");
    expect(String(ws.sent[0])).toContain("connect.response");

    const transcriptSpy = vi.fn();
    const interruptSpy = vi.fn();
    const audioSpy = vi.fn();
    result.current.onTranscript.current = transcriptSpy;
    result.current.onInterrupt.current = interruptSpy;
    result.current.onAudioResponse.current = audioSpy;

    act(() => {
      ws.emitJson({ type: "transcript", role: "user", text: "hello world" });
      ws.emitJson({ type: "interruption" });
      ws.emitAudio(new Int16Array([1, 2, 3]).buffer);
    });

    expect(transcriptSpy).toHaveBeenCalledWith("hello world", "user");
    expect(interruptSpy).toHaveBeenCalledTimes(1);
    expect(audioSpy).toHaveBeenCalledTimes(1);

    act(() => {
      ws.close(1006, "network");
      vi.advanceTimersByTime(1000);
    });

    expect(MockWebSocket.instances.length).toBe(2);
  });
});
