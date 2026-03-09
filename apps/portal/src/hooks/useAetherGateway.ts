"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import nacl from "tweetnacl";
import { useAetherStore } from "../store/useAetherStore";

// ============================================================================
// Types - Extended for new API
// ============================================================================

export type GatewayStatus =
    | "disconnected"
    | "connecting"
    | "handshaking"
    | "connected"
    | "reconnecting"
    | "error";

export interface GatewayOptions {
    url?: string;
    highWaterMark?: number;
    reconnectBaseDelay?: number;
    reconnectMaxDelay?: number;
    onMetrics?: (metrics: GatewayMetrics) => void;
}

export interface GatewayMetrics {
    rtt: number;
    sendQueueDepth: number;
    droppedFrames: number;
    reconnectionCount: number;
    bufferedAmount: number;
}

export interface GatewayAPI {
    status: GatewayStatus;
    latencyMs: number;
    connect: (idToken?: string) => Promise<void>;
    disconnect: () => void;
    sendAudio: (pcm: ArrayBuffer) => void;
    sendVisionFrame: (base64: string) => void;
    sendIntent: (input: string, level?: 1 | 2 | 3) => Promise<void>;
    sendUIStateSync: (widgets: any[]) => void;
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>;
    isConnected: () => boolean;
}

// ============================================================================
// BackpressureController - Manages send queue with thresholds
// ============================================================================

class BackpressureController {
    private highWaterMark: number;
    private sendQueue: Array<() => void> = [];
    private draining: boolean = false;
    private drainPromise: Promise<void> | null = null;
    private resolveDrain: (() => void) | null = null;

    constructor(highWaterMark: number = 65536) {
        this.highWaterMark = highWaterMark;
    }

    /**
     * Check if we should throttle sends based on bufferedAmount
     */
    shouldThrottle(bufferedAmount: number): boolean {
        return bufferedAmount > this.highWaterMark;
    }

    /**
     * Queue a send function to be executed when buffer drains
     */
    async sendQueued(fn: () => void): Promise<void> {
        if (!this.shouldThrottle(0)) {
            fn();
            return;
        }

        return new Promise((resolve) => {
            this.sendQueue.push(() => {
                fn();
                resolve();
            });
            this.scheduleDrain();
        });
    }

    /**
     * Schedule drain when buffer empties
     */
    private scheduleDrain(): void {
        if (this.draining) return;
        this.draining = true;

        const checkDrain = () => {
            if (this.sendQueue.length === 0) {
                this.draining = false;
                this.resolveDrain?.();
                return;
            }
            setTimeout(checkDrain, 50);
        };
        checkDrain();
    }

    /**
     * Get current queue depth
     */
    getQueueDepth(): number {
        return this.sendQueue.length;
    }

    /**
     * Clear all queued sends
     */
    clear(): void {
        this.sendQueue = [];
        this.draining = false;
    }
}

// ============================================================================
// ReconnectionManager - Exponential backoff with jitter
// ============================================================================

class ReconnectionManager {
    private baseDelay: number;
    private maxDelay: number;
    private attemptCount: number = 0;
    private reconnectionCount: number = 0;
    private isReconnecting: boolean = false;

    constructor(baseDelay: number = 250, maxDelay: number = 5000) {
        this.baseDelay = baseDelay;
        this.maxDelay = maxDelay;
    }

    /**
     * Calculate delay with exponential backoff and jitter
     */
    getDelay(): number {
        const exponentialDelay = this.baseDelay * Math.pow(2, this.attemptCount);
        const jitter = Math.random() * 0.3 * exponentialDelay;
        return Math.min(exponentialDelay + jitter, this.maxDelay);
    }

    /**
     * Record an attempt and get the delay
     */
    recordAttempt(): number {
        this.attemptCount++;
        return this.getDelay();
    }

    /**
     * Reset on successful connection
     */
    reset(): void {
        this.attemptCount = 0;
    }

    /**
     * Get total reconnection count
     */
    getReconnectionCount(): number {
        return this.reconnectionCount;
    }

