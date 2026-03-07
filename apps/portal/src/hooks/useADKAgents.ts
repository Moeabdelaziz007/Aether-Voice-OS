/**
 * Aether Voice OS — useADKAgents Hook
 * 
 * Frontend integration with Google ADK (Agent Development Kit).
 * Provides task delegation, agent status monitoring, and handover events.
 * 
 * Features:
 * - Connect to ADK InMemoryRunner backend
 * - Delegate tasks to specialist agents
 * - Monitor active agent status
 * - Handle handover events
 * - Stream agent responses
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAetherStore } from '../store/useAetherStore';

export interface ADKAgent {
    name: string;
    model: string;
    description: string;
    isActive: boolean;
    status: 'idle' | 'thinking' | 'executing' | 'handing_off';
}

export interface ADKTask {
    id: string;
    task: string;
    assignedTo: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    result?: string;
    timestamp: number;
}

export interface HandoverEvent {
    fromAgent: string;
    toAgent: string;
    reason: string;
    context: Record<string, any>;
    timestamp: number;
}

interface UseADKAgentsReturn {
    // Agents
    agents: ADKAgent[];
    activeAgent: string | null;

    // Tasks
    tasks: ADKTask[];
    delegateTask: (task: string, agentName?: string) => Promise<void>;
    cancelTask: (taskId: string) => void;

    // Events
    handoverHistory: HandoverEvent[];

    // Status
    isConnected: boolean;
    isConnecting: boolean;
    error: string | null;

    // Controls
    connect: () => Promise<void>;
    disconnect: () => void;
    setActiveAgent: (agentName: string) => void;
}

const ADK_WS_URL = process.env.NEXT_PUBLIC_ADK_WS_URL || 'ws://localhost:18790/adk';

export function useADKAgents(): UseADKAgentsReturn {
    const store = useAetherStore();
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

    // State
    const [agents, setAgents] = useState<ADKAgent[]>([
        {
            name: 'AetherCore',
            model: 'gemini-2.0-flash',
            description: 'Primary orchestrator',
            isActive: true,
            status: 'idle',
        },
        {
            name: 'ArchitectAgent',
            model: 'gemini-2.0-flash',
            description: 'System architecture specialist',
            isActive: false,
            status: 'idle',
        },
        {
            name: 'DebuggerAgent',
            model: 'gemini-2.0-flash',
            description: 'Debugging and repair specialist',
            isActive: false,
            status: 'idle',
        },
    ]);

    const [tasks, setTasks] = useState<ADKTask[]>([]);
    const [handoverHistory, setHandoverHistory] = useState<HandoverEvent[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [activeAgent, setActiveAgentState] = useState<string | null>('AetherCore');

    // Connect to ADK WebSocket
    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setIsConnecting(true);
        setError(null);

        try {
            const ws = new WebSocket(ADK_WS_URL);

            ws.onopen = () => {
                console.log('[ADK] Connected to InMemoryRunner');
                setIsConnected(true);
                setIsConnecting(false);
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    handleADKMessage(message);
                } catch (err) {
                    console.error('[ADK] Failed to parse message:', err);
                }
            };

            ws.onerror = (err) => {
                console.error('[ADK] WebSocket error:', err);
                setError('Connection failed');
                setIsConnecting(false);
            };

            ws.onclose = () => {
                console.log('[ADK] Disconnected');
                setIsConnected(false);

                // Attempt reconnection after 3 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    if (!wsRef.current?.readyState) {
                        connect();
                    }
                }, 3000);
            };

            wsRef.current = ws;
        } catch (err) {
            setError('Failed to connect to ADK backend');
            setIsConnecting(false);
        }
    }, []);

    // Handle incoming ADK messages
    const handleADKMessage = useCallback((message: any) => {
        const { type, data } = message;

        switch (type) {
            case 'agent.status':
                setAgents(prev => prev.map(agent =>
                    agent.name === data.agent
                        ? { ...agent, status: data.status }
                        : agent
                ));
                break;

            case 'agent.active':
                setActiveAgentState(data.agent);
                setAgents(prev => prev.map(agent => ({
                    ...agent,
                    isActive: agent.name === data.agent,
                })));
                break;

            case 'handover.initiated': {
                const handoverEvent: HandoverEvent = {
                    fromAgent: data.from_agent,
                    toAgent: data.to_agent,
                    reason: data.reason || 'Task delegation',
                    context: data.context || {},
                    timestamp: Date.now(),
                };
                setHandoverHistory(prev => [handoverEvent, ...prev].slice(0, 50));

                // Update store
                store.addSystemLog(`[Hive] Handover: ${data.from_agent} → ${data.to_agent}`);
                break;
            }

            case 'task.result':
                setTasks(prev => prev.map(task =>
                    task.id === data.task_id
                        ? { ...task, status: 'completed', result: data.result }
                        : task
                ));
                break;

            case 'error':
                console.error('[ADK] Error:', data.message);
                setError(data.message);
                break;
        }
    }, [store]);

    // Disconnect on unmount
    useEffect(() => {
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            wsRef.current?.close();
        };
    }, []);

    // Delegate task to ADK agent
    const delegateTask = useCallback(async (task: string, agentName?: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            throw new Error('ADK not connected');
        }

        const taskId = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const targetAgent = agentName || activeAgent || 'AetherCore';

        const newTask: ADKTask = {
            id: taskId,
            task,
            assignedTo: targetAgent,
            status: 'pending',
            timestamp: Date.now(),
        };

        setTasks(prev => [...prev, newTask]);

        // Send task to ADK runner
        wsRef.current.send(JSON.stringify({
            type: 'task.delegate',
            task_id: taskId,
            agent: targetAgent,
            task_description: task,
        }));

        // Update task status to in_progress
        setTimeout(() => {
            setTasks(prev => prev.map(t =>
                t.id === taskId ? { ...t, status: 'in_progress' } : t
            ));
        }, 500);
    }, [activeAgent]);

    // Cancel task
    const cancelTask = useCallback((taskId: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            return;
        }

        wsRef.current.send(JSON.stringify({
            type: 'task.cancel',
            task_id: taskId,
        }));

        setTasks(prev => prev.filter(t => t.id !== taskId));
    }, []);

    // Disconnect from ADK
    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        wsRef.current?.close();
        setIsConnected(false);
        setActiveAgentState(null);
    }, []);

    return {
        agents,
        activeAgent,
        tasks,
        delegateTask,
        cancelTask,
        handoverHistory,
        isConnected,
        isConnecting,
        error,
        connect,
        disconnect,
        setActiveAgent: setActiveAgentState,
    };
}

export default useADKAgents;
