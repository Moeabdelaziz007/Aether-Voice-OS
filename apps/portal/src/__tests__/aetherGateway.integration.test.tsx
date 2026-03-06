import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useAetherGateway } from "@/hooks/useAetherGateway";

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  static OPEN = 1;
  static CLOSED = 3;

  url: string;
  readyState = 0;
  binaryType = "blob";
  sent: Array<string | ArrayBuffer> = [];

  onopen: ((ev: Event) => void) | null = null;
  onmessage: ((ev: MessageEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  send(data: string | ArrayBuffer) {
    this.sent.push(data);
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({ code: 1000, reason: "closed" } as CloseEvent);
  }

  open() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.({} as Event);
  }

  emitJson(payload: Record<string, any>) {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent);
  }

  emitAudio(buffer: ArrayBuffer) {
    this.onmessage?.({ data: buffer } as MessageEvent);
  }
}

describe("useAetherGateway integration", () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.stubGlobal("WebSocket", MockWebSocket as any);
    vi.stubGlobal("crypto", {
      randomUUID: () => "id-1",
      subtle: { digest: vi.fn(async () => new ArrayBuffer(32)) },
    } as any);
    vi.useFakeTimers();
  });

  it("covers handshake, reconnect, transcript, audio and interruption", async () => {
    const { result } = renderHook(() => useAetherGateway("ws://test"));

    await act(async () => {
      await result.current.connect();
    });

    const ws1 = MockWebSocket.instances[0];
    expect(ws1).toBeDefined();

    act(() => {
      ws1.open();
      ws1.emitJson({ type: "connect.challenge", challenge: "aa" });
    });
    expect(ws1.sent[0]).toContain("connect.response");

    act(() => {
      ws1.emitJson({ type: "connect.ack" });
    });
    expect(result.current.status).toBe("connected");

    const transcriptSpy = vi.fn();
    const interruptSpy = vi.fn();
    const audioSpy = vi.fn();
    result.current.onTranscript.current = transcriptSpy;
    result.current.onInterrupt.current = interruptSpy;
    result.current.onAudioResponse.current = audioSpy;

    act(() => {
      ws1.emitJson({ type: "transcript", role: "user", text: "hello" });
      ws1.emitJson({ type: "interruption" });
      ws1.emitAudio(new Int16Array([1, 2]).buffer);
    });

    expect(transcriptSpy).toHaveBeenCalledWith("hello", "user");
    expect(interruptSpy).toHaveBeenCalled();
    expect(audioSpy).toHaveBeenCalled();

    act(() => {
      ws1.onclose?.({ code: 1006, reason: "drop" } as CloseEvent);
      vi.advanceTimersByTime(1000);
    });

    expect(MockWebSocket.instances.length).toBe(2);
  });
});
