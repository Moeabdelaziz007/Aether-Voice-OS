"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

/**
 * TelemetryItem represents a single log entry in the system stream.
 */
export interface TelemetryItem {
    id: string;
    timestamp: string;
    message: string;
    type: "info" | "action" | "error" | "success";
    source?: string;
}

interface TelemetryContextType {
    logs: TelemetryItem[];
    addLog: (message: string, type?: TelemetryItem["type"], source?: string) => void;
    clearLogs: () => void;
}

const TelemetryContext = createContext<TelemetryContextType | undefined>(undefined);

export function TelemetryProvider({ children }: { children: ReactNode }) {
    const [logs, setLogs] = useState<TelemetryItem[]>([]);

    const addLog = useCallback((message: string, type: TelemetryItem["type"] = "info", source?: string) => {
        const newLog: TelemetryItem = {
            id: Math.random().toString(36).substring(2, 11),
            timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            message,
            type,
            source,
        };
        setLogs((prev) => [newLog, ...prev].slice(0, 50)); // Keep last 50 logs
    }, []);

    const clearLogs = useCallback(() => setLogs([]), []);

    return (
        <TelemetryContext.Provider value={{ logs, addLog, clearLogs }}>
            {children}
        </TelemetryContext.Provider>
    );
}

export const useTelemetry = () => {
    const context = useContext(TelemetryContext);
    if (!context) {
        throw new Error("useTelemetry must be used within a TelemetryProvider");
    }
    return context;
}
