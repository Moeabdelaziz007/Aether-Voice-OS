"use client";

import { useCallback, useEffect, useRef } from 'react';
import { useForgeStore } from '@/store/useForgeStore';

/**
 * useVoiceForge — Hook for voice-first interaction in the Forge.
 *
 * Manages Web Speech API for voice input,
 * maps spoken commands to Forge actions,
 * and drives the voice mode state machine.
 */
export function useVoiceForge() {
    const {
        voiceMode,
        setVoiceMode,
        setListening,
        setTranscript,
        updateDNA,
        setStep,
        activeStep,
    } = useForgeStore();

    const recognitionRef = useRef<SpeechRecognition | null>(null);

    // Initialize Web Speech API
    useEffect(() => {
        if (typeof window === 'undefined') return;

        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (!SpeechRecognition) return;

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: SpeechRecognitionEvent) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                if (result.isFinal) {
                    finalTranscript += result[0].transcript;
                } else {
                    interimTranscript += result[0].transcript;
                }
            }

            setTranscript(finalTranscript || interimTranscript);

            // Parse voice commands from final transcript
            if (finalTranscript) {
                parseVoiceCommand(finalTranscript.toLowerCase());
            }
        };

        recognition.onerror = () => {
            setVoiceMode('idle');
            setListening(false);
        };

        recognition.onend = () => {
            if (voiceMode === 'listening') {
                // Auto-restart if still in listening mode
                try { recognition.start(); } catch { /* noop */ }
            }
        };

        recognitionRef.current = recognition;

        return () => {
            recognition.abort();
        };
    }, []);

    // Start/stop based on voiceMode
    useEffect(() => {
        const recognition = recognitionRef.current;
        if (!recognition) return;

        if (voiceMode === 'listening') {
            try { recognition.start(); } catch { /* already started */ }
        } else {
            try { recognition.stop(); } catch { /* already stopped */ }
        }
    }, [voiceMode]);

    // Parse voice commands
    const parseVoiceCommand = useCallback((text: string) => {
        // Step navigation
        if (text.includes('next') || text.includes('continue')) {
            const steps = ['genesis', 'brain', 'memory', 'skills', 'visual', 'review'] as const;
            const idx = steps.indexOf(activeStep as any);
            if (idx >= 0 && idx < steps.length - 1) {
                setStep(steps[idx + 1]);
            }
        }

        // Genesis step — extract name & role
        if (activeStep === 'genesis') {
            const nameMatch = text.match(/(?:name|named|call)\s+(?:it|him|her|them)?\s*(\w+)/i);
            if (nameMatch) updateDNA({ name: nameMatch[1] });

            const roleMatch = text.match(/(?:role|specializ|expert|focus)\w*\s+(?:in|on|as)?\s*(.+)/i);
            if (roleMatch) updateDNA({ role: roleMatch[1].trim() });
        }

        // Brain step — model selection
        if (activeStep === 'brain') {
            if (text.includes('gemini')) updateDNA({ model: 'Google Gemini 2.5' });
            if (text.includes('gpt') || text.includes('openai')) updateDNA({ model: 'OpenAI GPT-4o' });
            if (text.includes('claude') || text.includes('anthropic')) updateDNA({ model: 'Anthropic Claude 3.5' });
            if (text.includes('llama') || text.includes('local')) updateDNA({ model: 'Local Llama 3' });
        }

        // Memory step
        if (activeStep === 'memory') {
            if (text.includes('cloud') || text.includes('firebase')) updateDNA({ memoryType: 'firebase' });
            if (text.includes('local') || text.includes('device')) updateDNA({ memoryType: 'local' });
        }
    }, [activeStep, setStep, updateDNA]);

    const startListening = useCallback(() => {
        setVoiceMode('listening');
        setListening(true);
    }, [setVoiceMode, setListening]);

    const stopListening = useCallback(() => {
        setVoiceMode('idle');
        setListening(false);
    }, [setVoiceMode, setListening]);

    return {
        voiceMode,
        startListening,
        stopListening,
    };
}
