"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { useAetherStore } from "@/store/useAetherStore";
import { WIDGET_REGISTRY } from "./WidgetRegistry";
import { WidgetContainer } from "../WidgetContainer";

/**
 * GenerativePortal — A vertical stack of active widgets.
 * Items can be dynamically injected by the Engine via Tool Results.
 */
export default function GenerativePortal() {
    const activeWidgets = useAetherStore((s) => s.activeWidgets);
    const removeWidget = useAetherStore((s) => s.removeWidget);

    if (activeWidgets.length === 0) return null;

    return (
        <div className="fixed top-24 right-8 flex flex-col gap-4 z-40 max-h-[70vh] overflow-y-auto no-scrollbar py-4 px-2 pointer-events-none">
            <AnimatePresence mode="popLayout">
                {activeWidgets.map((widget) => {
                    const WidgetComponent = WIDGET_REGISTRY[widget.type];
                    if (!WidgetComponent) return null;

                    return (
                        <motion.div
                            key={widget.id}
                            layout
                            initial={{ x: 50, opacity: 0, scale: 0.9 }}
                            animate={{ x: 0, opacity: 1, scale: 1 }}
                            exit={{ x: 20, opacity: 0, scale: 0.95 }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                            className="pointer-events-auto"
                        >
                            <div className="relative group">
                                <WidgetContainer className="!h-auto min-w-[320px] max-w-[400px]">
                                    <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={() => removeWidget(widget.id)}
                                            className="p-1 hover:bg-white/10 rounded-full text-white/40 hover:text-white/80 transition-colors"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                    </div>
                                    <WidgetComponent {...widget.props} />
                                </WidgetContainer>
                            </div>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}
