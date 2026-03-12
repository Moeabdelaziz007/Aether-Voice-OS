'use client';

import React, { useCallback, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface VoiceControlPanelProps {
  isListening: boolean;
  isProcessing: boolean;
  onStart?: () => void;
  onStop?: () => void;
  onError?: (error: string) => void;
}

/**
 * Voice control panel with microphone button and smooth transitions
 * Includes accessibility features and keyboard fallback (dev flag)
 */
export default function VoiceControlPanel({
  isListening,
  isProcessing,
  onStart,
  onStop,
  onError,
}: VoiceControlPanelProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startListening = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: BlobPart[] = [];
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstart = () => onStart?.();
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        console.log('[VoiceControlPanel] Recording complete:', blob);
      };

      mediaRecorder.start();
      setError(null);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to access microphone';
      setError(errorMsg);
      onError?.(errorMsg);
    }
  }, [onStart, onError]);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      onStop?.();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }
  }, [onStop]);

  const handleMicrophoneToggle = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  return (
    <div className="flex flex-col gap-4">
      {/* Microphone Button */}
      <div className="flex items-center justify-center">
        <motion.button
          onClick={handleMicrophoneToggle}
          disabled={isProcessing}
          className={`relative w-20 h-20 rounded-full font-semibold text-white transition-all ${
            isListening
              ? 'bg-gradient-to-br from-red-500 to-red-600'
              : 'bg-gradient-to-br from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          whileTap={{ scale: 0.95 }}
          aria-pressed={isListening}
          aria-label={isListening ? 'Stop listening' : 'Start listening'}
        >
          {/* Pulsing background on listening */}
          {isListening && (
            <>
              <motion.div
                className="absolute inset-0 rounded-full bg-red-500/40 border-2 border-red-500"
                initial={{ scale: 1, opacity: 1 }}
                animate={{ scale: 1.4, opacity: 0 }}
                transition={{ duration: 0.8, repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-0 rounded-full bg-red-500/40 border-2 border-red-500"
                initial={{ scale: 1, opacity: 1 }}
                animate={{ scale: 1.6, opacity: 0 }}
                transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
              />
            </>
          )}

          {/* Icon */}
          <span className="relative text-2xl z-10">
            {isListening ? '🔴' : '🎤'}
          </span>
        </motion.button>
      </div>

      {/* Status text */}
      <div className="text-center text-sm text-gray-400">
        {isListening ? (
          <span className="text-red-400 font-semibold">Listening...</span>
        ) : isProcessing ? (
          <span className="text-purple-400 font-semibold">Processing...</span>
        ) : (
          <span>Click the mic to speak</span>
        )}
      </div>

      {/* Error message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs text-red-400 text-center"
          role="alert"
        >
          {error}
        </motion.div>
      )}

      {/* Helper text with examples */}
      <div className="text-xs text-gray-500 text-center space-y-1">
        <p>Try saying:</p>
        <ul className="space-y-1 text-gray-600">
          <li>"Open agent Atlas"</li>
          <li>"Deploy this agent"</li>
          <li>"Show my widgets"</li>
        </ul>
      </div>

      {/* Accessibility: Keyboard fallback (dev flag) */}
      {process.env.NODE_ENV === 'development' && (
        <details className="text-xs text-gray-500 mt-2">
          <summary>Keyboard Control (dev only)</summary>
          <div className="mt-2 space-y-1 text-gray-600">
            <p>Space: Toggle listening</p>
            <p>Esc: Cancel</p>
          </div>
        </details>
      )}
    </div>
  );
}
