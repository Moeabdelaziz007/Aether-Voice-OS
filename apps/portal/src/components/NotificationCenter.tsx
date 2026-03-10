"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, X, RefreshCcw, ShieldAlert, Info } from "lucide-react";
import { useAetherStore } from "../store/useAetherStore";
import { ErrorSeverity } from "../store/slices/errorSlice";

const SEVERITY_ICONS: Record<ErrorSeverity, any> = {
    low: Info,
    medium: AlertCircle,
    high: ShieldAlert,
    critical: ShieldAlert,
};

const SEVERITY_COLORS: Record<ErrorSeverity, string> = {
    low: "bg-blue-500/10 border-blue-500/50 text-blue-400",
    medium: "bg-amber-500/10 border-amber-500/50 text-amber-400",
    high: "bg-rose-500/10 border-rose-500/50 text-rose-400",
    critical: "bg-rose-600/20 border-rose-600 border-2 text-rose-500",
};

export default function NotificationCenter() {
    const errors = useAetherStore((s) => s.errors);
    const dismissError = useAetherStore((s) => s.dismissError);

    return (
        <div className="fixed top-24 right-6 z-[9999] flex flex-col gap-3 w-80 pointer-events-none">
            <AnimatePresence mode="popLayout">
                {errors.map((error) => {
                    const Icon = SEVERITY_ICONS[error.severity];
                    return (
                        <motion.div
                            key={error.id}
                            layout
                            initial={{ opacity: 0, x: 20, scale: 0.9 }}
                            animate={{ opacity: 1, x: 0, scale: 1 }}
                            exit={{ opacity: 0, x: 20, scale: 0.9 }}
                            className={`pointer-events-auto p-4 rounded-xl border backdrop-blur-md flex gap-3 shadow-2xl ${SEVERITY_COLORS[error.severity]}`}
                        >
                            <div className="mt-0.5">
                                <Icon size={18} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between gap-2">
                                    <span className="text-xs font-mono uppercase tracking-wider opacity-60">
                                        {error.code}
                                    </span>
                                    <button
                                        onClick={() => dismissError(error.id)}
                                        className="hover:opacity-100 opacity-40 transition-opacity"
                                    >
                                        <X size={14} />
                                    </button>
                                </div>
                                <p className="text-sm font-medium mt-1 leading-relaxed">
                                    {error.message}
                                </p>
                                {error.retryable && (
                                    <button
                                        onClick={error.onAction}
                                        className="mt-3 flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest bg-white/10 hover:bg-white/20 px-2 py-1 rounded transition-colors"
                                    >
                                        <RefreshCcw size={10} />
                                        {error.actionLabel || "Retry Action"}
                                    </button>
                                )}
                            </div>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}
