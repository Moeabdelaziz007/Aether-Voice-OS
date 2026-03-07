'use client';

/**
 * Expert Soul-Swap Animations — Agent Transition System
 * 
 * Visual effects for switching between AI expert agents.
 * Features:
 * - Particle dissolution effect (outgoing agent)
 * - Energy coalescence animation (incoming agent)
 * - Neural pathway connections
 * - Color-coded agent signatures
 * - Smooth cross-fade transitions
 */

import React, { useEffect, useState, useRef } from 'react';
import clsx from 'clsx';
import { useMicroAnimations } from '@/hooks/useMicroAnimations';

interface ExpertAgent {
    id: string;
    name: string;
    role: string;
    color: string;
    icon: string;
}

interface SoulSwapAnimationProps {
    fromAgent?: ExpertAgent | null;
    toAgent?: ExpertAgent | null;
    isSwapping?: boolean;
    onSwapComplete?: () => void;
    className?: string;
}

export function SoulSwapAnimation({
    fromAgent,
    toAgent,
    isSwapping = false,
    onSwapComplete,
    className,
}: SoulSwapAnimationProps) {
    const [phase, setPhase] = useState<'idle' | 'dissolve' | 'coalesce' | 'complete'>('idle');
    const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; size: number; delay: number }>>([]);
    const containerRef = useRef<HTMLDivElement>(null);
    const { triggerHapticShake } = useMicroAnimations();

    // Generate particles for dissolution effect
    useEffect(() => {
        if (isSwapping && phase === 'idle') {
            setPhase('dissolve');
            
            // Create dissolution particles
            const newParticles = Array.from({ length: 24 }, (_, i) => ({
                id: i,
                x: Math.random() * 100,
                y: Math.random() * 100,
                size: Math.random() * 8 + 4,
                delay: Math.random() * 0.3,
            }));
            setParticles(newParticles);

            // Trigger haptic feedback
            if (containerRef.current) {
                triggerHapticShake(containerRef.current, 'intense');
            }

            // Phase transitions
            const dissolveTimer = setTimeout(() => {
                setPhase('coalesce');
            }, 800);

            const completeTimer = setTimeout(() => {
                setPhase('complete');
                onSwapComplete?.();
            }, 1600);

            return () => {
                clearTimeout(dissolveTimer);
                clearTimeout(completeTimer);
            };
        } else if (!isSwapping && phase === 'complete') {
            setPhase('idle');
            setParticles([]);
        }
    }, [isSwapping, phase, onSwapComplete, triggerHapticShake]);

    // Get agent color classes
    const getAgentColorClasses = (agent: ExpertAgent | null) => {
        if (!agent) return 'from-gray-500/20 to-gray-500/10 border-gray-500/30 text-gray-400';
        
        const colorMap: Record<string, string> = {
            cyan: 'from-cyan-500/20 to-cyan-500/10 border-cyan-500/30 text-cyan-400',
            blue: 'from-blue-500/20 to-blue-500/10 border-blue-500/30 text-blue-400',
            red: 'from-red-500/20 to-red-500/10 border-red-500/30 text-red-400',
            green: 'from-green-500/20 to-green-500/10 border-green-500/30 text-green-400',
            purple: 'from-purple-500/20 to-purple-500/10 border-purple-500/30 text-purple-400',
            orange: 'from-orange-500/20 to-orange-500/10 border-orange-500/30 text-orange-400',
        };
        
        return colorMap[agent.color] || colorMap.cyan;
    };

    const currentAgent = phase === 'dissolve' ? fromAgent : toAgent;
    const colorClasses = getAgentColorClasses(currentAgent);

    return (
        <div 
            ref={containerRef}
            className={clsx(
                'soul-swap-container relative w-32 h-32 mx-auto',
                className
            )}
        >
            {/* Agent Icon Container */}
            <div className={clsx(
                'agent-icon-wrapper absolute inset-0 flex items-center justify-center rounded-full border-2 transition-all duration-500',
                colorClasses,
                phase === 'dissolve' && 'animate-dissolve-out',
                phase === 'coalesce' && 'animate-coalesce-in',
                phase === 'complete' && 'scale-100 opacity-100'
            )}>
                {currentAgent ? (
                    <div className="text-4xl">{currentAgent.icon}</div>
                ) : (
                    <div className="text-white/30 text-sm">No Agent</div>
                )}
            </div>

            {/* Dissolution Particles (Outgoing Agent) */}
            {phase === 'dissolve' && fromAgent && (
                <div className="particles-layer absolute inset-0 pointer-events-none">
                    {particles.map((particle) => (
                        <div
                            key={particle.id}
                            className="dissolution-particle absolute rounded-full"
                            style={{
                                left: `${particle.x}%`,
                                top: `${particle.y}%`,
                                width: `${particle.size}px`,
                                height: `${particle.size}px`,
                                backgroundColor: `rgba(6, 182, 212, ${0.6 - particle.delay})`,
                                boxShadow: `0 0 ${particle.size * 2}px rgba(6, 182, 212, 0.8)`,
                                animation: `dissolve-fly 0.8s ease-out ${particle.delay}s forwards`,
                            }}
                        />
                    ))}
                </div>
            )}

            {/* Coalescence Ring (Incoming Agent) */}
            {phase === 'coalesce' && toAgent && (
                <>
                    <div className="coalescence-ring absolute inset-0 rounded-full border-2 animate-spin-slow"
                        style={{
                            borderColor: `rgba(${toAgent.color === 'cyan' ? '6, 182, 212' : '59, 130, 246'}, 0.3)`,
                        }}
                    />
                    <div className="energy-core absolute inset-4 rounded-full bg-gradient-to-br from-cyan-500/30 to-blue-500/30 animate-pulse-fast" />
                </>
            )}

            {/* Neural Pathways */}
            {(phase === 'dissolve' || phase === 'coalesce') && (
                <svg className="neural-pathways absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 128 128">
                    {Array.from({ length: 8 }, (_, i) => {
                        const angle = (i / 8) * Math.PI * 2;
                        const x1 = 64 + Math.cos(angle) * 20;
                        const y1 = 64 + Math.sin(angle) * 20;
                        const x2 = 64 + Math.cos(angle) * 56;
                        const y2 = 64 + Math.sin(angle) * 56;
                        
                        return (
                            <line
                                key={i}
                                x1={x1}
                                y1={y1}
                                x2={x2}
                                y2={y2}
                                stroke={`rgba(6, 182, 212, ${phase === 'dissolve' ? 0.4 : 0.6})`}
                                strokeWidth="1"
                                strokeLinecap="round"
                                className={phase === 'dissolve' ? 'animate-pathway-dim' : 'animate-pathway-bright'}
                            />
                        );
                    })}
                </svg>
            )}

            {/* Agent Info Label */}
            <div className="agent-label absolute -bottom-16 left-1/2 -translate-x-1/2 text-center whitespace-nowrap">
                <div className={clsx(
                    'text-sm font-semibold transition-all duration-300',
                    currentAgent ? 'text-white/90' : 'text-white/50'
                )}>
                    {currentAgent?.name || 'Transitioning...'}
                </div>
                <div className={clsx(
                    'text-xs mt-1 transition-all duration-300',
                    currentAgent ? 'text-white/70' : 'text-white/40'
                )}>
                    {currentAgent?.role || ''}
                </div>
            </div>
        </div>
    );
}

