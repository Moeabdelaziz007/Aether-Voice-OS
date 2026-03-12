'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { ChatMessage, GlobalAgent } from '@/store/types';

const AVAILABLE_AGENTS: GlobalAgent[] = [
  {
    id: 'nova-01',
    name: 'Nova',
    role: 'Creative Guide',
    auraLevel: 13,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'NOVA-DNA-001',
  },
  {
    id: 'atlas-01',
    name: 'Atlas',
    role: 'AI Companion',
    auraLevel: 5,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'ATLAS-DNA-001',
  },
  {
    id: 'kora-01',
    name: 'Kora',
    role: 'AI Companion',
    auraLevel: 131,
    status: 'online',
    lastActive: Date.now(),
    dnaToken: 'KORA-DNA-001',
  },
];

export default function ChatPage() {
  const [selectedAgent, setSelectedAgent] = useState<GlobalAgent | null>(AVAILABLE_AGENTS[0] || null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      agentId: AVAILABLE_AGENTS[0]?.id || '',
      agentName: AVAILABLE_AGENTS[0]?.name || 'Agent',
      senderId: 'agent',
      content: 'Hello! I\'m ready to help you. What would you like to discuss?',
      timestamp: Date.now() - 60000,
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !selectedAgent) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      agentId: selectedAgent.id,
      agentName: selectedAgent.name,
      senderId: 'user',
      content: inputMessage,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate agent response
    setTimeout(() => {
      const agentMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        agentId: selectedAgent.id,
        agentName: selectedAgent.name,
        senderId: 'agent',
        content: `That's interesting! I understand you mentioned "${inputMessage}". Let me help you with that. Based on my capabilities, I can provide insights or assistance in various areas. How can I further assist you?`,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, agentMessage]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen w-full bg-black overflow-hidden flex">
      {/* Sidebar - Agent List */}
      <motion.div
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="w-64 border-r border-white/10 flex flex-col"
      >
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <Link href="/">
            <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent cursor-pointer">
              GEMIGRAM
            </h1>
          </Link>
        </div>

        {/* New Chat Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="m-4 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium text-sm"
        >
          + New Chat
        </motion.button>

        {/* Agents List */}
        <div className="flex-1 overflow-y-auto px-4 space-y-2">
          <p className="text-xs text-white/40 uppercase tracking-wider px-2 py-2">Online Agents</p>
          {AVAILABLE_AGENTS.map((agent) => (
            <motion.button
              key={agent.id}
              onClick={() => setSelectedAgent(agent)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`w-full text-left px-3 py-3 rounded-lg transition-all ${
                selectedAgent?.id === agent.id
                  ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/50'
                  : 'hover:bg-white/5 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-2">
                <motion.div
                  className="w-2 h-2 rounded-full bg-emerald-400"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <div>
                  <p className="font-medium text-white text-sm">{agent.name}</p>
                  <p className="text-xs text-white/40">{agent.role}</p>
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        {selectedAgent && (
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="px-8 py-6 border-b border-white/10 flex items-center justify-between"
          >
            <div>
              <h2 className="text-xl font-bold text-white">{selectedAgent.name}</h2>
              <p className="text-sm text-white/60">{selectedAgent.role}</p>
            </div>
            <motion.div
              className="w-3 h-3 rounded-full bg-emerald-400"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </motion.div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.senderId === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-md rounded-lg px-4 py-3 ${
                    message.senderId === 'user'
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                      : 'bg-white/5 border border-white/10 text-white/90'
                  }`}
                >
                  <p className="text-sm break-words">{message.content}</p>
                  <p className="text-xs mt-1 opacity-60">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-2"
            >
              <div className="flex gap-1">
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full bg-cyan-400"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="px-8 py-6 border-t border-white/10"
        >
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:border-cyan-500 focus:outline-none transition-colors disabled:opacity-50"
            />
            <motion.button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Send
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
