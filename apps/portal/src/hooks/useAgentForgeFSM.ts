"use client";

import { useState, useCallback, useEffect } from "react";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { useAetherStore } from "../store/useAetherStore";
import { useAetherGateway } from "./useAetherGateway";
import { useForgeStore, AgentDNA } from "../store/useForgeStore";

/**
 * Aether Forge FSM States
 */
export type ForgeState =
    | "IDLE"
    | "LISTENING_SPEC"
    | "EXTRACTING_JSON"
    | "AWAITING_CONFIRMATION"
    | "COMMITTING_TO_FIRESTORE"
    | "ERROR";

/**
 * Gemini Function Declaration for Forge Protocol
 */
export const FORGE_AGENT_SCHEMA = {
    name: "forge_agent_manifest",
    description: "Extract structured agent configuration from the user's vocal description for the Aether Forge protocol.",
    parameters: {
        type: "object",
        properties: {
            name: { type: "string", description: "The name of the AI consciousness." },
            role: { type: "string", description: "The core professional role or persona of the agent (e.g., DevOps Engineer)." },
            skills: { type: "array", items: { type: "string" }, description: "Specific technical or creative skills (e.g., Docker, Python)." },
            tone: { type: "string", description: "The vocal and behavioral tone (e.g., Analytical, Mentor, Sarcastic)." },
            tools_required: { type: "array", items: { type: "string" }, description: "The specialized tools or MCP skills the agent needs access to." }
        },
        required: ["name", "role"]
    }
};

export function useAgentForgeFSM() {
    const [state, setState] = useState<ForgeState>("IDLE");
    const { status, sendIntent, onToolCall, isConnected } = useAetherGateway();
    const forgeStore = useForgeStore();
    const auraStore = useAetherStore();

    const handleToolCall = useCallback((toolCall: any) => {
        if (toolCall.name === "forge_agent_manifest") {
            const args = toolCall.args;
            setState("EXTRACTING_JSON");

            // Update store with incoming neural DNA
            forgeStore.updateDNA({
                name: args.name,
                role: args.role,
                skills: args.skills || [],
                tone: args.tone || "Analytical",
            });

            // Transition to confirmation
            setTimeout(() => setState("AWAITING_CONFIRMATION"), 1000);
            auraStore.addTerminalLog('SYS', `[PROTOCOL] Identity Mapped: ${args.name}. Awaiting confirmation.`);
        }
    }, [forgeStore, auraStore]);

    useEffect(() => {
        // Inject hook for tool handling
        onToolCall.current = handleToolCall;
    }, [handleToolCall, onToolCall]);

    const initiateForge = useCallback(() => {
        if (!isConnected) return;
        setState("LISTENING_SPEC");
        forgeStore.setVoiceMode("listening");
        auraStore.addTerminalLog('SYS', 'Neural Ear Active. Awaiting Agent Specification...');
    }, [isConnected, auraStore, forgeStore]);

    const confirmForge = useCallback(async () => {
        if (state !== "AWAITING_CONFIRMATION") return;

        setState("COMMITTING_TO_FIRESTORE");
        forgeStore.setVoiceMode("processing");
        auraStore.addTerminalLog('SYS', 'Initiating Soul Injection into Firestore Cluster...');

        // Real Firestore Write
        try {
            // Using a top-level 'agents' collection
            const newAgentRef = await addDoc(collection(db, "agents"), {
                ...forgeStore.dna,
                ownerId: "anonymous", // Simplified for current demo scope
                createdAt: serverTimestamp(),
            });

            console.log("🔥 Agent Forged successfully with ID:", newAgentRef.id);

            forgeStore.completeForge();
            auraStore.setAnimationTrigger('soul-swap');
            setState("IDLE");
            auraStore.addTerminalLog('SUCCESS', `Consciousness Stable. Aether Forge Complete. [ID: ${newAgentRef.id}]`);
        } catch (e: any) {
            console.error("Firestore Error:", e);
            setState("ERROR");
            auraStore.addTerminalLog('ERROR', `Firestore Synthesis Failed: ${e.message}`);
        }
    }, [state, forgeStore, auraStore]);

    return {
        state,
        initiateForge,
        confirmForge,
        currentDNA: forgeStore.dna,
        isListening: state === "LISTENING_SPEC"
    };
}
