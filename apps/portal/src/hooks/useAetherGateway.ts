"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import nacl from "tweetnacl";
import { encode, decode } from "@msgpack/msgpack";
import { useAetherStore } from "../store/useAetherStore";

export type GatewayStatus = "disconnected" | "connecting" | "handshaking" | "connected" | "reconnecting" | "error";
export type GazeVector = [number, number, number];

export interface GatewayAPI {
    status: GatewayStatus; latencyMs: number; connect: (t?: string) => Promise<void>; disconnect: () => void;
    sendAudio: (pcm: Uint8Array | ArrayBuffer) => void; sendIntent: (i: string, l?: 1 | 2 | 3) => Promise<void>;
    sendUIStateSync: (w: any[]) => void; sendVisionFrame: (f: string) => void;
    sendForgeCommit: (dna: any) => Promise<void>;
    sendClawInject: (instructions: string, rationales?: string[]) => Promise<void>;
    onAudioResponse: React.MutableRefObject<((a: ArrayBuffer) => void) | null>;
    onTranscript: React.MutableRefObject<((text: string, role: "user" | "ai") => void) | null>;
    onToolCall: React.MutableRefObject<((toolCall: any) => void) | null>;
    onInterrupt: React.MutableRefObject<(() => void) | null>;
    isConnected: boolean;
    isAudioActive: boolean;
    toggleAudio: () => void;
}

export type GatewayEvent =
    | { type: "tick"; timestamp: number }
    | { type: "engine_state"; payload: { state: string } }
    | { type: "transcript"; payload: { role: string; text: string } }
    | { type: "affective_score"; payload: { frustration: number; valence: number; arousal: number; engagement: number } }
    | { type: "vision_pulse"; payload: { timestamp: string } }
    | { type: "tool_result"; payload: { tool_name: string; status: string } }
    | { type: "task_pulse"; payload: { taskId: string; phase: string } }
    | { type: "repair_state"; payload: { status: any; message: string; log: string } }
    | { type: "GAZE_SYNC"; payload: { vector: GazeVector; intent: string } }
    | { type: "vad"; payload: { active: boolean; energy_db: number; ts_ms: number } }
    | { type: "interrupt_latency"; payload: { ms: number; ts_ms: number } };

