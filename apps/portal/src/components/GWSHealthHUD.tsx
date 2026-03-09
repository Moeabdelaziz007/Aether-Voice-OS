"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAetherStore } from "../store/useAetherStore";

export function GWSHealthHUD() {
    const repairState = useAetherStore((state) => state.repairState);
    const [isVisible, setIsVisible] = useState(false);
    const [repairStatus, setRepairStatus] = useState<"error" | "rehandshaking" | "resolved">("error");
    const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (!repairState) return;

        // repairState might be emitted on a 503/500 code
        if (repairState.status === "failed") {
            setIsVisible(true);
            setRepairStatus("rehandshaking");

            // Start silent verification (ping)
            if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

            pingIntervalRef.current = setInterval(async () => {
                try {
                    // Silently hit a lightweight health endpoint
                    // (Assuming /api/health or similar exists on the local gateway server)
                    const baseUrl = process.env.NEXT_PUBLIC_AETHER_API_URL || "http://localhost:18790";
                    const res = await fetch(`${baseUrl}/health`, { method: "GET" });

                    if (res.status === 200) {
                        setRepairStatus("resolved");
                        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

                        // Close the HUD after showing "resolved" for a short time
                        setTimeout(() => {
                            setIsVisible(false);
                        }, 2500);
                    }
                } catch (err) {
                    // Still failing, continue to rehandshake
                    console.debug("GWS Ping failed, still rehandshaking...");
                }
            }, 3000);
        }

        return () => {
            if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        };
    }, [repairState]);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: -50, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    transition={{ type: "spring", stiffness: 300, damping: 25 }}
                    className="fixed top-6 right-6 z-[9999] pointer-events-none"
                >
                    <div className="bg-black/90 border border-red-500/50 rounded-xl p-4 shadow-[0_0_30px_rgba(239,68,68,0.3)] backdrop-blur-md min-w-[300px] flex items-center gap-4">

                        {/* Status Icon */}
                        <div className="relative flex-shrink-0 w-10 h-10 flex items-center justify-center">
                            {repairStatus === "rehandshaking" ? (
                                <>
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                                        className="absolute inset-0 rounded-full border-t-2 border-r-2 border-orange-500"
                                    />
                                    <motion.div
                                        animate={{ opacity: [0.3, 1, 0.3] }}
                                        transition={{ repeat: Infinity, duration: 1.5 }}
                                        className="w-4 h-4 bg-orange-500 rounded-full"
                                    />
                                </>
                            ) : repairStatus === "resolved" ? (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
                                >
                                    <svg className="w-4 h-4 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                    </svg>
                                </motion.div>
                            ) : (
                                <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                                    <span className="text-black font-bold text-xs">!</span>
                                </div>
                            )}
                        </div>

                        {/* Text Content */}
                        <div className="flex-1 font-mono">
                            <h3 className={`text-sm font-bold uppercase tracking-wider ${
                                repairStatus === "resolved" ? "text-green-400" :
                                repairStatus === "rehandshaking" ? "text-orange-400" : "text-red-400"
                            }`}>
                                {repairStatus === "resolved" ? "Connection Restored" :
                                 repairStatus === "rehandshaking" ? "Re-handshaking GWS" : "GWS Connection Lost"}
                            </h3>
                            <p className="text-xs text-gray-400 mt-1">
                                {repairStatus === "resolved" ? "Zero Context Loss." :
                                 repairStatus === "rehandshaking" ? "Verifying fix silently..." :
                                 repairState?.message || "Error 503: Service Unavailable"}
                            </p>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