    /**
     * Start reconnecting
     */
    startReconnecting(): void {
        this.isReconnecting = true;
        this.reconnectionCount++;
    }

    /**
     * Check if currently reconnecting
     */
    isInReconnectMode(): boolean {
        return this.isReconnecting;
    }

    /**
     * Stop reconnecting mode
     */
    stopReconnecting(): void {
        this.isReconnecting = false;
    }
}

// ============================================================================
// Crypto Helpers - Ed25519 Key Management
// ============================================================================

const STORAGE_KEY = "aether_ed25519_seed";

function getOrCreateKeypair(): nacl.SignKeyPair {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            const seed = new Uint8Array(JSON.parse(stored));
            return nacl.sign.keyPair.fromSeed(seed);
        }
    } catch { /* localStorage may not be available (SSR) */ }

    const seed = nacl.randomBytes(32);
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(seed)));
    } catch { /* ignore */ }

    return nacl.sign.keyPair.fromSeed(seed);
}

function toHex(data: Uint8Array): string {
    return Array.from(data).map(b => b.toString(16).padStart(2, "0")).join("");
}

function fromHex(hex: string): Uint8Array {
    const normalized = hex.length % 2 === 0 ? hex : `0${hex}`;
    const bytes = new Uint8Array(normalized.length / 2);
    for (let i = 0; i < normalized.length; i += 2) {
        bytes[i / 2] = Number.parseInt(normalized.slice(i, i + 2), 16);
    }
    return bytes;
}

// ============================================================================
// Event Handlers - Extracted for clarity
// ============================================================================

type EventHandler = (msg: any, store: any, latencyMs: number, setLatencyMs: (n: number) => void) => void;

/**
 * Setup event router - demultiplexes JSON messages by type
 */
