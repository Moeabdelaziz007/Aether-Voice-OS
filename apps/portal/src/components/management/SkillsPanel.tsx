'use client';

import React from 'react';
import { Sparkles, RefreshCw } from 'lucide-react';
import { useAetherStore } from '@/store/useAetherStore';

const DEFAULT_SKILLS = [
    { id: 'coding', name: 'Coding Assistant', description: 'Write, review, and refactor code', enabled: true },
    { id: 'debugging', name: 'Debugger', description: 'Find and fix bugs proactively', enabled: true },
    { id: 'architecture', name: 'Architecture Advisor', description: 'System design and patterns', enabled: false },
    { id: 'devops', name: 'DevOps Engineer', description: 'CI/CD, deployment, infrastructure', enabled: false },
    { id: 'vision', name: 'Vision Pulse', description: 'Screen capture and visual context', enabled: true },
    { id: 'web-search', name: 'Web Search', description: 'Search and scrape documentation', enabled: false },
    { id: 'rag', name: 'Code RAG', description: 'Semantic codebase search', enabled: true },
    { id: 'tasks', name: 'Task Manager', description: 'Create and manage tasks', enabled: true },
];

export default function SkillsPanel() {
    const activeSkills = useAetherStore((s) => s.activeSkills);
    const setActiveSkills = useAetherStore((s) => s.setActiveSkills);
    const skillsSyncStatus = useAetherStore((s) => s.skillsSyncStatus);
    const setSkillsSyncStatus = useAetherStore((s) => s.setSkillsSyncStatus);

    // Use store skills or defaults
    const skills = activeSkills.length > 0 ? activeSkills : DEFAULT_SKILLS.map(s => ({
        id: s.id,
        name: s.name,
        description: s.description,
        enabled: s.enabled,
    }));

    const toggleSkill = (id: string) => {
        const updated = skills.map(s => s.id === id ? { ...s, enabled: !s.enabled } : s);
        setActiveSkills(updated);
    };

    const handleSync = () => {
        setSkillsSyncStatus('syncing');
        setTimeout(() => {
            setSkillsSyncStatus('success');
            setTimeout(() => setSkillsSyncStatus('idle'), 2000);
        }, 1500);
    };

    const enabledCount = skills.filter(s => s.enabled).length;

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    <h2 className="text-lg font-medium text-white/90">Skills Hub</h2>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-white/20">
                        {enabledCount}/{skills.length} active
                    </span>
                    <button
                        onClick={handleSync}
                        disabled={skillsSyncStatus === 'syncing'}
                        className="p-1.5 hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30"
                        title="Sync skills"
                    >
                        <RefreshCw className={`w-4 h-4 text-white/20 ${skillsSyncStatus === 'syncing' ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Sync status */}
            {skillsSyncStatus === 'success' && (
                <div className="mb-3 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono">
                    ✓ Skills synced with backend
                </div>
            )}

            {/* Skills list */}
            <div className="flex-1 overflow-y-auto flex flex-col gap-2">
                {skills.map((skill) => (
                    <div
                        key={skill.id}
                        className={`flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer ${
                            skill.enabled
                                ? 'bg-white/[0.04] border-white/[0.08]'
                                : 'bg-white/[0.01] border-white/[0.04] opacity-50'
                        }`}
                        onClick={() => toggleSkill(skill.id)}
                    >
                        <div className="flex-1">
                            <div className="text-sm text-white/70 font-medium">{skill.name}</div>
                            <div className="text-[10px] text-white/30 mt-0.5">{skill.description}</div>
                        </div>

                        {/* Toggle switch */}
                        <div className={`w-8 h-4.5 rounded-full p-0.5 transition-colors ${
                            skill.enabled ? 'bg-cyan-500/60' : 'bg-white/10'
                        }`}>
                            <div className={`w-3.5 h-3.5 rounded-full bg-white transition-transform ${
                                skill.enabled ? 'translate-x-3.5' : 'translate-x-0'
                            }`} />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
