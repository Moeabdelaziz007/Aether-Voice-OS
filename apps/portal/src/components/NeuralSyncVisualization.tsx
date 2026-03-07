/**
 * Aether Voice OS — Neural Sync Visualization
 * 
 * Real-time visualization of neural synchronization between:
 * - User voice input (audio waveform)
 * - Gemini session state (connection status)
 * - ADK agent activity (which specialist is active)
 * - Handover events (agent transitions)
 * 
 * Features:
 * - Multi-channel audio visualization
 * - Agent neural pathway connections
 * - Sync quality indicator
 * - Latency heatmap
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';

interface NeuralSyncProps {
    isListening?: boolean;
    isSpeaking?: boolean;
    activeAgent?: string;
    agents?: string[];
    syncQuality?: number; // 0-100
    latencyMs?: number;
    showHeatmap?: boolean;
}

interface NeuralPathway {
    id: string;
    from: string;
    to: string;
    activity: number; // 0-1
    color: string;
}

export const NeuralSyncVisualization: React.FC<NeuralSyncProps> = ({
    isListening = false,
    isSpeaking = false,
    activeAgent = 'AetherCore',
    agents = ['AetherCore', 'ArchitectAgent', 'DebuggerAgent'],
    syncQuality = 85,
    latencyMs = 120,
    showHeatmap = true,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [pathways, setPathways] = useState<NeuralPathway[]>([]);
    const [pulsePhase, setPulsePhase] = useState(0);

    // Generate neural pathways between agents
    useEffect(() => {
        const generated: NeuralPathway[] = [];
        
        // Create bidirectional pathways
        for (let i = 0; i < agents.length; i++) {
            for (let j = i + 1; j < agents.length; j++) {
                generated.push({
                    id: `${agents[i]}-${agents[j]}`,
                    from: agents[i],
                    to: agents[j],
                    activity: Math.random() * 0.5 + 0.3,
                    color: agents[i] === activeAgent || agents[j] === activeAgent 
                        ? '#06B6D4' // Cyan for active pathways
                        : '#6366F1', // Indigo for inactive
                });
            }
        }
        
        setPathways(generated);
    }, [agents, activeAgent]);

    // Animate neural pulses
    useEffect(() => {
        const interval = setInterval(() => {
            setPulsePhase(prev => (prev + 0.05) % (Math.PI * 2));
        }, 16); // ~60fps
        
        return () => clearInterval(interval);
    }, []);

    // Draw neural sync visualization
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        const width = canvas.width;
        const height = canvas.height;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.35;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw background gradient
        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 1.5);
        gradient.addColorStop(0, 'rgba(2, 0, 5, 0.8)');
        gradient.addColorStop(1, 'rgba(10, 10, 15, 0.95)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
        
        // Calculate agent positions (equilateral triangle or circle)
        const agentPositions: Record<string, { x: number; y: number }> = {};
        const angleStep = (Math.PI * 2) / agents.length;
        
        agents.forEach((agent, index) => {
            const angle = index * angleStep - Math.PI / 2; // Start from top
            agentPositions[agent] = {
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
            };
        });
        
        // Draw neural pathways
        pathways.forEach((pathway) => {
            const from = agentPositions[pathway.from];
            const to = agentPositions[pathway.to];
            
            if (!from || !to) return;
            
            // Pathway glow
            ctx.shadowBlur = 15;
            ctx.shadowColor = pathway.color;
            
            // Pathway line with pulse animation
            const pulseIntensity = Math.sin(pulsePhase + pathway.id.length) * 0.3 + 0.7;
            ctx.strokeStyle = pathway.color.replace(')', `, ${pulseIntensity * pathway.activity})`).replace('rgb', 'rgba');
            ctx.lineWidth = 2 + pulseIntensity * 2;
            
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();
            
            // Reset shadow
            ctx.shadowBlur = 0;
        });
        
        // Draw agent nodes
        Object.entries(agentPositions).forEach(([agent, pos]) => {
            const isActive = agent === activeAgent;
            const nodeRadius = isActive ? 25 : 18;
            
            // Node glow
            if (isActive) {
                ctx.shadowBlur = 25;
                ctx.shadowColor = '#06B6D4';
            }
            
            // Node circle
            const nodeGradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, nodeRadius);
            nodeGradient.addColorStop(0, '#06B6D4');
            nodeGradient.addColorStop(1, '#0891b2');
            
            ctx.fillStyle = nodeGradient;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, nodeRadius, 0, Math.PI * 2);
            ctx.fill();
            
            // Node border
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Reset shadow
            ctx.shadowBlur = 0;
            
            // Agent label
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.font = '11px Outfit, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(agent.replace('Agent', ''), pos.x, pos.y + nodeRadius + 18);
        });
        
        // Draw central sync core
        const coreRadius = 30;
        const syncIntensity = syncQuality / 100;
        
        // Core pulsing glow
        const coreGlow = Math.sin(pulsePhase * 2) * 0.2 + 0.8;
        ctx.shadowBlur = 30 * coreGlow;
        ctx.shadowColor = `rgba(6, 182, 212, ${coreGlow})`;
        
        const coreGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, coreRadius);
        coreGradient.addColorStop(0, 'rgba(6, 182, 212, 0.9)');
        coreGradient.addColorStop(0.5, 'rgba(6, 182, 212, 0.4)');
        coreGradient.addColorStop(1, 'rgba(6, 182, 212, 0)');
        
        ctx.fillStyle = coreGradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
        ctx.fill();
        
        // Reset shadow
        ctx.shadowBlur = 0;
        
        // Draw audio activity rings
        if (isListening || isSpeaking) {
            const audioRadius = coreRadius + 10;
            const audioActivity = isListening ? 0.8 : isSpeaking ? 0.6 : 0;
            
            for (let i = 0; i < 3; i++) {
                const ringRadius = audioRadius + i * 8;
                const ringOpacity = audioActivity * (1 - i / 3) * 0.4;
                
                ctx.strokeStyle = `rgba(6, 182, 212, ${ringOpacity})`;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(centerX, centerY, ringRadius, 0, Math.PI * 2);
                ctx.stroke();
            }
        }
        
    }, [agents, activeAgent, syncQuality, isListening, isSpeaking, pulsePhase, pathways]);

    // Calculate sync quality color
    const getSyncColor = () => {
        if (syncQuality >= 80) return '#22C55E'; // Green
        if (syncQuality >= 60) return '#EAB308'; // Yellow
        return '#EF4444'; // Red
    };

    // Calculate latency status
    const getLatencyStatus = () => {
        if (latencyMs < 100) return { label: 'Excellent', color: '#22C55E' };
        if (latencyMs < 200) return { label: 'Good', color: '#EAB308' };
        return { label: 'High', color: '#EF4444' };
    };

    return (
        <div className="relative w-full h-full min-h-[400px]">
            {/* Header */}
            <div className="absolute top-4 left-4 z-10">
                <h3 className="text-lg font-bold text-white tracking-wide">
                    Neural Sync
                </h3>
                <p className="text-xs text-cyan-400/70 mt-1">
                    Agent Synchronization Matrix
                </p>
            </div>

            {/* Sync Quality Badge */}
            <div className="absolute top-4 right-4 z-10">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/40 backdrop-blur-md border border-white/10">
                    <div 
                        className="w-2 h-2 rounded-full animate-pulse"
                        style={{ backgroundColor: getSyncColor() }}
                    />
                    <span className="text-sm font-semibold text-white">{syncQuality}%</span>
                    <span className="text-xs text-gray-400">Sync</span>
                </div>
            </div>

            {/* Latency Indicator */}
            <div className="absolute bottom-4 left-4 z-10">
                <div className="px-3 py-2 rounded-lg bg-black/40 backdrop-blur-md border border-white/10">
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400">Latency</span>
                        <span 
                            className="text-sm font-bold"
                            style={{ color: getLatencyStatus().color }}
                        >
                            {latencyMs}ms
                        </span>
                    </div>
                    <div className="mt-1 flex items-center gap-1">
                        <div 
                            className="w-1.5 h-1.5 rounded-full"
                            style={{ backgroundColor: getLatencyStatus().color }}
                        />
                        <span className="text-xs" style={{ color: getLatencyStatus().color }}>
                            {getLatencyStatus().label}
                        </span>
                    </div>
                </div>
            </div>

            {/* Activity Indicators */}
            <div className="absolute bottom-4 right-4 z-10 flex gap-2">
                {isListening && (
                    <div className="px-3 py-1.5 rounded-lg bg-cyan-500/20 backdrop-blur-md border border-cyan-500/30">
                        <span className="text-xs font-semibold text-cyan-400">🎤 Listening</span>
                    </div>
                )}
                {isSpeaking && (
                    <div className="px-3 py-1.5 rounded-lg bg-purple-500/20 backdrop-blur-md border border-purple-500/30">
                        <span className="text-xs font-semibold text-purple-400">🔊 Speaking</span>
                    </div>
                )}
            </div>

            {/* Main Canvas */}
            <canvas
                ref={canvasRef}
                width={800}
                height={600}
                className="w-full h-full object-cover"
                style={{ filter: 'blur(0.3px)' }}
            />

            {/* Heatmap Overlay (Optional) */}
            {showHeatmap && (
                <div className="absolute inset-0 pointer-events-none opacity-30">
                    <div className="w-full h-full bg-gradient-to-br from-cyan-500/10 via-transparent to-purple-500/10" />
                </div>
            )}
        </div>
    );
};

export default NeuralSyncVisualization;