function setupEventRouter(
    ws: WebSocket,
    store: any,
    latencyMs: number,
    setLatencyMs: (n: number) => void,
    onAudioResponse: React.MutableRefObject<((audio: ArrayBuffer) => void) | null>
): void {
    const getCinematicPayload = (msg: any) => {
        const payload = msg.payload ?? msg;
        const protocolVersion = Number(
            payload?.protocol_version ?? payload?.protocolVersion ?? msg?.protocol_version ?? msg?.protocolVersion ?? 1
        );
        if (!Number.isFinite(protocolVersion) || protocolVersion !== 1) {
            store.addSystemLog(`[Protocol] Ignored ${msg.type} with version ${String(protocolVersion)}`);
            return null;
        }
        return payload;
    };

    // Event handlers map
    const handlers: Record<string, EventHandler> = {
        "connect.challenge": (msg, store) => {
            // Handled in setupAuthHandshake
        },
        "connect.ack": (msg, store) => {
            console.log("✦ Gateway Handshake Successful");
            store.setSessionStartTime(Date.now());
            store.addSystemLog("[Gateway] Authenticated successfully.");
        },
        "error": (msg, store) => {
            console.error("Gateway error:", msg.message);
            store.addSystemLog(`[Gateway] Error: ${msg.message}`);
        },
        "tick": (msg, store, _, setLatencyMs) => {
            const now = Date.now();
            const serverTime = msg.timestamp * 1000;
            const measuredLatency = Math.abs(now - serverTime);
            setLatencyMs(measuredLatency);
            store.setLatencyMs(measuredLatency);
        },
        "engine_state": (msg, store) => {
            store.setEngineState(msg.state);
            store.addSystemLog(`[Engine] State → ${msg.state}`);
        },
        "transcript": (msg, store) => {
            store.addTranscriptMessage({
                role: msg.role === "user" ? "user" : "agent",
                content: msg.text || msg.content || "",
            });
        },
        "affective_score": (msg, store, latencyMs) => {
            store.setTelemetry({
                frustration: msg.frustration,
                valence: msg.valence,
                arousal: msg.arousal,
                engagement: msg.engagement,
                pitch: msg.pitch,
                rate: msg.rate,
            }, latencyMs);
        },
        "audio_telemetry": (msg, store) => {
            useAetherStore.getState().setAudioLevels(msg.payload.rms || 0, msg.payload.gain || 0);
        },
        "repair_state": (msg, store) => {
            useAetherStore.getState().setRepairState({
                status: msg.payload?.status || msg.status || 'diagnosing',
                message: msg.payload?.message || msg.message || '',
                log: msg.payload?.log || msg.log || '',
                timestamp: Date.now(),
            });
        },
        "neural_event": (msg, store) => {
            store.addNeuralEvent({
                fromAgent: msg.from_agent || "AetherCore",
                toAgent: msg.to_agent || "Unknown",
                task: msg.task || msg.description || "",
                status: msg.status || "active",
            });
        },
        "vision_pulse": (msg, store) => {
            store.setVisionPulse(msg.timestamp || new Date().toISOString());
            store.setVisionActive(true);
        },
        "intent_update": (msg, store) => {
            if (msg.memory_update?.predicted_next_goal) {
                store.setPredictedGoal(msg.memory_update.predicted_next_goal);
            }
        },
        "mutation_event": (msg, store) => {
            store.setMutation(msg.description || msg.mutation || "Unknown mutation");
        },
        "tool_result": (msg, store) => {
            store.addSilentHint({
                id: crypto.randomUUID(),
                text: msg.tool_name || "Tool completed",
                code: msg.code,
                explanation: msg.result || msg.message,
                priority: msg.priority || "info",
                type: msg.code ? "code" : "hint",
                timestamp: Date.now(),
            });
            store.addSystemLog(`[Tool] ${msg.tool_name}: ${msg.status || "done"}`);
        },
        "task_pulse": (msg, store) => {
            const payload = getCinematicPayload(msg);
            if (!payload) return;
            const taskId = payload.task_id || payload.taskId || "task-unknown";
            store.setTaskPulse({
                taskId,
                phase: payload.phase || "EXECUTING",
                action: payload.action || "task_execution",
                vibe: payload.vibe || "focusing",
                thought: payload.thought || "",
                avatarTarget: payload.avatar_target || payload.avatarTarget || "center",
                intensity: Number(payload.intensity ?? 0.6),
                latencyMs: payload.latency_ms || payload.latencyMs,
                timestamp: Date.now(),
            });
            store.setAvatarCinematicState(payload.avatar_state || payload.avatarState || "EXECUTING");
            store.pushMissionLog({
                taskId,
                title: payload.action || "Neural Operation",
                detail: payload.thought || payload.message || "",
                status: payload.phase === "FAILED" ? "failed" : payload.phase === "COMPLETED" ? "completed" : "in-progress",
            });
        },
        "avatar_state": (msg, store) => {
            const payload = getCinematicPayload(msg);
            if (!payload) return;
            const nextState = payload.state || payload.avatar_state || "IDLE";
            store.setAvatarCinematicState(nextState);
            if (payload.reason) {
                store.addSystemLog(`[Avatar] ${nextState} — ${payload.reason}`);
            }
        },
        "workspace_state": (msg, store) => {
            const payload = getCinematicPayload(msg);
            if (!payload) return;
            store.applyWorkspaceState(payload);
            const appId = String(payload.app_id || payload.appId || "").toLowerCase();
            if (appId.includes("notes")) {
                const latestState = useAetherStore.getState();
                const notesWidget = latestState.activeWidgets.find((widget: any) => widget.type === "notes_planet");
                if ((payload.action === "materialize_app" || payload.action === "focus_app") && !notesWidget) {
                    store.addWidget("notes_planet", { appId });
                }
                if (payload.action === "collapse_app" && notesWidget) {
                    store.removeWidget(notesWidget.id);
                }
            }
        },
        "mirror_frame": (msg, store) => {
            const payload = getCinematicPayload(msg);
            if (!payload) return;
            const eventKind = payload.event_kind || payload.eventKind || "capture";
            store.addMirrorFrameEvent({
                action: payload.action || "capture_frame",
                eventKind,
                selector: payload.selector || undefined,
                text: payload.text || undefined,
                url: payload.url || undefined,
                x: typeof payload.x === "number" ? payload.x : undefined,
                y: typeof payload.y === "number" ? payload.y : undefined,
                latencyMs: Number(payload.latency_ms || payload.latencyMs || 0) || undefined,
            });
            if (payload.latency_ms || payload.latencyMs) {
                store.pushVoyagerLatencyRow({
                    label: `${eventKind}:${payload.action || "action"}`,
                    latencyMs: Number(payload.latency_ms || payload.latencyMs || 0),
                    status: "ok",
                });
            }
        },
        "task_timeline_item": (msg, store) => {
            const payload = getCinematicPayload(msg);
            if (!payload) return;
            store.pushMissionLog({
                taskId: payload.task_id || payload.taskId || undefined,
                title: payload.title || "Mission Step",
                detail: payload.detail || payload.description || "",
                status: payload.status || "in-progress",
            });
        },
        "telemetry": (msg, store, latencyMs) => {
            if (msg.metric_name === "paralinguistics") {
                store.setTelemetry({
                    pitch: msg.metadata?.pitch_hz,
                    spectralCentroid: msg.metadata?.spectral_centroid,
                    frustration: msg.metadata?.frustration,
                }, latencyMs);
                store.setAudioLevels(msg.metadata?.volume || 0, store.speakerLevel);
            } else if (msg.metric_name === "noise_floor") {
                store.setTelemetry({ noiseFloor: msg.value }, latencyMs);
            }
        },
        "soul_handoff": (msg, store) => {
            const target = msg.target_soul || msg.target_agent_id || "AetherCore";
            store.setActiveSoul(target);
            store.addNeuralEvent({
                fromAgent: msg.from_soul || msg.source_agent_id || "AetherCore",
                toAgent: target,
                task: msg.task_goal || msg.reason || "Context handover",
                status: "active",
            });
            store.addSystemLog(`[Hive] Handover → ${target}`);
        },
        "handover": (msg, store) => {
            const target = msg.target_soul || msg.target_agent_id || "AetherCore";
            store.setActiveSoul(target);
            store.addNeuralEvent({
                fromAgent: msg.from_soul || msg.source_agent_id || "AetherCore",
                toAgent: target,
                task: msg.task_goal || msg.reason || "Context handover",
                status: "active",
            });
            store.addSystemLog(`[Hive] Handover → ${target}`);
        },
    };

    ws.onmessage = (event) => {
        if (typeof event.data === "string") {
            const msg = JSON.parse(event.data);

            // Handle handshake challenge separately
            if (msg.type === "connect.challenge") {
                // Will be handled by setupAuthHandshake
                return;
            }

            const handler = handlers[msg.type];
            if (handler) {
                handler(msg, store, latencyMs, setLatencyMs);
            }
        } else if (event.data instanceof ArrayBuffer) {
            // Binary audio data
            if (onAudioResponse.current) {
                onAudioResponse.current(event.data);
            }
        }
    };
}

