"use client";

import { useEffect, useRef } from 'react';
import { useAetherStore } from '../store/useAetherStore';
import { useAetherGateway } from './useAetherGateway';

/**
 * useUIStateSync — Neural UI State Synchronization Hook.
 * 
 * Automatically synchronizes the frontend's active widgets state with the Aether Gateway.
 * Uses a debounced comparison to minimize network traffic while maintaining high-fidelity awareness.
 */
export function useUIStateSync() {
    const activeWidgets = useAetherStore(s => s.activeWidgets);
    const { sendUIStateSync, status } = useAetherGateway();
    const lastSyncRef = useRef<string>("");

    useEffect(() => {
        if (status !== "connected") return;

        const widgetsJson = JSON.stringify(activeWidgets);
        if (widgetsJson === lastSyncRef.current) return;

        // Atomic comparison + Debounce sync
        const timeout = setTimeout(() => {
            sendUIStateSync(activeWidgets);
            lastSyncRef.current = widgetsJson;
        }, 500);

        return () => clearTimeout(timeout);
    }, [activeWidgets, status, sendUIStateSync]);
}
