'use client';

/**
 * SRE Heartbeat — System Health Telemetry Display
 * 
 * Real-time monitoring dashboard for AetherOS system health.
 * Features:
 * - Live heartbeat visualization (ECG-style)
 * - System metrics grid (CPU, Memory, Network, Latency)
 * - Service status indicators
 * - Error rate tracking
 * - Uptime counter
 * - Alert notifications
 */

import React, { useEffect, useRef, useState } from 'react';
import clsx from 'clsx';

interface SystemMetrics {
    activeConnections: number;
    interruptLatency: number; // ms
}

interface ServiceStatus {
    name: string;
    status: 'healthy' | 'degraded' | 'down';
    latency?: number;
    lastCheck: string;
}

interface SREHeartbeatProps {
    className?: string;
    metrics?: Partial<SystemMetrics>;
    services?: ServiceStatus[];
    showGraph?: boolean;
    compact?: boolean;
}

export function SREHeartbeat({
    className,
    metrics = {},
    services = [],
    showGraph = true,
    compact = false,
}: SREHeartbeatProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [heartbeatData, setHeartbeatData] = useState<number[]>([]);
    const [currentBeat, setCurrentBeat] = useState(0);
    const animationRef = useRef<number>(0);

    // Default metrics
    const systemMetrics: SystemMetrics = {
        cpu: metrics.cpu ?? 45,
        memory: metrics.memory ?? 62,
        networkIn: metrics.networkIn ?? 12.5,
        networkOut: metrics.networkOut ?? 8.3,
        latency: metrics.latency ?? 24,
        errorRate: metrics.errorRate ?? 0.2,
        uptime: metrics.uptime ?? 86400,
        activeConnections: metrics.activeConnections ?? 142,
        interruptLatency: metrics.interruptLatency ?? 0,
    };

    // Animate ECG heartbeat line
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !showGraph) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;
        const dataPoints: number[] = [];
        let position = 0;
        let beatPhase = 0;

        // Initialize with flat line
        for (let i = 0; i < width; i++) {
            dataPoints.push(height / 2);
        }

        const animate = () => {
            ctx.clearRect(0, 0, width, height);

            // Generate heartbeat waveform
            beatPhase += 0.08;
            const baseLine = height / 2;
            let amplitude = 0;

            // PQRST complex simulation (heartbeat spike pattern)
            const beatCycle = beatPhase % (Math.PI * 2);

            if (beatCycle < 0.3) {
                // P wave (small bump)
                amplitude = Math.sin(beatCycle / 0.3 * Math.PI) * 8;
            } else if (beatCycle >= 0.5 && beatCycle < 0.7) {
                // Q wave (small dip)
                amplitude = -Math.sin((beatCycle - 0.5) / 0.2 * Math.PI) * 6;
            } else if (beatCycle >= 0.7 && beatCycle < 0.9) {
                // R wave (big spike)
                amplitude = Math.sin((beatCycle - 0.7) / 0.2 * Math.PI) * 40;
            } else if (beatCycle >= 0.9 && beatCycle < 1.1) {
                // S wave (deep dip)
                amplitude = -Math.sin((beatCycle - 0.9) / 0.2 * Math.PI) * 12;
            } else if (beatCycle >= 1.1 && beatCycle < 1.4) {
                // T wave (medium bump)
                amplitude = Math.sin((beatCycle - 1.1) / 0.3 * Math.PI) * 10;
            }

            // Add some noise for realism
            amplitude += (Math.random() - 0.5) * 3;

            // Shift data
            dataPoints.shift();
            dataPoints.push(baseLine + amplitude);

            // Draw grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            ctx.lineWidth = 1;
            for (let i = 0; i < width; i += 40) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, height);
                ctx.stroke();
            }
            for (let i = 0; i < height; i += 40) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(width, i);
                ctx.stroke();
            }

            // Draw ECG line
            ctx.beginPath();
            ctx.moveTo(0, dataPoints[0]);

            for (let i = 1; i < dataPoints.length; i++) {
                ctx.lineTo(i, dataPoints[i]);
            }

            // Gradient stroke
            const gradient = ctx.createLinearGradient(0, 0, width, 0);
            gradient.addColorStop(0, 'rgba(6, 182, 212, 0)');
            gradient.addColorStop(0.7, 'rgba(6, 182, 212, 0.8)');
            gradient.addColorStop(1, 'rgba(6, 182, 212, 1)');

            ctx.strokeStyle = gradient;
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.stroke();

            // Glow effect
            ctx.shadowColor = 'rgba(6, 182, 212, 0.6)';
            ctx.shadowBlur = 10;
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Draw moving dot at tip
            const tipX = width - 1;
            const tipY = dataPoints[dataPoints.length - 1];

            ctx.beginPath();
            ctx.arc(tipX, tipY, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#06B6D4';
            ctx.fill();

            setCurrentBeat(amplitude);
            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(animationRef.current);
        };
    }, [showGraph]);

    // Format uptime
    const formatUptime = (seconds: number) => {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${days}d ${hours}h ${minutes}m`;
    };

    // Get status color
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'text-green-400 bg-green-500/20 border-green-500/30';
            case 'degraded': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
            case 'down': return 'text-red-400 bg-red-500/20 border-red-500/30';
            default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
        }
    };

    if (compact) {
        return (
            <div className={clsx('sre-heartbeat-compact flex items-center gap-4', className)}>
                {/* Mini Heartbeat Graph */}
                <div className="w-24 h-12 rounded bg-black/50 overflow-hidden border border-white/10">
                    <canvas ref={canvasRef} width={96} height={48} className="w-full h-full" />
                </div>

                {/* Quick Stats */}
                <div className="flex gap-4 text-xs">
                    <div>
                        <div className="text-white/50">CPU</div>
                        <div className={clsx('font-mono', systemMetrics.cpu > 80 ? 'text-red-400' : 'text-white/90')}>
                            {systemMetrics.cpu}%
                        </div>
                    </div>
                    <div>
                        <div className="text-white/50">Memory</div>
                        <div className={clsx('font-mono', systemMetrics.memory > 80 ? 'text-red-400' : 'text-white/90')}>
                            {systemMetrics.memory}%
                        </div>
                    </div>
                    <div>
                        <div className="text-white/50">Latency</div>
                        <div className={clsx('font-mono', systemMetrics.latency > 100 ? 'text-red-400' : 'text-white/90')}>
                            {systemMetrics.latency}ms
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={clsx('sre-heartbeat-dashboard ultra-glass rounded-xl p-6 border border-white/10', className)}>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <h3 className="text-white/90 font-semibold text-lg">SRE Heartbeat Monitor</h3>
                </div>

                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    <span className="text-green-400 text-sm font-medium">System Healthy</span>
                </div>
            </div>

            {/* ECG Graph */}
            {showGraph && (
                <div className="ecg-graph mb-6 rounded-lg overflow-hidden bg-black/50 border border-white/10">
                    <canvas
                        ref={canvasRef}
                        width={800}
                        height={160}
                        className="w-full h-40"
                    />
                </div>
            )}

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <MetricCard
                    label="CPU Usage"
                    value={`${systemMetrics.cpu}%`}
                    icon="🖥️"
                    status={systemMetrics.cpu > 80 ? 'warning' : systemMetrics.cpu > 90 ? 'critical' : 'normal'}
                />
                <MetricCard
                    label="Memory"
                    value={`${systemMetrics.memory}%`}
                    icon="💾"
                    status={systemMetrics.memory > 80 ? 'warning' : systemMetrics.memory > 90 ? 'critical' : 'normal'}
                />
                <MetricCard
                    label="Network In"
                    value={`${systemMetrics.networkIn.toFixed(1)} Mb/s`}
                    icon="⬇️"
                    status="normal"
                />
                <MetricCard
                    label="Network Out"
                    value={`${systemMetrics.networkOut.toFixed(1)} Mb/s`}
                    icon="⬆️"
                    status="normal"
                />
                <MetricCard
                    label="Latency"
                    value={`${systemMetrics.latency}ms`}
                    icon="⚡"
                    status={systemMetrics.latency > 100 ? 'warning' : systemMetrics.latency > 200 ? 'critical' : 'normal'}
                />
                <MetricCard
                    label="Error Rate"
                    value={`${systemMetrics.errorRate.toFixed(1)}/min`}
                    icon="❌"
                    status={systemMetrics.errorRate > 1 ? 'warning' : systemMetrics.errorRate > 5 ? 'critical' : 'normal'}
                />
                <MetricCard
                    label="Active Connections"
                    value={systemMetrics.activeConnections.toString()}
                    icon="🔗"
                    status="normal"
                />
                <MetricCard
                    label="Uptime"
                    value={formatUptime(systemMetrics.uptime)}
                    icon="⏱️"
                    status="normal"
                />
                <MetricCard
                    label="Interrupt Latency"
                    value={`${systemMetrics.interruptLatency.toFixed(1)}ms`}
                    icon="🔴"
                    status={systemMetrics.interruptLatency > 150 ? 'critical' : systemMetrics.interruptLatency > 100 ? 'warning' : 'normal'}
                />
            </div>

            {/* Service Status */}
            {services.length > 0 && (
                <div className="services-section">
                    <h4 className="text-white/70 font-medium mb-3">Service Status</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {services.map((service) => (
                            <div
                                key={service.name}
                                className={clsx(
                                    'service-status-card p-3 rounded-lg border flex items-center justify-between',
                                    getStatusColor(service.status)
                                )}
                            >
                                <div className="flex items-center gap-2">
                                    <div className={clsx(
                                        'w-2 h-2 rounded-full',
                                        service.status === 'healthy' ? 'bg-green-400 animate-pulse' :
                                            service.status === 'degraded' ? 'bg-yellow-400' : 'bg-red-400'
                                    )} />
                                    <span className="text-sm font-medium">{service.name}</span>
                                </div>
                                <div className="text-xs opacity-70">
                                    {service.latency ? `${service.latency}ms` : ''}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

/**
 * Individual Metric Card Component
 */
function MetricCard({
    label,
    value,
    icon,
    status = 'normal',
}: {
    label: string;
    value: string | number;
    icon: string;
    status?: 'normal' | 'warning' | 'critical';
}) {
    const statusColors = {
        normal: 'bg-white/5 border-white/10',
        warning: 'bg-yellow-500/10 border-yellow-500/30',
        critical: 'bg-red-500/10 border-red-500/30',
    };

    const valueColors = {
        normal: 'text-white/90',
        warning: 'text-yellow-400',
        critical: 'text-red-400',
    };

    return (
        <div className={clsx('metric-card p-4 rounded-lg border transition-all hover:scale-105', statusColors[status])}>
            <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{icon}</span>
                <span className="text-white/50 text-xs">{label}</span>
            </div>
            <div className={clsx('text-2xl font-mono font-bold', valueColors[status])}>
                {value}
            </div>
        </div>
    );
}

export default SREHeartbeat;