/**
 * Agent Switcher Control Panel
 */
export function AgentSwitcher({ 
    availableAgents,
    activeAgentId,
    onSwitchAgent,
    className 
}: {
    availableAgents: ExpertAgent[];
    activeAgentId: string | null;
    onSwitchAgent: (agentId: string) => void;
    className?: string;
}) {
    const [isSwapping, setIsSwapping] = useState(false);
    const [swapTarget, setSwapTarget] = useState<ExpertAgent | null>(null);

    const handleSwitch = async (agent: ExpertAgent) => {
        if (isSwapping || agent.id === activeAgentId) return;
        
        setIsSwapping(true);
        setSwapTarget(agent);
        
        // Simulate swap delay
        await new Promise(resolve => setTimeout(resolve, 1800));
        
        onSwitchAgent(agent.id);
        setIsSwapping(false);
        setSwapTarget(null);
    };

    const activeAgent = availableAgents.find(a => a.id === activeAgentId) || null;

    return (
        <div className={clsx('agent-switcher-panel ultra-glass rounded-xl p-6 border border-white/10', className)}>
            <div className="mb-6">
                <h3 className="text-white/90 font-semibold mb-1">Active Expert</h3>
                <p className="text-white/50 text-sm">Switch between specialist AI agents</p>
            </div>

            {/* Current Agent Display */}
            <div className="mb-8">
                <SoulSwapAnimation
                    fromAgent={activeAgent}
                    toAgent={swapTarget || activeAgent}
                    isSwapping={isSwapping}
                    onSwapComplete={() => {}}
                />
            </div>

            {/* Agent Selection Grid */}
            <div className="grid grid-cols-3 gap-3">
                {availableAgents.map((agent) => (
                    <button
                        key={agent.id}
                        onClick={() => handleSwitch(agent)}
                        disabled={isSwapping || agent.id === activeAgentId}
                        className={clsx(
                            'agent-selector-btn p-3 rounded-lg border transition-all magnetic-hover interactive-element',
                            agent.id === activeAgentId
                                ? `bg-${agent.color}-500/20 border-${agent.color}-500/30`
                                : 'bg-white/5 border-white/10 hover:bg-white/10',
                            (isSwapping || agent.id === activeAgentId) && 'opacity-50 cursor-not-allowed'
                        )}
                    >
                        <div className="text-2xl mb-1">{agent.icon}</div>
                        <div className="text-white/90 text-xs font-medium">{agent.name}</div>
                        <div className="text-white/50 text-[10px] mt-0.5">{agent.role}</div>
                    </button>
                ))}
            </div>
        </div>
    );
}

export default SoulSwapAnimation;
