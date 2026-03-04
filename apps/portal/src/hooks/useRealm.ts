"use client";
/**
 * useRealm — Realm state machine for AetherOS.
 *
 * Manages which realm is currently active and provides
 * transition helpers with orb position/size configs.
 */

import { useCallback } from "react";
import { useAetherStore } from "@/store/useAetherStore";

export type RealmType = "void" | "skills" | "memory" | "identity" | "neural";

export interface OrbConfig {
    size: number;      // px
    x: string;         // CSS position
    y: string;         // CSS position
    glow: number;      // glow intensity multiplier
}

export const REALM_ORB_CONFIG: Record<RealmType, OrbConfig> = {
    void: { size: 320, x: "50%", y: "45%", glow: 1.0 },
    skills: { size: 120, x: "50%", y: "12%", glow: 0.6 },
    memory: { size: 100, x: "12%", y: "50%", glow: 0.5 },
    identity: { size: 160, x: "50%", y: "30%", glow: 1.2 },
    neural: { size: 80, x: "50%", y: "10%", glow: 0.4 },
};

export const REALM_LABELS: Record<RealmType, string> = {
    void: "Void",
    skills: "Skills",
    memory: "Memory",
    identity: "Identity",
    neural: "Neural",
};

export function useRealm() {
    const currentRealm = useAetherStore((s) => s.currentRealm);
    const setRealm = useAetherStore((s) => s.setRealm);

    const orbConfig = REALM_ORB_CONFIG[currentRealm];

    const navigateTo = useCallback(
        (realm: RealmType) => {
            if (realm !== currentRealm) {
                setRealm(realm);
            }
        },
        [currentRealm, setRealm]
    );

    return {
        currentRealm,
        orbConfig,
        navigateTo,
        isVoid: currentRealm === "void",
    };
}
