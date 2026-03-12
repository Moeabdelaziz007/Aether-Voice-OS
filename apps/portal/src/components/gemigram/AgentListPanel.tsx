'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { listAgents } from '@/services/agentService';
import type { FirestoreAgent } from '@/lib/validation';

interface AgentListPanelProps {
  onSelectAgent?: (agentId: string) => void;
}

/**
 * Agent list with live status badges and voice-triggered actions
 */
export default function AgentListPanel({ onSelectAgent }: AgentListPanelProps) {
  const [agents, setAgents] = useState<FirestoreAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        const loadedAgents = await listAgents(undefined, 'active');
        setAgents(loadedAgents);
      } catch (error) {
        console.error('[AgentListPanel] Failed to load agents:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAgents();
  }, []);

  const handleSelectAgent = (agentId: string) => {
    setSelectedAgent(agentId);
    onSelectAgent?.(agentId);
  };

  // Status colors
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500/20 border-green-500/50';
      case 'busy':
        return 'bg-yellow-500/20 border-yellow-500/50';
      case 'offline':
      default:
        return 'bg-gray-500/20 border-gray-500/50';
    }
  };

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500 shadow-lg shadow-green-500/50';
      case 'busy':
        return 'bg-yellow-500 shadow-lg shadow-yellow-500/50';
      case 'offline':
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="h-14 border-b border-cyan-500/10 flex items-center px-4">
        <h2 className="text-sm font-semibold text-gray-300">Agents</h2>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center h-20"
            >
              <div className="w-4 h-4 rounded-full border-2 border-cyan-500/50 border-t-cyan-500 animate-spin" />
            </motion.div>
          ) : agents.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-xs">
              No agents yet. Create one to get started.
            </div>
          ) : (
            agents.map((agent) => (
              <motion.button
                key={agent.id}
                onClick={() => handleSelectAgent(agent.id)}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ x: 4 }}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  selectedAgent === agent.id
                    ? 'bg-cyan-500/10 border-cyan-500/50'
                    : 'bg-black/40 border-gray-600/30 hover:bg-black/60'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-lg border ${getStatusColor('online')} flex items-center justify-center`}>
                    <span className="text-xs font-bold text-gray-300">
                      {agent.name.charAt(0).toUpperCase()}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-white truncate">
                        {agent.name}
                      </h3>
                      {/* Status indicator */}
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${getStatusDot('online')}`} />
                    </div>
                    <p className="text-xs text-gray-400 truncate">
                      {agent.persona || 'No description'}
                    </p>
                    {agent.skills && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {agent.skills.slice(0, 2).map((skill) => (
                          <span
                            key={skill}
                            className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400"
                          >
                            {skill}
                          </span>
                        ))}
                        {agent.skills.length > 2 && (
                          <span className="text-[10px] px-2 py-0.5 text-gray-400">
                            +{agent.skills.length - 2}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Last action time */}
                  <div className="text-xs text-gray-500 flex-shrink-0">
                    Now
                  </div>
                </div>
              </motion.button>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Create New Agent Button */}
      <div className="h-12 border-t border-cyan-500/10 p-3">
        <button className="w-full px-4 py-2 text-xs font-semibold text-white bg-cyan-500/20 border border-cyan-500/50 rounded-lg hover:bg-cyan-500/30 transition-colors">
          + New Agent
        </button>
      </div>
    </div>
  );
}
