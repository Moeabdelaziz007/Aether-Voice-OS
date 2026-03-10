'use client';

import React from 'react';
import clsx from 'clsx';
import { useAetherStore } from '@/store/useAetherStore';

/**
 * Latency HUD — Real-time performance metrics for Gemini Live
 * Designed for "Industrial Sci-Fi" aesthetics for the Gemini Live Agent Challenge.
 */
export function LatencyHUD() {
    const latencyMs = useAetherStore((s) => s.latencyMs);
    const p50 = useAetherStore((s) => s.p50);
    const p95 = useAetherStore((s) => s.p95);
    const p99 = useAetherStore((s) => s.p99);

    const getLatencyStatus = (val: number) => {
        if (val > 500) return 'critical';
        if (val > 250) return 'warning';
        return 'healthy';
    };

    const statusColors = {
        healthy: 'text-cyan-400',
        warning: 'text-yellow-400',
        critical: 'text-red-500 animate-pulse',
    };

    return (
        <div className="latency-hud ultra-glass border border-white/10 rounded-lg p-3 w-64 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-2">
                <h4 className="text-[10px] uppercase tracking-[0.2em] text-white/50 font-bold">Latency Telemetry</h4>
                <div className={clsx('w-2 h-2 rounded-full', latencyMs > 300 ? 'bg-red-500 animate-pulse' : 'bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]')} />
            </div>

            <div className="grid grid-cols-2 gap-2 mt-4">
                {/* Real-time Latency */}
                <div className="col-span-2 bg-white/5 rounded p-2 border border-white/5">
                    <div className="text-[9px] text-white/40 uppercase mb-1">Live Ping</div>
                    <div className={clsx('text-xl font-mono font-bold leading-none', statusColors[getLatencyStatus(latencyMs)])}>
                        {latencyMs}<span className="text-[10px] ml-1">MS</span>
                    </div>
                </div>

                {/* Percentiles */}
                <div className="bg-white/5 rounded p-2 border border-white/5">
                    <div className="text-[9px] text-white/40 uppercase mb-1">P50</div>
                    <div className="text-md font-mono text-white/80 leading-none">
                        {Math.round(p50)}<span className="text-[8px] ml-1">MS</span>
                    </div>
                </div>

                <div className="bg-white/5 rounded p-2 border border-white/5">
                    <div className="text-[9px] text-white/40 uppercase mb-1">P95</div>
                    <div className={clsx('text-md font-mono leading-none', p95 > 250 ? 'text-yellow-400' : 'text-white/80')}>
                        {Math.round(p95)}<span className="text-[8px] ml-1">MS</span>
                    </div>
                </div>

                <div className="col-span-2 bg-white/5 rounded p-2 border border-white/5 relative overflow-hidden">
                    <div className="text-[9px] text-white/40 uppercase mb-1">P99 (Max Tail)</div>
                    <div className={clsx('text-lg font-mono font-bold leading-none', p99 > 500 ? 'text-red-500' : 'text-white/80')}>
                        {Math.round(p99)}<span className="text-[8px] ml-1 font-normal">MS</span>
                    </div>
                    {/* Progress bar visualizer */}
                    <div className="absolute bottom-0 left-0 h-[2px] bg-cyan-500/30 w-full" />
                    <div
                        className={clsx('absolute bottom-0 left-0 h-[2px] transition-all duration-500', p99 > 500 ? 'bg-red-500' : 'bg-cyan-500')}
                        style={{ width: `${Math.min((p99 / 1000) * 100, 100)}%` }}
                    />
                </div>
            </div>

            <div className="mt-3 pt-2 border-t border-white/5 flex gap-2">
                <div className="h-1 flex-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 w-[70%]" />
                </div>
                <div className="h-1 flex-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 w-[45%]" />
                </div>
                <div className="h-1 flex-1 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 w-[90%]" />
                </div>
            </div>
        </div>
    );
}
