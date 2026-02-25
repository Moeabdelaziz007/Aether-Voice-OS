"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Database, Server, Fingerprint, Clock, Zap, Cpu, Network } from "lucide-react";

export default function AdminDashboard() {
    const [sessions, setSessions] = useState<any[]>([]);
    const [synapse, setSynapse] = useState<any>(null);
    const [status, setStatus] = useState<string>("offline");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [sessRes, synRes, statusRes] = await Promise.all([
                    fetch("http://127.0.0.1:18790/api/sessions").catch(() => null),
                    fetch("http://127.0.0.1:18790/api/synapse").catch(() => null),
                    fetch("http://127.0.0.1:18790/api/status").catch(() => null),
                ]);

                if (sessRes && sessRes.ok) setSessions(await sessRes.json());
                if (synRes && synRes.ok) setSynapse(await synRes.json());
                if (statusRes && statusRes.ok) {
                    const data = await statusRes.json();
                    setStatus(data.status);
                } else {
                    setStatus("offline");
                }
            } catch (e) {
                setStatus("offline");
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    // Helper to format timestamps
    const formatTime = (isoString?: string) => {
        if (!isoString) return "N/A";
        return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    return (
        <main className="min-h-screen bg-black text-white p-6 md:p-12 font-sans overflow-x-hidden selection:bg-purple-500/30">
            {/* Background Effects */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px]" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_100%)] opacity-20" />
            </div>

            <div className="max-w-7xl mx-auto relative z-10">

                {/* Header */}
                <header className="flex flex-col md:flex-row md:items-end justify-between mb-12 border-b border-white/10 pb-6">
                    <div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-white flex items-center gap-3">
                            <Network className="w-10 h-10 text-blue-400" />
                            AetherOS Admin
                        </h1>
                        <p className="text-gray-400 mt-2 flex items-center gap-2 text-sm uppercase tracking-widest font-medium">
                            <Fingerprint size={14} /> Mission Control & Analytics
                        </p>
                    </div>
                    <div className="mt-4 md:mt-0 flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                        <div className={`w-2.5 h-2.5 rounded-full ${status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                        <span className="text-sm font-bold uppercase tracking-wider text-white/80">
                            Engine: {status}
                        </span>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Left Column: Synapse Status */}
                    <div className="lg:col-span-1 space-y-8">
                        <section className="bg-black/40 border border-white/10 rounded-2xl p-6 backdrop-blur-xl relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-white/90">
                                <Cpu className="w-5 h-5 text-purple-400" />
                                L2 Synapse Node
                            </h2>

                            {!synapse ? (
                                <div className="text-gray-500 text-sm flex items-center gap-2">
                                    <Activity className="w-4 h-4 animate-spin" /> Waiting for heartbeat...
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5">
                                        <span className="text-sm text-gray-400">Status</span>
                                        <span className={`text-sm font-bold uppercase ${synapse.status === 'active' ? 'text-green-400' : 'text-yellow-400'}`}>
                                            {synapse.status}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5">
                                        <span className="text-sm text-gray-400">Total Memories</span>
                                        <span className="text-sm font-bold text-white/90">{synapse.total_memories || 0}</span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5">
                                        <span className="text-sm text-gray-400">Total Tasks</span>
                                        <span className="text-sm font-bold text-white/90">{synapse.total_tasks || 0}</span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5">
                                        <span className="text-sm text-gray-400">Last Sync</span>
                                        <span className="text-sm font-medium text-gray-300">
                                            {formatTime(synapse.last_heartbeat)}
                                        </span>
                                    </div>
                                </div>
                            )}
                        </section>

                        <section className="bg-black/40 border border-white/10 rounded-2xl p-6 backdrop-blur-xl relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-orange-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-white/90">
                                <Zap className="w-5 h-5 text-red-400" />
                                System Health
                            </h2>
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                                    <div className="text-red-400 text-xs font-bold uppercase tracking-wider mb-1">Voice Pipeline</div>
                                    <div className="text-white/80 text-sm">Thalamic Gate: Active</div>
                                    <div className="text-white/80 text-sm mt-1">AEC: Software RMS</div>
                                    <div className="text-white/80 text-sm mt-1">Latency: ~300ms</div>
                                </div>
                            </div>
                        </section>
                    </div>

                    {/* Right Column: Sessions */}
                    <div className="lg:col-span-2 space-y-8">
                        <section className="bg-black/40 border border-white/10 rounded-2xl p-6 backdrop-blur-xl relative overflow-hidden">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold flex items-center gap-2 text-white/90">
                                    <Database className="w-5 h-5 text-blue-400" />
                                    Recent Sessions
                                </h2>
                                <span className="text-xs font-bold uppercase tracking-widest text-gray-500 bg-white/5 px-2 py-1 rounded">Firestore</span>
                            </div>

                            <div className="space-y-3">
                                <AnimatePresence>
                                    {sessions.length === 0 ? (
                                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12 text-gray-500 border border-dashed border-white/10 rounded-xl">
                                            No recent sessions found.
                                        </motion.div>
                                    ) : (
                                        sessions.map((session, idx) => (
                                            <motion.div
                                                key={session.id || idx}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: idx * 0.05 }}
                                                className="group relative overflow-hidden bg-white/5 border border-white/10 hover:border-white/20 rounded-xl p-4 transition-all"
                                            >
                                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />

                                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                                    <div>
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <span className="text-sm font-mono text-blue-300">{session.id}</span>
                                                            {session.status === 'active' ? (
                                                                <span className="text-[10px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">Active</span>
                                                            ) : (
                                                                <span className="text-[10px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full bg-gray-500/20 text-gray-400 border border-gray-500/30">Ended</span>
                                                            )}
                                                        </div>
                                                        <div className="text-xs text-gray-400 flex items-center gap-3">
                                                            <span className="flex items-center gap-1"><Server size={12} /> {session.model || 'Unknown'}</span>
                                                            <span className="flex items-center gap-1"><Clock size={12} /> Started: {formatTime(session.started_at)}</span>
                                                        </div>
                                                    </div>

                                                    {session.summary && session.summary.tools_used && (
                                                        <div className="flex flex-wrap gap-2 justify-end max-w-[200px]">
                                                            {session.summary.tools_used.map((tool: any, i: number) => (
                                                                <span key={i} className="text-[10px] bg-white/10 text-white/70 px-2 py-1 rounded">
                                                                    {String(tool)}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            </motion.div>
                                        ))
                                    )}
                                </AnimatePresence>
                            </div>
                        </section>
                    </div>

                </div>
            </div>
        </main>
    );
}
