"use client";

import React from "react";
import { motion } from "framer-motion";

interface StatusIndicatorProps {
    label: string;
    status: "online" | "offline" | "connecting";
    icon: React.ReactNode;
}

const statusColors = {
    online: { bg: "#00f3ff", text: "text-neon-blue", glow: "shadow-[0_0_8px_#00f3ff]" },
    offline: { bg: "#555", text: "text-gray-500", glow: "" },
    connecting: { bg: "#f0c040", text: "text-yellow-400", glow: "shadow-[0_0_8px_#f0c040]" },
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ label, status, icon }) => {
    const colors = statusColors[status];

    return (
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-md bg-white/[0.03] border border-white/[0.06]">
            <motion.div
                animate={status === "online" ? { scale: [1, 1.3, 1] } : status === "connecting" ? { opacity: [1, 0.3, 1] } : {}}
                transition={{ duration: 1.5, repeat: Infinity }}
                className={`h-2 w-2 rounded-full ${colors.glow}`}
                style={{ backgroundColor: colors.bg }}
            />
            <span className="text-gray-600 text-[11px]">{icon}</span>
            <span className={`text-[10px] uppercase tracking-wider font-medium ${colors.text}`}>{label}</span>
        </div>
    );
};
