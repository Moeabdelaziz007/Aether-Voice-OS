"use client";

import React from "react";
import { motion } from "framer-motion";

/**
 * HUDContainer — The digital scaffolding of AetherOS.
 * Provides corner markers, scanning lines, and tactical overlays across the viewport.
 */

const CornerMarker = ({ position }: { position: "tl" | "tr" | "bl" | "br" }) => {
    const styles = {
        tl: "top-8 left-8 border-t-2 border-l-2",
        tr: "top-8 right-8 border-t-2 border-r-2",
        bl: "bottom-8 left-8 border-b-2 border-l-2",
        br: "bottom-8 right-8 border-b-2 border-r-2",
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 1 }}
            className={`absolute w-8 h-8 border-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.3)] pointer-events-none ${styles[position]}`}
        >
            <div className="absolute inset-0 bg-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.05)] blur-sm" />
        </motion.div>
    );
};

const ScanningLine = () => (
    <motion.div
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="absolute left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.2)] to-transparent z-0 pointer-events-none"
    />
);

export default function HUDContainer({ children }: { children: React.ReactNode }) {
    return (
        <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
            {/* Corner Brackets */}
            <CornerMarker position="tl" />
            <CornerMarker position="tr" />
            <CornerMarker position="bl" />
            <CornerMarker position="br" />

            {/* Vertical Scanning Pulse */}
            <ScanningLine />

            {/* CRT Scanline Overlay */}
            <div className="absolute inset-0 z-0 opacity-10 pointer-events-none mix-blend-overlay
                            bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] 
                            bg-[length:100%_4px,3px_100%]" />

            {/* Vignette Overlay for Depth */}
            <div className="absolute inset-0 z-0 bg-[radial-gradient(circle_at_center,transparent_40%,rgba(0,0,0,0.7)_100%)] pointer-events-none" />

            {/* Content Area (Actual UI) */}
            <div className="relative z-10 w-full h-full pointer-events-auto">
                {children}
            </div>

            {/* Subtle Noise Texture Overlay */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] mix-blend-overlay" />
        </div>
    );
}
