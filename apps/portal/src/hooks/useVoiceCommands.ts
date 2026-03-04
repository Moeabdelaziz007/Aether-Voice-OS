"use client";
/**
 * useVoiceCommands — Parse transcript for realm navigation triggers.
 *
 * Watches the latest user transcript messages and matches keywords
 * to trigger realm transitions. Debounced to avoid rapid switching.
 */

import { useEffect, useRef } from "react";
import { useAetherStore } from "@/store/useAetherStore";
import type { RealmType } from "@/store/useAetherStore";

interface VoiceCommand {
    keywords: string[];
    realm: RealmType;
}

const VOICE_COMMANDS: VoiceCommand[] = [
    { keywords: ["show skills", "my skills", "abilities", "capabilities"], realm: "skills" },
    { keywords: ["show memory", "memory", "history", "remember"], realm: "memory" },
    { keywords: ["who are you", "settings", "identity", "persona", "customize"], realm: "identity" },
    { keywords: ["diagnostics", "stats", "telemetry", "neural", "show diagnostics"], realm: "neural" },
    { keywords: ["go home", "clear", "home", "void", "back", "close"], realm: "void" },
];

const DEBOUNCE_MS = 500;

export function useVoiceCommands() {
    const transcript = useAetherStore((s) => s.transcript);
    const currentRealm = useAetherStore((s) => s.currentRealm);
    const setRealm = useAetherStore((s) => s.setRealm);
    const lastProcessedRef = useRef<string | null>(null);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
        // Get the latest user message
        const lastUserMsg = [...transcript]
            .reverse()
            .find((m) => m.role === "user");

        if (!lastUserMsg || lastUserMsg.id === lastProcessedRef.current) return;

        const text = lastUserMsg.content.toLowerCase().trim();

        // Check for command matches
        for (const cmd of VOICE_COMMANDS) {
            const matched = cmd.keywords.some((kw) => text.includes(kw));
            if (matched && cmd.realm !== currentRealm) {
                lastProcessedRef.current = lastUserMsg.id;

                // Debounce realm change
                if (debounceRef.current) clearTimeout(debounceRef.current);
                debounceRef.current = setTimeout(() => {
                    setRealm(cmd.realm);
                }, DEBOUNCE_MS);
                break;
            }
        }
    }, [transcript, currentRealm, setRealm]);
}