/**
 * Setup authentication handshake with Ed25519
 */
function setupAuthHandshake(
    ws: WebSocket,
    keyPair: nacl.SignKeyPair,
    idToken?: string,
    onAck?: () => void
): void {
    const originalOnMessage = ws.onmessage;

    ws.onmessage = (event) => {
        if (typeof event.data === "string") {
            const msg = JSON.parse(event.data);

            if (msg.type === "connect.challenge") {
                const challengeBytes = fromHex(msg.challenge);
                const signatureBytes = nacl.sign.detached(challengeBytes, keyPair.secretKey);
                ws.send(JSON.stringify({
                    type: "connect.response",
                    client_id: toHex(keyPair.publicKey),
                    signature: toHex(signatureBytes),
                    id_token: idToken,
                    capabilities: ["audio_streaming", "telemetry", "vision"]
                }));
                return;
            }

            if (msg.type === "connect.ack") {
                console.log("✦ Gateway Handshake Successful");
                onAck?.();
                return;
            }
        }

        // Pass through to original handler after auth
        if (originalOnMessage) {
            originalOnMessage(event);
        }
    };
}

/**
 * Setup audio pipelines with backpressure control
 */
function setupAudioPipelines(
    ws: WebSocket,
    backpressure: BackpressureController
): { sendAudio: (pcm: ArrayBuffer) => void } {
    return {
        sendAudio: (pcm: ArrayBuffer) => {
            if (ws.readyState !== WebSocket.OPEN) return;

            // Check backpressure
            if (backpressure.shouldThrottle(ws.bufferedAmount)) {
                // Queue the send
                backpressure.sendQueued(() => {
                    ws.send(pcm);
                });
            } else {
                ws.send(pcm);
            }
        }
    };
}

