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
    | "REFINING_WITH_VISION"
    | "AWAITING_CONFIRMATION"
    | "COMMITTING_TO_FIRESTORE"
    | "ERROR";

/**
 * Gemini Function Declaration for Forge Protocol V2.0
 */
export const FORGE_AGENT_SCHEMA = {
    name: "forge_agent_manifest",
    description: "Extract structured agent configuration from the user's vocal description and environmental context for the Aether Forge protocol.",
    parameters: {
        type: "object",
        properties: {
            name: { type: "string", description: "The name of the AI consciousness." },
            role: { type: "string", description: "The core professional role or persona of the agent." },
            skills: { type: "array", items: { type: "string" }, description: "Specific technical or creative skills." },
            tone: { type: "string", description: "The vocal and behavioral tone (e.g., Analytical, Mentor, Sarcastic)." },
            personality_quarks: { 
                type: "array", 
                items: { type: "string" }, 
                description: "Subtle character traits or quirks (e.g., 'obsessed with clean code', 'loves sci-fi metaphors')." 
            },
            visual_grounding: { 
                type: "string", 
                description: "Context captured from user's screen that influenced the design (e.g., 'Detected React project open')." 
            }
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

            // Update store with incoming neural DNA + V2.0 metadata
            forgeStore.updateDNA({
                name: args.name,
                role: args.role,
                skills: args.skills || [],
                tone: args.tone || "Analytical",
                personality_quarks: args.personality_quarks || [],
                visual_grounding: args.visual_grounding || ""
            });

            // Transition to vision refinement (simulated grounding)
            setTimeout(() => {
                setState("REFINING_WITH_VISION");
                auraStore.addTerminalLog('SYS', `[PROTOCOL] Multimodal Grounding Active: ${args.visual_grounding || "Scanning workspace environment..."}`);
                
                // Final transition to confirmation
                setTimeout(() => {
                    setState("AWAITING_CONFIRMATION");
                    auraStore.addTerminalLog('SYS', `[PROTOCOL] Identity Mapped: ${args.name}. Awaiting confirmation.`);
                }, 2000);
            }, 1000);
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
