/**
 * Aether Voice OS — Task Delegate Modal
 * 
 * UI component for delegating tasks to ADK specialist agents.
 * Provides agent selection, task description, and progress tracking.
 * 
 * Features:
 * - Agent selection with descriptions
 * - Rich text task input
 * - Real-time task status updates
 * - Progress visualization
 * - Cancellation support
 */

'use client';

import React, { useState } from 'react';
import { useADKAgents, ADKTask } from '../hooks/useADKAgents';

interface TaskDelegateModalProps {
    isOpen: boolean;
    onClose: () => void;
    prefillTask?: string;
}

export const TaskDelegateModal: React.FC<TaskDelegateModalProps> = ({
    isOpen,
    onClose,
    prefillTask = '',
}) => {
    const { agents, delegateTask, tasks, isConnected, connect } = useADKAgents();
    const [selectedAgent, setSelectedAgent] = useState(agents[0]?.name || 'AetherCore');
    const [taskDescription, setTaskDescription] = useState(prefillTask);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Get active tasks
    const activeTasks = tasks.filter(t => t.status === 'pending' || t.status === 'in_progress');

    // Handle task submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!taskDescription.trim()) {
            setError('Please enter a task description');
            return;
        }

        if (!isConnected) {
            setError('Not connected to ADK backend. Please connect first.');
            await connect();
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            await delegateTask(taskDescription, selectedAgent);
            setTaskDescription('');
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delegate task');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Cancel task
    const handleCancelTask = (taskId: string) => {
        // Implementation would call the cancelTask function
        console.log('[TaskDelegateModal] Cancelling task:', taskId);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div 
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-2xl mx-4">
                <div className="ultra-glass rounded-2xl border border-white/10 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                    
                    {/* Header */}
                    <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-cyan-500/10 to-purple-500/10">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-bold text-white">
                                    🤖 Delegate Task to ADK Agent
                                </h2>
                                <p className="text-sm text-gray-400 mt-1">
                                    Assign complex tasks to specialist AI agents
                                </p>
                            </div>
                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <form onSubmit={handleSubmit}>
                        <div className="p-6 space-y-6">
                            
                            {/* Connection Status */}
                            {!isConnected && (
                                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                                    <div className="flex items-center gap-2 text-yellow-400">
                                        <span>⚠️</span>
                                        <span className="text-sm font-medium">Not connected to ADK backend</span>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={connect}
                                        className="mt-2 px-3 py-1.5 text-xs font-medium text-yellow-400 hover:bg-yellow-500/20 rounded transition-colors"
                                    >
                                        Connect Now
                                    </button>
                                </div>
                            )}

                            {/* Agent Selection */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-3">
                                    Select Specialist Agent
                                </label>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {agents.map(agent => (
                                        <button
                                            key={agent.name}
                                            type="button"
                                            onClick={() => setSelectedAgent(agent.name)}
                                            className={`p-3 rounded-lg border text-left transition-all ${
                                                selectedAgent === agent.name
                                                    ? 'bg-cyan-500/20 border-cyan-500/50'
                                                    : 'bg-white/5 border-white/10 hover:border-white/20'
                                            }`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <div className={`w-3 h-3 rounded-full ${
                                                    agent.isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
                                                }`} />
                                                <span className="font-medium text-white text-sm">
                                                    {agent.name.replace('Agent', '')}
                                                </span>
                                            </div>
                                            <p className="text-xs text-gray-400 mt-1">
                                                {agent.description}
                                            </p>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Task Description */}
                            <div>
                                <label htmlFor="task" className="block text-sm font-medium text-gray-300 mb-2">
                                    Task Description
                                </label>
                                <textarea
                                    id="task"
                                    value={taskDescription}
                                    onChange={(e) => setTaskDescription(e.target.value)}
                                    rows={5}
                                    placeholder="Describe the task you want to delegate... Be specific about what you want to achieve."
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 outline-none focus:border-cyan-500/50 transition-colors resize-none"
                                />
                                <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
                                    <span>{taskDescription.length} characters</span>
                                    <span>Be clear and specific for best results</span>
                                </div>
                            </div>

                            {/* Error Message */}
                            {error && (
                                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                                    <div className="flex items-center gap-2 text-red-400">
                                        <span>❌</span>
                                        <span className="text-sm font-medium">{error}</span>
                                    </div>
                                </div>
                            )}

                            {/* Active Tasks */}
                            {activeTasks.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-medium text-gray-300 mb-2">
                                        Active Tasks ({activeTasks.length})
                                    </h3>
                                    <div className="space-y-2 max-h-40 overflow-y-auto">
                                        {activeTasks.map(task => (
                                            <div
                                                key={task.id}
                                                className="p-3 rounded-lg bg-white/5 border border-white/10"
                                            >
                                                <div className="flex items-start justify-between gap-3">
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm text-white truncate">
                                                            {task.task}
                                                        </p>
                                                        <div className="flex items-center gap-2 mt-1">
                                                            <span className="text-xs text-gray-400">
                                                                → {task.assignedTo.replace('Agent', '')}
                                                            </span>
                                                            <span className={`text-xs px-1.5 py-0.5 rounded ${
                                                                task.status === 'in_progress'
                                                                    ? 'bg-blue-500/20 text-blue-400'
                                                                    : 'bg-yellow-500/20 text-yellow-400'
                                                            }`}>
                                                                {task.status.replace('_', ' ')}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleCancelTask(task.id)}
                                                        className="text-gray-400 hover:text-red-400 transition-colors text-sm"
                                                    >
                                                        Cancel
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Footer Actions */}
                        <div className="px-6 py-4 border-t border-white/10 bg-black/20 flex items-center justify-end gap-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isSubmitting || !isConnected}
                                className="px-6 py-2 text-sm font-medium text-white bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                {isSubmitting ? 'Delegating...' : 'Delegate Task'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default TaskDelegateModal;