export function useAetherGateway(url = process.env.NEXT_PUBLIC_AETHER_GATEWAY_URL || "ws://localhost:18789"): GatewayAPI {
    const [status, setStatus] = useState<GatewayStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);
    const store = useAetherStore(), wsRef = useRef<WebSocket | null>(null), abortRef = useRef<AbortController | null>(null);
    const bp = useRef(new BackpressureController()), rm = useRef(new ReconnectionManager(() => connect()));
    const batcher = useRef<PCMStreamBatcher | null>(null);
    const onAudioResponse = useRef<((a: ArrayBuffer) => void) | null>(null);
    const onTranscript = useRef<((text: string, role: "user" | "ai") => void) | null>(null);
    const onToolCall = useRef<((toolCall: any) => void) | null>(null);
    const onInterrupt = useRef<(() => void) | null>(null);

    const connect = useCallback(async (token?: string) => {
        if (wsRef.current?.readyState === 1) return;
        abortRef.current?.abort(); abortRef.current = new AbortController();
        setStatus(rm.current.attempt > 0 ? "reconnecting" : "connecting");
        const hk = new HandshakeManager();
        const sig = abortRef.current.signal;
        try {
            const ws = new WebSocket(url); ws.binaryType = "arraybuffer"; wsRef.current = ws;
            batcher.current = new PCMStreamBatcher(ws, bp.current);
            ws.onopen = () => { rm.current.reset(); setStatus("handshaking"); };
            ws.onmessage = async (e) => {
                if (sig.aborted) return;

                let m;
                if (e.data instanceof ArrayBuffer) {
                    try {
                        m = decode(new Uint8Array(e.data));
                        // If it successfully decodes and has a type, it's a msgpack event, not raw audio
                        if (!m || typeof m !== 'object' || !("type" in m)) {
                            return onAudioResponse.current?.(e.data);
                        }
                    } catch (err) {
                        // Decoding failed, so it must be raw audio
                        return onAudioResponse.current?.(e.data);
                    }
                } else {
                    m = JSON.parse(e.data);
                }

                if (m.type === "connect.challenge") {
                    const auth = hk.generateResponse(m.challenge);
                    ws.send(JSON.stringify({ type: "connect.response", client_id: auth.client_id, signature: auth.signature, id_token: token, capabilities: ["audio_streaming", "msgpack"] }));
                } else if (m.type === "connect.ack") { setStatus("connected"); store.setSessionStartTime(Date.now()); }
                else if (m.type === "AUDIO_ACK") { bp.current.ack(); }
                else if (m.type === "tool_call") { onToolCall.current?.(m.payload); }
                else if (m.type === "interrupt") { onInterrupt.current?.(); }
                else if (m.type === "error") {
                    store.addError({
                        code: m.payload.code || "UNKNOWN_ERROR",
                        message: m.payload.message || "An unexpected error occurred in the gateway.",
                        severity: m.payload.severity || "medium",
                        retryable: m.payload.retryable ?? true
                    });
                    store.addTerminalLog('ERROR', `Gateway Error: ${m.payload.code} - ${m.payload.message}`);
                }
                else processEvent(m as GatewayEvent, store, setLatencyMs, onTranscript);
            };
            ws.onclose = (ev) => {
                hk.zeroize();
                if (ev.code !== 1000 && ev.code !== 1001) { setStatus("reconnecting"); rm.current.trigger(); } else setStatus("disconnected");
            };
            ws.onerror = () => { hk.zeroize(); setStatus("error"); };
        } catch { setStatus("error"); }
    }, [url, store]);

    const disconnect = useCallback(() => { abortRef.current?.abort(); wsRef.current?.close(1000); wsRef.current = null; setStatus("disconnected"); rm.current.stop(); }, []);
    const sendAudio = useCallback((pcm: Uint8Array | ArrayBuffer) => batcher.current?.add(pcm instanceof ArrayBuffer ? new Uint8Array(pcm) : pcm), []);
    const sendIntent = useCallback(async (raw_input: string, level = 1) => {
        const ws = wsRef.current;
        if (ws?.readyState !== 1) {
            store.addError({
                code: "GATEWAY_DISCONNECTED",
                message: "Cannot send intent. Gateway is not connected.",
                severity: "high",
                retryable: true
            });
            return;
        }
        try {
            const hk = new HandshakeManager();
            const signature = hk.signIntent(raw_input);
            ws.send(encode({ type: "INTENT", intent_id: crypto.randomUUID(), level, raw_input, signature }));
            hk.zeroize();
        } catch (e) {
            store.addError({
                code: "INTENT_SEND_FAILED",
                message: "Failed to transmit intent through the gateway.",
                severity: "medium",
                retryable: true
            });
        }
    }, [store]);
    const sendUIStateSync = useCallback((w: any[]) => wsRef.current?.readyState === 1 && wsRef.current.send(encode({ type: "UI_STATE_SYNC", payload: { active_widgets: w } })), []);

    // Add vision uploader with backoff mechanism to prevent flooding connection
    const visionBackoff = useRef(0);
    const lastVisionSent = useRef(0);
    const [isAudioActive, setIsAudioActive] = useState(false);
    const toggleAudio = useCallback(() => {
        setIsAudioActive(prev => !prev);
        // If we are starting audio, we might want to notify the engine
        if (!isAudioActive) {
            store.addTerminalLog('SYS', 'Neural Audio Stream Initialized.');
        } else {
            store.addTerminalLog('SYS', 'Neural Audio Stream Hibernated.');
        }
    }, [isAudioActive, store]);

    const sendVisionFrame = useCallback((f: string) => {
        if (wsRef.current?.readyState !== 1) return;

        const now = Date.now();
        if (now - lastVisionSent.current < visionBackoff.current) {
            // Drop frame if we are within the backoff period
            return;
        }

        try {
            // Buffer size check could go here if using BackpressureController for vision too
            wsRef.current.send(encode({ type: "VISION_FRAME", payload: { frame: f, id: crypto.randomUUID() } }));
            lastVisionSent.current = now;

            // Success, reduce backoff down to 1s minimum
            visionBackoff.current = Math.max(1000, visionBackoff.current * 0.8);

            // Pre-emptively update store for immediate UI feedback
            store.setVisionActive(true);
        } catch (e) {
            // On failure, increase backoff up to 10s maximum
            visionBackoff.current = Math.min(10000, Math.max(2000, visionBackoff.current * 1.5));
            console.warn("Vision upload failed, increasing backoff to", visionBackoff.current);
            store.addError({
                code: "VISION_UPLOAD_FAILED",
                message: "Failed to upload vision frame. Retrying with backoff.",
                severity: "low",
                retryable: true
            });
        }
    }, [store]);
    const sendForgeCommit = useCallback(async (dna: any) => {
        const ws = wsRef.current;
        if (ws?.readyState !== 1) {
            store.addError({ code: "FORGE_OFFLINE", message: "Cannot commit DNA. Forge gateway is offline.", severity: "high", retryable: true });
            return;
        }
        try {
            ws.send(encode({ type: "FORGE_COMMIT", payload: { dna, timestamp: Date.now() } }));
        } catch (e) {
            store.addError({ code: "FORGE_COMMIT_FAILED", message: "Failed to transmit DNA blueprint.", severity: "medium", retryable: true });
        }
    }, [store]);
    const sendClawInject = useCallback(async (instructions: string, rationales: string[] = []) => {
        const ws = wsRef.current;
        if (ws?.readyState !== 1) {
            store.addError({ code: "CLAW_OFFLINE", message: "ClawHub injection failed: Gateway offline.", severity: "high", retryable: true });
            return;
        }
        try {
            ws.send(encode({ type: "CLAW_INJECT", payload: { instructions, rationales, timestamp: Date.now() } }));
        } catch (e) {
            store.addError({ code: "CLAW_INJECT_FAILED", message: "Failed to transmit ClawHub instructions.", severity: "medium", retryable: true });
        }
    }, [store]);

    useEffect(() => () => disconnect(), [disconnect]);
    return { status, latencyMs, connect, disconnect, sendAudio, sendIntent, sendUIStateSync, sendVisionFrame, sendForgeCommit, sendClawInject, onAudioResponse, onTranscript, onToolCall, onInterrupt, isConnected: status === "connected", isAudioActive, toggleAudio };
}

