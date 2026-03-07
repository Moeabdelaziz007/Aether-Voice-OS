'use client';

import React, { useState } from 'react';
import { Plus, Check, Circle, Trash2 } from 'lucide-react';

interface TaskItem {
    id: string;
    title: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
}

const PRIORITY_COLORS: Record<string, string> = {
    high: 'border-red-500/30',
    medium: 'border-amber-500/30',
    low: 'border-white/10',
};

const INITIAL_TASKS: TaskItem[] = [
    { id: '1', title: 'Review Gemini integration', completed: false, priority: 'high' },
    { id: '2', title: 'Update Firebase rules', completed: true, priority: 'medium' },
    { id: '3', title: 'Test voice pipeline', completed: false, priority: 'high' },
    { id: '4', title: 'Write deployment docs', completed: false, priority: 'low' },
];

export default function TasksWidget() {
    const [tasks, setTasks] = useState<TaskItem[]>(INITIAL_TASKS);
    const [newTask, setNewTask] = useState('');

    const toggleTask = (id: string) => {
        setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
    };

    const addTask = () => {
        if (!newTask.trim()) return;
        setTasks([...tasks, { id: Date.now().toString(), title: newTask, completed: false, priority: 'medium' }]);
        setNewTask('');
    };

    const removeTask = (id: string) => {
        setTasks(tasks.filter(t => t.id !== id));
    };

    const pendingCount = tasks.filter(t => !t.completed).length;

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest">Tasks</span>
                <span className="text-[10px] font-mono text-white/20">{pendingCount} pending</span>
            </div>

            {/* Tasks list */}
            <div className="flex flex-col gap-1.5 flex-1 overflow-y-auto max-h-[140px]">
                {tasks.map((task) => (
                    <div
                        key={task.id}
                        className={`group flex items-center gap-2.5 px-2.5 py-2 rounded-lg border transition-all ${
                            task.completed
                                ? 'bg-white/[0.02] border-white/5 opacity-50'
                                : `bg-white/[0.03] ${PRIORITY_COLORS[task.priority]}`
                        }`}
                    >
                        <button onClick={() => toggleTask(task.id)} className="shrink-0">
                            {task.completed ? (
                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                                <Circle className="w-3.5 h-3.5 text-white/20 hover:text-white/50 transition-colors" />
                            )}
                        </button>
                        <span className={`text-xs flex-1 ${task.completed ? 'line-through text-white/30' : 'text-white/60'}`}>
                            {task.title}
                        </span>
                        <button
                            onClick={() => removeTask(task.id)}
                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            <Trash2 className="w-3 h-3 text-white/20 hover:text-red-400 transition-colors" />
                        </button>
                    </div>
                ))}
            </div>

            {/* Add task input */}
            <div className="flex items-center gap-2 mt-3 pt-2 border-t border-white/5">
                <input
                    type="text"
                    value={newTask}
                    onChange={(e) => setNewTask(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addTask()}
                    placeholder="Add task..."
                    className="flex-1 bg-transparent text-xs text-white/60 placeholder:text-white/15 outline-none"
                />
                <button
                    onClick={addTask}
                    className="p-1 hover:bg-white/5 rounded transition-colors"
                >
                    <Plus className="w-3.5 h-3.5 text-white/30 hover:text-cyan-400 transition-colors" />
                </button>
            </div>
        </div>
    );
}