// ============================================================================
// Main Hook
// ============================================================================

const DEFAULT_URL = process.env.NEXT_PUBLIC_AETHER_GATEWAY_URL || "ws://localhost:18789";

export function useAetherGateway(url = DEFAULT_URL): GatewayAPI {
    const [status, setStatus] = useState<GatewayStatus>("disconnected");
    const [latencyMs, setLatencyMs] = useState(0);

    const wsRef = useRef<WebSocket | null>(null);
    const store = useAetherStore();
    const onAudioResponse = useRef<((audio: ArrayBuffer) => void) | null>(null);
    const keyPairRef = useRef<nacl.SignKeyPair | null>(null);

    // Controllers
    const backpressureRef = useRef<BackpressureController | null>(null);
    const reconnectRef = useRef<ReconnectionManager | null>(null);
    const metricsCallbackRef = useRef<((metrics: GatewayMetrics) => void) | null>(null);
    const droppedFramesRef = useRef(0);

    // Initialize controllers
    if (!backpressureRef.current) {
        backpressureRef.current = new BackpressureController(65536);
    }
    if (!reconnectRef.current) {
        reconnectRef.current = new ReconnectionManager(250, 5000);
    }

    // Check if connected
    const isConnected = useCallback(() => {
        return wsRef.current?.readyState === WebSocket.OPEN && status === "connected";
    }, [status]);

    // Connect with reconnection support
    const connect = useCallback(async (idToken?: string): Promise<void> => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const reconnectMgr = reconnectRef.current!;
        const backpressure = backpressureRef.current!;

        // Check if we should reconnect
        if (reconnectMgr.isInReconnectMode()) {
            setStatus("reconnecting");
        } else {
            setStatus("connecting");
        }

        // Initialize keypair
        if (!keyPairRef.current) {
            keyPairRef.current = getOrCreateKeypair();
        }
        const kp = keyPairRef.current;

        try {
            const ws = new WebSocket(url);
            ws.binaryType = "arraybuffer";
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("✦ Aether Gateway connection opened");
                setStatus("handshaking");

                // Reset reconnection state on successful connect
                reconnectMgr.reset();
                reconnectMgr.stopReconnecting();
                backpressure.clear();
            };

            // Setup event routing (handles all non-handshake messages)
            const handleMessage = (event: MessageEvent): void => {
                if (typeof event.data === "string") {
                    const msg = JSON.parse(event.data);
                    const type = msg.type;

                    // Skip handshake messages - handled separately
                    if (type === "connect.challenge" || type === "connect.ack") return;

                    switch (type) {
                        case "error":
                            console.error("Gateway error:", msg.message);
                            store.addSystemLog(`[Gateway] Error: ${msg.message}`);
                            break;
                        case "tick": {
                            const now = Date.now();
                            const serverTime = msg.timestamp * 1000;
                            const measuredLatency = Math.abs(now - serverTime);
                            setLatencyMs(measuredLatency);
                            store.setLatencyMs(measuredLatency);
                            break;
                        }
                        case "engine_state":
                            store.setEngineState(msg.state);
                            store.addSystemLog(`[Engine] State → ${msg.state}`);
                            break;
                        case "transcript":
                            store.addTranscriptMessage({
                                role: msg.role === "user" ? "user" : "agent",
                                content: msg.text || msg.content || "",
                            });
                            break;
                        case "affective_score":
                            store.setTelemetry({
                                frustration: msg.frustration,
                                valence: msg.valence,
                                arousal: msg.arousal,
                                engagement: msg.engagement,
                                pitch: msg.pitch,
                                rate: msg.rate,
                            }, latencyMs);
                            break;
                        case "audio_telemetry":
                            useAetherStore.getState().setAudioLevels(msg.payload?.rms || 0, msg.payload?.gain || 0);
                            break;
                        case "repair_state":
                            useAetherStore.getState().setRepairState({
                                status: msg.payload?.status || msg.status || 'diagnosing',
                                message: msg.payload?.message || msg.message || '',
                                log: msg.payload?.log || msg.log || '',
                                timestamp: Date.now(),
                            });
                            break;
                        case "neural_event":
                            store.addNeuralEvent({
                                fromAgent: msg.from_agent || "AetherCore",
                                toAgent: msg.to_agent || "Unknown",
                                task: msg.task || msg.description || "",
                                status: msg.status || "active",
                            });
                            break;
                        case "vision_pulse":
                            store.setVisionPulse(msg.timestamp || new Date().toISOString());
                            store.setVisionActive(true);
                            break;
                        case "intent_update":
                            if (msg.memory_update?.predicted_next_goal) {
                                store.setPredictedGoal(msg.memory_update.predicted_next_goal);
                            }
                            break;
                        case "mutation_event":
                            store.setMutation(msg.description || msg.mutation || "Unknown mutation");
                            break;
                        case "tool_result":
                            store.addSilentHint({
                                id: crypto.randomUUID(),
                                text: msg.tool_name || "Tool completed",
                                code: msg.code,
                                explanation: msg.result || msg.message,
                                priority: msg.priority || "info",
                                type: msg.code ? "code" : "hint",
                                timestamp: Date.now(),
                            });
                            store.addSystemLog(`[Tool] ${msg.tool_name}: ${msg.status || "done"}`);
                            break;
                        case "soul_handover":
                        case "handover": {
                            const target = msg.target_soul || msg.target_agent_id || "AetherCore";
                            store.setActiveSoul(target);
                            store.addNeuralEvent({
                                fromAgent: msg.from_soul || msg.source_agent_id || "AetherCore",
                                toAgent: target,
                                task: msg.task_goal || msg.reason || "Context handover",
                                status: "active",
                            });
                            store.addSystemLog(`[Hive] Handover → ${target}`);
                            break;
                        }
                    }
                } else if (event.data instanceof ArrayBuffer) {
                    if (onAudioResponse.current) {
                        onAudioResponse.current(event.data);
                    }
                }
            };

            // Handle handshake challenge inline
            ws.onmessage = (event: MessageEvent) => {
                if (typeof event.data === "string") {
                    const msg = JSON.parse(event.data);
                    if (msg.type === "connect.challenge") {
                        const challengeBytes = fromHex(msg.challenge);
                        const signatureBytes = nacl.sign.detached(challengeBytes, kp.secretKey);
                        ws.send(JSON.stringify({
                            type: "connect.response",
                            client_id: toHex(kp.publicKey),
                            signature: toHex(signatureBytes),
                            id_token: idToken,
                            capabilities: ["audio_streaming", "telemetry", "vision"]
                        }));
                        return;
                    }
                    if (msg.type === "connect.ack") {
                        console.log("✦ Gateway Handshake Successful");
                        setStatus("connected");
                        store.setSessionStartTime(Date.now());
                        store.addSystemLog("[Gateway] Authenticated successfully.");
                        return;
                    }
                }
                // Forward to main event handler
                handleMessage(event);
            };

            // Setup audio with backpressure
            const { sendAudio } = setupAudioPipelines(ws, backpressure);

            ws.onerror = (err) => {
                console.error("Gateway WS error:", err);
                setStatus("error");
            };

            ws.onclose = (event) => {
                console.log("Gateway WS closed", event.code, event.reason);

                // Check if clean close or error
                if (event.code !== 1000 && event.code !== 1001) {
                    // Abnormal close - attempt reconnection
                    reconnectMgr.startReconnecting();
                    const delay = reconnectMgr.recordAttempt();
                    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectMgr.getReconnectionCount()})`);

                    setTimeout(() => {
                        connect(idToken);
                    }, delay);
                } else {
                    setStatus("disconnected");
                    wsRef.current = null;
                }
            };

            // Emit metrics periodically
            const metricsInterval = setInterval(() => {
                if (metricsCallbackRef.current && wsRef.current) {
                    metricsCallbackRef.current({
                        rtt: latencyMs,
                        sendQueueDepth: backpressure.getQueueDepth(),
                        droppedFrames: droppedFramesRef.current,
                        reconnectionCount: reconnectMgr.getReconnectionCount(),
                        bufferedAmount: wsRef.current?.bufferedAmount || 0,
                    });
                }
            }, 1000);

            return () => clearInterval(metricsInterval);

        } catch (err) {
            console.error("Failed to connect to Gateway:", err);
            setStatus("error");
        }
    }, [url, store, latencyMs]);

    // Send audio with backpressure
    const sendAudio = useCallback((pcm: ArrayBuffer) => {
        const ws = wsRef.current;
        const backpressure = backpressureRef.current;
        if (!ws || !backpressure || status !== "connected") return;

        if (backpressure.shouldThrottle(ws.bufferedAmount)) {
            droppedFramesRef.current++;
            backpressure.sendQueued(() => {
                ws.send(pcm);
            });
        } else {
            ws.send(pcm);
        }
    }, [status]);

    // Send intent with debouncing
    const sendIntent = useCallback(async (input: string, level: 1 | 2 | 3 = 1) => {
        const ws = wsRef.current;
        const kp = keyPairRef.current;
        if (!ws || !kp || status !== "connected") return;

        const intent_id = crypto.randomUUID();
        const payload = {
            raw_input: input,
            timestamp_ms: Date.now(),
            user_context: {
                active_file: "portal/main",
                cursor_line: 0
            }
        };

        // V1.1 Signature: Sign the SHA-256 hash
        const payloadStr = JSON.stringify(payload);
        const encoder = new TextEncoder();
        const msgUint8 = encoder.encode(payloadStr);
        const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
        const hashArray = new Uint8Array(hashBuffer);
        const signature = nacl.sign.detached(hashArray, kp.secretKey);

        ws.send(JSON.stringify({
            type: "INTENT",
            version: "1.1",
            intent_id,
            level,
            source: "text",
            payload,
            signature: toHex(signature),
            memory_context: {
                last_intent_id: localStorage.getItem("aether_last_intent_id") || undefined,
                session_depth: 0
            }
        }));

        localStorage.setItem("aether_last_intent_id", intent_id);
    }, [status]);

    const sendVisionFrame = useCallback((base64: string) => {
        const ws = wsRef.current;
        if (!ws || status !== "connected") return;
        ws.send(JSON.stringify({
            type: "vision_frame",
            data: base64,
            timestamp: Date.now(),
        }));
    }, [status]);

    const sendUIStateSync = useCallback((widgets: any[]) => {
        const ws = wsRef.current;
        if (!ws || status !== "connected") return;
        ws.send(JSON.stringify({
            type: "UI_STATE_SYNC",
            payload: { active_widgets: widgets },
            timestamp: Date.now()
        }));
    }, [status]);

    const disconnect = useCallback(() => {
        wsRef.current?.close(1000, "Client disconnect");
        wsRef.current = null;
        setStatus("disconnected");
        reconnectRef.current?.reset();
        backpressureRef.current?.clear();
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            disconnect();
        };
    }, [disconnect]);

    return {
        status,
        latencyMs,
        connect,
        disconnect,
        sendAudio,
        sendVisionFrame,
        sendIntent,
        sendUIStateSync,
        onAudioResponse,
        isConnected,
    };
}