function processEvent(m: GatewayEvent, s: any, sl: (l: number) => void, ot?: React.MutableRefObject<((t: string, r: "user" | "ai") => void) | null>) {
    if (m.type === "tick") { const rtt = Math.abs(Date.now() - m.timestamp * 1000); sl(rtt); s.setLatencyMs(rtt); return; }
    const p = (m as any).payload; if (!p) return;
    switch (m.type) {
        case "engine_state": s.setEngineState(p.state); break;
        case "transcript":
            s.addTranscriptMessage({ role: p.role || "ai", content: p.text });
            // Direct injection into Forge Store for zero-latency UI updates
            try {
                const { useForgeStore } = require("../store/useForgeStore");
                if (useForgeStore.getState().activeStep !== 'review') {
                    useForgeStore.getState().setTranscript(p.text);
                }
            } catch (e) { /* Forge store might not be loaded in all views */ }

            ot?.current?.(p.text, (p.role as "user" | "ai") || "ai");
            break;
        case "affective_score": s.setTelemetry(p, 0); break;
        case "vision_pulse": s.setVisionPulse(p.timestamp); s.setVisionActive(true); break;
        case "tool_result": s.addToolCall({ toolName: p.tool_name, status: p.status }); break;
        case "task_pulse": s.setTaskPulse({ ...p, timestamp: Date.now() }); break;
        case "repair_state": s.setRepairState({ ...p, timestamp: Date.now() }); break;
        case "GAZE_SYNC": s.setGazeTarget(p.vector); break;
        case "vad":
            s.setAvatarState(p.active ? 'ListeningActive' : 'ListeningWaiting');
            // Notify Forge Store of VAD status
            try {
                const { useForgeStore } = require("../store/useForgeStore");
                useForgeStore.getState().setListening(p.active);
                if (p.active) useForgeStore.getState().setVoiceMode('listening');
            } catch (e) { }
            break;
        case "interrupt_latency":
            s.setTelemetry({ ...s.telemetry, interruptLatency: p.ms }, 0);
            break;
    }
}

