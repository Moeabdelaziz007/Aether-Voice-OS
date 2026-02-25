"use client";

import { useState, useEffect } from "react";
import { LiveWaveLine } from "@/components/LiveWaveLine";
import { Mic, MicOff, Settings, Shield, Power, Activity } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function AetherDashboard() {
    const [isActive, setIsActive] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [audioData, setAudioData] = useState<number[]>([]);

    // Mock audio data simulation for now
    useEffect(() => {
        if (!isActive || isMuted) {
            setAudioData([]);
            return;
        }

        const interval = setInterval(() => {
            const mockData = Array.from({ length: 64 }, () => Math.random() * 100 + 20);
            setAudioData(mockData);
        }, 50);

        return () => clearInterval(interval);
    }, [isActive, isMuted]);

    return (
        <div className="flex h-screen flex-col items-center justify-between p-8 font-mono overflow-hidden">
            {/* Top Navigation */}
            <header className="flex w-full items-center justify-between p-4 carbon-panel rounded-lg neon-border">
                <div className="flex items-center gap-4">
                    <div className="h-4 w-4 rounded-full bg-neon-blue animate-pulse shadow-[0_0_10px_#00f3ff]" />
                    <h1 className="text-xl font-bold tracking-widest text-white">AETHER OS <span className="text-xs text-neon-blue">V2.0 ALPHA</span></h1>
                </div>
                <div className="flex gap-4">
                    <Settings className="h-5 w-5 cursor-pointer text-gray-400 hover:text-neon-blue transition-colors" />
                    <Shield className="h-5 w-5 cursor-pointer text-gray-400 hover:text-neon-purple transition-colors" />
                </div>
            </header>

            {/* Main Vision Core */}
            <div className="relative flex w-full flex-1 flex-col items-center justify-center gap-12">
                <div className="relative flex h-64 w-64 items-center justify-center">
                    {/* Pulsing Orb Background */}
                    <motion.div
                        animate={{ scale: isActive ? [1, 1.2, 1] : 1, opacity: isActive ? [0.2, 0.4, 0.2] : 0.1 }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="absolute inset-x-0 h-full w-full rounded-full bg-neon-blue blur-3xl"
                    />

                    <AnimatePresence>
                        {isActive ? (
                            <motion.div
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0, opacity: 0 }}
                                className="relative z-10 flex h-48 w-48 flex-col items-center justify-center rounded-full border-2 border-neon-blue bg-black shadow-[0_0_50px_#00f3ff22]"
                            >
                                <Activity className="h-12 w-12 text-neon-blue mb-2" />
                                <span className="text-xs text-neon-blue tracking-tighter">LISTENING</span>
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                className="relative z-10 flex h-48 w-48 items-center justify-center rounded-full border-2 border-gray-800 bg-carbon-900"
                            >
                                <Power className="h-12 w-12 text-gray-700 hover:text-neon-blue transition-colors cursor-pointer" onClick={() => setIsActive(true)} />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Waveform Section */}
                <div className="w-full max-w-4xl carbon-panel p-6 rounded-xl border border-gray-800">
                    <div className="flex justify-between items-center mb-4 px-2">
                        <span className="text-[10px] text-gray-500 uppercase">Input Feed (Multimodal Pipeline)</span>
                        <span className="text-[10px] text-neon-blue uppercase">{isActive ? "8.2ms LATENCY" : "STANDBY"}</span>
                    </div>
                    <LiveWaveLine analyzing={isActive} audioData={audioData} />
                </div>
            </div>

            {/* Controls Footer */}
            <footer className="w-full flex justify-center gap-8 pb-4">
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsActive(!isActive)}
                    className={`flex h-16 w-16 items-center justify-center rounded-full border-2 transition-all ${isActive ? "border-neon-blue bg-neon-blue/10 text-neon-blue" : "border-gray-800 bg-black text-gray-600"
                        }`}
                >
                    {isActive ? <Mic className="h-8 w-8" /> : <MicOff className="h-8 w-8" />}
                </motion.button>

                <button
                    className="flex h-16 w-48 items-center justify-center rounded-full border-2 border-red-900/50 bg-red-950/10 text-red-500 font-bold hover:bg-red-950/30 transition-all uppercase tracking-widest text-sm"
                    onClick={() => setIsActive(false)}
                >
                    Emergency Kill
                </button>
            </footer>

            {/* Background Grid Pattern */}
            <div className="fixed inset-0 -z-10 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
        </div>
    );
}
