'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAetherStore } from '@/store/useAetherStore';
import AgentListPanel from './AgentListPanel';
import VoiceControlPanel from './VoiceControlPanel';
import WidgetPanel from './WidgetPanel';
import GlobalVoiceRouter from './GlobalVoiceRouter';
import VoiceActivityIndicator from './VoiceActivityIndicator';

/**
 * Main GemiGram interface component
 * Telegram-like interface with voice-only command flow
 */

export interface GemiGramState {
  isListening: boolean;
  transcript: string;
  isProcessing: boolean;
  activeAgent?: string;
  showWidgets: boolean;
  error?: string;
}

export default function GemiGramInterface() {
  const avatarState = useAetherStore((s) => s.avatarState);
  const voiceTranscript = useAetherStore((s) => s.voiceTranscript);
  const setVoiceTranscript = useAetherStore((s) => s.setVoiceTranscript);

  const [state, setState] = useState<GemiGramState>({
    isListening: false,
    transcript: '',
    isProcessing: false,
    showWidgets: false,
  });

  // Sync with global state
  useEffect(() => {
    setState((prev) => ({
      ...prev,
      isListening: avatarState === 'Listening' || avatarState === 'ListeningActive',
      transcript: voiceTranscript,
    }));
  }, [avatarState, voiceTranscript]);

  const handleVoiceStart = useCallback(() => {
    setState((prev) => ({ ...prev, isListening: true, transcript: '' }));
  }, []);

  const handleVoiceStop = useCallback(() => {
    setState((prev) => ({ ...prev, isListening: false }));
  }, []);

  const handleVoiceError = useCallback((error: string) => {
    setState((prev) => ({ ...prev, error }));
    setTimeout(() => setState((prev) => ({ ...prev, error: undefined })), 5000);
  }, []);

  const handleToggleWidgets = useCallback(() => {
    setState((prev) => ({ ...prev, showWidgets: !prev.showWidgets }));
  }, []);

  return (
    <div className="w-full h-screen flex flex-col bg-gradient-to-br from-[#050505] via-[#0a0a1a] to-[#050505] overflow-hidden">
      {/* Header with branding */}
      <header className="h-16 border-b border-cyan-500/10 flex items-center justify-between px-6 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center font-bold text-white text-sm">
            Gg
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            GemiGram
          </h1>
        </div>

        {/* Voice Activity Indicator */}
        <VoiceActivityIndicator
          isListening={state.isListening}
          isProcessing={state.isProcessing}
          transcript={state.transcript}
        />

        {/* Widget Toggle */}
        <button
          onClick={handleToggleWidgets}
          className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          aria-label="Toggle widgets"
        >
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h12a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6z" />
          </svg>
        </button>
      </header>

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Agent List - Left sidebar */}
        <div className="w-80 border-r border-cyan-500/10 overflow-hidden flex flex-col">
          <AgentListPanel onSelectAgent={(agentId) => setState((prev) => ({ ...prev, activeAgent: agentId }))} />
        </div>

        {/* Central area - Voice control + conversation */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Main area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            <AnimatePresence>
              {state.error && (
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 text-sm"
                  role="alert"
                >
                  {state.error}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Transcript display */}
            <AnimatePresence mode="wait">
              {state.transcript && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="p-4 bg-cyan-500/5 border border-cyan-500/20 rounded-lg"
                  role="status"
                  aria-live="polite"
                >
                  <p className="text-sm text-cyan-300">{state.transcript}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Voice Control Panel - Bottom */}
          <div className="border-t border-cyan-500/10 p-6 bg-black/40 backdrop-blur-xl">
            <VoiceControlPanel
              isListening={state.isListening}
              isProcessing={state.isProcessing}
              onStart={handleVoiceStart}
              onStop={handleVoiceStop}
              onError={handleVoiceError}
            />
          </div>
        </div>

        {/* Right sidebar - Widgets */}
        <AnimatePresence>
          {state.showWidgets && (
            <motion.div
              initial={{ opacity: 0, x: 400 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 400 }}
              transition={{ type: 'spring', damping: 25, stiffness: 120 }}
              className="w-96 border-l border-cyan-500/10 overflow-y-auto bg-black/40 backdrop-blur-xl p-6"
            >
              <WidgetPanel />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Global Voice Router */}
      <GlobalVoiceRouter
        transcript={state.transcript}
        onProcessing={(isProcessing) => setState((prev) => ({ ...prev, isProcessing }))}
      />
    </div>
  );
}