class BackpressureController {
    HIGH = 65536;
    MAX_UNACKED = 15;
    unacked = 0;

    isThrottled(ba: number) {
        return ba > this.HIGH || this.unacked >= this.MAX_UNACKED;
    }

    send() { this.unacked++; }
    ack() { this.unacked = Math.max(0, this.unacked - 1); }
}

class ReconnectionManager {
    attempt = 0; timer: any = null; constructor(private onR: () => void) { }
    MAX_ATTEMPTS = 10;
    trigger() {
        this.stop();
        if (this.attempt >= this.MAX_ATTEMPTS) {
            console.error("❌ Aether Gateway: Max reconnection attempts reached.");
            return;
        }
        const delay = Math.min(1000 * Math.pow(1.5, this.attempt++) + Math.random() * 500, 15000);
        console.log(`↻ Aether Gateway Reconnecting in ${Math.round(delay)}ms (Attempt ${this.attempt}/${this.MAX_ATTEMPTS})`);
        this.timer = setTimeout(() => this.onR(), delay);
    }
    stop() { if (this.timer) clearTimeout(this.timer); }
    reset() { this.attempt = 0; this.stop(); }
}

class HandshakeManager {
    private kp: nacl.SignKeyPair | null = null;

    constructor() {
        // Enforce ephemeral keys: generate a fresh keypair on every connection
        // Do not persist Ed25519 seed in localStorage to avoid credential theft via XSS
        const seed = nacl.randomBytes(32);
        this.kp = nacl.sign.keyPair.fromSeed(seed);

        // Zeroize the seed buffer immediately after usage
        seed.fill(0);
    }

    generateResponse(ch: string) {
        if (!this.kp) throw new Error("Keypair already zeroized");
        const sig = nacl.sign.detached(this.fh(ch), this.kp.secretKey);
        return { client_id: this.th(this.kp.publicKey), signature: this.th(sig) };
    }

    signIntent(i: string) {
        if (!this.kp) throw new Error("Keypair already zeroized");
        return this.th(nacl.sign.detached(new TextEncoder().encode(i), this.kp.secretKey));
    }

    zeroize() {
        // Secure wipe of private key material
        if (this.kp) {
            const sk = this.kp.secretKey as Uint8Array;
            sk.fill(0);
            this.kp = null;
        }
    }

    private th(d: Uint8Array) { return Array.from(d).map(b => b.toString(16).padStart(2, '0')).join(''); }
    private fh(h: string) { const b = new Uint8Array(h.length / 2); for (let i = 0; i < h.length; i += 2) b[i / 2] = parseInt(h.slice(i, i + 2), 16); return b; }
}

class PCMStreamBatcher {
    private b: Uint8Array[] = []; timer: any = null; constructor(private ws: WebSocket, private bp: BackpressureController) { }
    add(p: Uint8Array) { this.b.push(p); if (!this.timer) this.timer = setTimeout(() => this.flush(), 40); }
    private flush() {
        this.timer = null; if (this.ws.readyState !== 1 || this.bp.isThrottled(this.ws.bufferedAmount)) { this.b = []; return; }
        const merged = new Uint8Array(this.b.reduce((a, v) => a + v.length, 0)); let o = 0;
        for (const c of this.b) { merged.set(c, o); o += c.length; }
        this.ws.send(merged); this.b = [];
        this.bp.send(); // Track unacked chunk
    }
}
