"use client";

import React, { useState, useEffect, useRef } from "react";
import { LiveWaveLine } from "@/components/LiveWaveLine";
import { Mic, MicOff, Settings, X, GripHorizontal, Activity } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
    const [isListening, setIsListening] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [aetherState, setAetherState] = useState<"idle" | "listening" | "speaking" | "thinking">("idle");
    const [connectionStatus, setConnectionStatus] = useState<"disconnected" | "connecting" | "connected">("disconnected");
    const [currentMessage, setCurrentMessage] = useState<string>("");
    const wsRef = useRef<WebSocket | null>(null);

    // Establish OpenClaw WebSocket connection to the Python backend
    useEffect(() => {
        const connectWs = () => {
            setConnectionStatus("connecting");
            // Connect to Aether Gateway
            // Connect to Aether Gateway on the correct port defined in .env
            const wsUrl = "ws://127.0.0.1:18789";
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log("Connected to Aether OpenClaw Gateway.");
                setConnectionStatus("connected");

                // Simple handshake for Aether Gateway
                ws.send(JSON.stringify({
                    type: "handshake",
                    client_id: "web-ui-client",
                    capabilities: ["voice", "transcript"],
                    signature: "test-auth-bypass"
                }));
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    // Handle VAD (Voice Activity Detection) Events
                    if (data.type === "vad.event" || data.type === "vad") {
                        if (data.is_speech) {
                            setAetherState("listening");
                            setIsListening(true);
                        } else if (data.status === "interrupted") {
                            setAetherState("idle");
                            setIsListening(false);
                        }
                    } else if (data.type === "state_change") {
                        // Example: "idle", "listening", "speaking", "thinking"
                        if (data.state) {
                            setAetherState(data.state);
                            // Clear message when transitioning to listening or thinking
                            if (data.state === "listening" || data.state === "thinking") {
                                setCurrentMessage("");
                            }
                        }
                    } else if (data.type === "transcript") {
                        setCurrentMessage(prev => prev + data.text);
                    }
                } catch (e) {
                    console.error("Failed to parse Aether message:", e);
                }
            };

            ws.onerror = (err) => {
                console.error("Aether WebSocket error:", err);
            };

            ws.onclose = () => {
                console.log("Disconnected from Aether Gateway. Reconnecting in 3s...");
                setConnectionStatus("disconnected");
                setIsListening(false);
                setAetherState("idle");
                setTimeout(connectWs, 3000); // Auto-reconnect
            };

            wsRef.current = ws;
        };

        connectWs();

        return () => {
            if (wsRef.current) wsRef.current.close();
        };
    }, []);

    const toggleListen = () => {
        // Optimistic UI updates
        const nextState = !isListening;
        setIsListening(nextState);
        setAetherState(nextState ? "listening" : "idle");

        // Send command to backend via WebSocket
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: "ui_command",
                action: nextState ? "unmute" : "mute"
            }));
        }
    };

    return (
        <main
            className="flex min-h-screen flex-col items-center justify-center p-4"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* 
        Main Floating Container 
        Glassmorphism effect, dark carbon styling, neon accents
      */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative flex flex-col items-center p-6 w-[360px] rounded-[32px] 
                   bg-black/40 backdrop-blur-xl border border-white/10 
                   shadow-[0_0_40px_rgba(0,0,0,0.5)] overflow-hidden"
            >
                {/* Drag Handle for Desktop Window */}
                <div data-tauri-drag-region className="absolute top-2 left-0 right-0 h-6 flex justify-center items-center cursor-grab active:cursor-grabbing opacity-50 hover:opacity-100 transition-opacity">
                    <GripHorizontal size={14} className="text-white/40 pointer-events-none" />
                </div>

                {/* Top Action Bar (Visible on Hover) */}
                <AnimatePresence>
                    {isHovered && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="absolute top-4 left-4 right-4 flex justify-between items-center z-10"
                        >
                            <button className="p-2 rounded-full hover:bg-white/10 transition-colors text-white/70 hover:text-white relative group">
                                <Settings size={16} />
                                {/* Quick tooltip for connection status */}
                                <div className="absolute top-full left-0 mt-2 bg-black/80 px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                    Gateway: {connectionStatus}
                                </div>
                            </button>
                            {connectionStatus === "connected" && (
                                <Activity size={14} className="text-green-400 animate-pulse" />
                            )}
                            <button className="p-2 rounded-full hover:bg-red-500/20 hover:text-red-400 transition-colors text-white/70 tracking-widest text-xs font-bold uppercase" title="Close Aether">
                                {/* <X size={16} /> */}
                                EXIT
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Aether Avatar or Indicator */}
                <div className="mt-8 mb-4 relative">
                    <div className={`absolute inset-0 rounded-full blur-xl transition-all duration-700 ${aetherState === 'listening' ? 'bg-blue-500/30 scale-150' : aetherState === 'speaking' ? 'bg-purple-500/40 scale-125' : 'bg-transparent scale-100'}`} />
                    <div className="h-16 w-16 rounded-full border border-white/20 bg-gradient-to-br from-gray-800 to-black flex items-center justify-center relative z-10 shadow-inner">
                        <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                            Æ
                        </span>
                    </div>
                </div>

                {/* Audio Visualizer */}
                <div className="w-full my-4">
                    <LiveWaveLine isListening={isListening} />
                </div>

                {/* State Text */}
                <div className="h-6 mt-2 text-center flex items-center justify-center">
                    <AnimatePresence mode="wait">
                        <motion.p
                            key={aetherState}
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -5 }}
                            className={`text-sm tracking-widest uppercase font-medium ${aetherState === 'listening' ? 'text-blue-400' : aetherState === 'speaking' ? 'text-purple-400' : 'text-gray-400'}`}
                        >
                            {aetherState === 'idle' ? 'Aether Idle' :
                                aetherState === 'listening' ? 'Listening...' :
                                    aetherState === 'thinking' ? 'Processing...' :
                                        'Speaking...'}
                        </motion.p>
                    </AnimatePresence>
                </div>

                {/* Transcript Drawer */}
                <AnimatePresence>
                    {currentMessage && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="w-full px-4 mb-4 text-center overflow-hidden"
                        >
                            <p className="text-[13px] text-white/80 leading-relaxed font-light italic mt-3 line-clamp-3">
                                "{currentMessage}"
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Main Mic Toggle Button */}
                <button
                    onClick={toggleListen}
                    title="Toggle Microphone"
                    className={`
            group relative flex items-center justify-center w-16 h-16 rounded-full
            transition-all duration-300 ease-out border
            ${isListening
                            ? 'bg-red-500/10 border-red-500/50 text-red-400 hover:bg-red-500/20'
                            : 'bg-white/5 border-white/20 text-white hover:bg-white/10 hover:border-white/40'}
            ${connectionStatus !== 'connected' ? 'opacity-50 cursor-not-allowed' : ''}
          `}
                    disabled={connectionStatus !== 'connected'}
                >
                    {isListening ? (
                        <MicOff size={24} className="relative z-10" />
                    ) : (
                        <Mic size={24} className="relative z-10" />
                    )}

                    {/* Subtle glow on hover */}
                    <div className={`absolute inset-0 rounded-full blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${isListening ? 'bg-red-500/30' : 'bg-white/20'}`} />
                </button>

            </motion.div>
        </main>
    );
}
