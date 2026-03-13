'use client';

import React, { useEffect, useCallback } from 'react';
import { useAetherStore } from '@/store/useAetherStore';

interface GlobalVoiceRouterProps {
  transcript: string;
  onProcessing?: (isProcessing: boolean) => void;
}

/**
 * Global voice command router
 * Parses voice commands and routes them to appropriate handlers
 * Examples:
 * - "open agent X"
 * - "deploy"
 * - "show widgets"
 * - "create agent"
 */
export default function GlobalVoiceRouter({
  transcript,
  onProcessing,
}: GlobalVoiceRouterProps) {
  const setVoiceTranscript = useAetherStore((s) => s.setVoiceTranscript);
  const addTerminalLog = useAetherStore((s) => s.addTerminalLog);

  /**
   * Parse voice command and extract intent + entities
   */
  const parseVoiceCommand = useCallback(
    (text: string): { intent: string; entities: Record<string, string> } | null => {
      const lowerText = text.toLowerCase().trim();

      // Command patterns
      const patterns = [
        {
          pattern: /open\s+agent\s+(\w+)/i,
          intent: 'open_agent',
          entityKey: 'agentName',
        },
        {
          pattern: /create\s+agent\s+(?:named\s+)?(\w+)/i,
          intent: 'create_agent',
          entityKey: 'agentName',
        },
        {
          pattern: /deploy\s+(?:agent\s+)?(\w+)?/i,
          intent: 'deploy_agent',
          entityKey: 'agentName',
        },
        {
          pattern: /show\s+widgets/i,
          intent: 'show_widgets',
        },
        {
          pattern: /hide\s+widgets/i,
          intent: 'hide_widgets',
        },
        {
          pattern: /help/i,
          intent: 'show_help',
        },
        {
          pattern: /what\s+can\s+you\s+do/i,
          intent: 'show_capabilities',
        },
      ];

      for (const { pattern, intent, entityKey } of patterns) {
        const match = lowerText.match(pattern);
        if (match) {
          const entities: Record<string, string> = {};
          if (entityKey && match[1]) {
            entities[entityKey] = match[1];
          }
          return { intent, entities };
        }
      }

      return null;
    },
    []
  );

  /**
   * Execute voice command
   */
  const executeCommand = useCallback(
    async (intent: string, entities: Record<string, string>) => {
      onProcessing?.(true);
      const commandId = Math.random().toString(36).substring(7);
      const timestamp = new Date().toLocaleTimeString();

      try {
        console.log(`[VoiceRouter] Executing command: ${intent}`, entities);
        addTerminalLog('SYS', `[${timestamp}] Executing: ${intent}`);

        switch (intent) {
          case 'open_agent': {
            const agentName = entities.agentName;
            console.log(`[VoiceRouter] Opening agent: ${agentName}`);
            addTerminalLog('AGENT', `Opening agent: ${agentName}`);
            break;
          }

          case 'create_agent': {
            const agentName = entities.agentName;
            console.log(`[VoiceRouter] Creating agent: ${agentName}`);
            addTerminalLog('AGENT', `Creating agent: ${agentName}`);
            break;
          }

          case 'deploy_agent': {
            const agentName = entities.agentName || 'current agent';
            console.log(`[VoiceRouter] Deploying agent: ${agentName}`);
            addTerminalLog('AGENT', `Deploying agent: ${agentName}`);
            break;
          }

          case 'show_widgets': {
            console.log('[VoiceRouter] Showing widgets');
            addTerminalLog('SYS', 'Displaying widgets');
            break;
          }

          case 'hide_widgets': {
            console.log('[VoiceRouter] Hiding widgets');
            addTerminalLog('SYS', 'Hiding widgets');
            break;
          }

          case 'show_help': {
            console.log('[VoiceRouter] Showing help');
            addTerminalLog('SYS', 'Voice commands: open agent, create agent, deploy, show widgets');
            break;
          }

          case 'show_capabilities': {
            console.log('[VoiceRouter] Showing capabilities');
            addTerminalLog('SYS', 'I can: create agents, deploy them, manage widgets, and control the interface with voice');
            break;
          }

          default:
            addTerminalLog('ERROR', `Unknown command: ${intent}`);
        }

        addTerminalLog('SUCCESS', `Command completed: ${intent}`);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        console.error(`[VoiceRouter] Command failed: ${intent}`, error);
        addTerminalLog('ERROR', `Command failed: ${intent} - ${errorMsg}`);
      } finally {
        onProcessing?.(false);
      }
    },
    [onProcessing, addTerminalLog]
  );

  /**
   * Process transcript when it changes
   */
  useEffect(() => {
    if (!transcript || transcript.trim().length === 0) {
      return;
    }

    const command = parseVoiceCommand(transcript);
    if (command) {
      console.log('[VoiceRouter] Parsed command:', command);
      executeCommand(command.intent, command.entities);
    } else {
      console.log('[VoiceRouter] No matching command pattern for:', transcript);
      addTerminalLog('SYS', `No command matched: ${transcript}`);
    }
  }, [transcript, parseVoiceCommand, executeCommand, addTerminalLog]);

  return null; // This is a background router component
}
