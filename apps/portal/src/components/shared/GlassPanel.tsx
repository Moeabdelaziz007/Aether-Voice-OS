"use client";

import React from "react";
import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlassPanelProps extends HTMLMotionProps<"div"> {
    children: React.ReactNode;
    className?: string;
    hover?: boolean;
}

export default function GlassPanel({
    children,
    className,
    hover = false,
    ...motionProps
}: GlassPanelProps) {
    return (
        <motion.div
            className={cn(
                "bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6",
                hover && "transition-shadow duration-300 hover:shadow-[0_0_20px_rgba(0,243,255,0.1)] hover:border-white/15",
                className
            )}
            {...motionProps}
        >
            {children}
        </motion.div>
    );
}
