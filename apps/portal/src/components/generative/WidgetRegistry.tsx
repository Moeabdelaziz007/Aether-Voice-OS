"use client";

import React from "react";
import { Activity, Shield, Cpu, Network } from "lucide-react";

/**
 * SystemStatusWidget — Real-time health metrics.
 */
function SystemStatusWidget({ cpu, memory, latency }: { cpu: number; memory: number; latency: number }) {
    return (
        <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-mono text-white/60 uppercase tracking-tighter">System Health</span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400">OPTIMAL</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
                <div className="bg-white/5 p-2 rounded-lg border border-white/10">
                    <div className="text-[9px] text-white/30 uppercase">CPU</div>
                    <div className="text-sm font-mono text-white/90">{cpu}%</div>
                </div>
                <div className="bg-white/5 p-2 rounded-lg border border-white/10">
                    <div className="text-[9px] text-white/30 uppercase">MEM</div>
                    <div className="text-sm font-mono text-white/90">{memory}GB</div>
                </div>
                <div className="bg-white/5 p-2 rounded-lg border border-white/10">
                    <div className="text-[9px] text-white/30 uppercase">LAT</div>
                    <div className="text-sm font-mono text-white/90">{latency}ms</div>
                </div>
            </div>
        </div>
    );
}

/**
 * PortStatusWidget — Active network listeners.
 */
function PortStatusWidget({ ports }: { ports: { port: number; status: string }[] }) {
    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 mb-1">
                <Network className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-mono text-white/60 uppercase tracking-tighter">Port Registry</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
                {ports.map((p) => (
                    <div key={p.port} className="flex items-center gap-1.5 px-2 py-1 rounded bg-black/40 border border-white/5">
                        <div className={`w-1.5 h-1.5 rounded-full ${p.status === "listening" ? "bg-emerald-500" : "bg-amber-500"}`} />
                        <span className="text-[10px] font-mono text-white/80">{p.port}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Registry mapping
export const WIDGET_REGISTRY: Record<string, React.FC<any>> = {
    "system_status": SystemStatusWidget,
    "port_registry": PortStatusWidget,
};
