"use client";

import { useAuth } from "@/hooks/useAuth";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { LogOut, User as UserIcon, Settings, Shield } from "lucide-react";

export default function UserAvatar() {
    const { user, logout } = useAuth();
    const [isOpen, setIsOpen] = useState(false);

    if (!user) return null;

    return (
        <div className="relative">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 p-1.5 pr-4 rounded-full bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] transition-colors backdrop-blur-md"
            >
                <div className="relative">
                    {user.photoURL ? (
                        <img
                            src={user.photoURL}
                            alt={user.displayName || "User"}
                            className="w-8 h-8 rounded-full border border-cyan-500/30"
                        />
                    ) : (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center">
                            <UserIcon className="w-4 h-4 text-white" />
                        </div>
                    )}
                    <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-500 border-2 border-[#050505] rounded-full" />
                </div>
                <div className="flex flex-col items-start">
                    <span className="text-[11px] font-bold text-white tracking-tight leading-none mb-0.5">
                        {user.displayName?.split(' ')[0].toUpperCase()}
                    </span>
                    <span className="text-[9px] text-cyan-400/50 font-mono leading-none flex items-center gap-1">
                        <Shield className="w-2 h-2" />
                        VERIFIED
                    </span>
                </div>
            </motion.button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <div
                            className="fixed inset-0 z-40"
                            onClick={() => setIsOpen(false)}
                        />
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            className="absolute right-0 mt-3 w-56 z-50 rounded-xl border border-white/10 bg-[#0a0a0a]/90 backdrop-blur-2xl shadow-2xl p-2 overflow-hidden"
                        >
                            {/* Glass highlight */}
                            <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />

                            <div className="px-3 py-2 mb-2 border-b border-white/5">
                                <p className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest mb-1">Authenticated Account</p>
                                <p className="text-xs font-medium text-white truncate">{user.email}</p>
                            </div>

                            <div className="space-y-1">
                                <button className="w-full flex items-center gap-3 px-3 py-2 text-xs font-medium text-zinc-400 hover:text-white hover:bg-white/5 rounded-lg transition-all group">
                                    <Settings className="w-4 h-4 group-hover:rotate-45 transition-transform" />
                                    Security Settings
                                </button>
                                <button
                                    onClick={() => logout()}
                                    className="w-full flex items-center gap-3 px-3 py-2 text-xs font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-all"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Terminate Session
                                </button>
                            </div>

                            <div className="mt-4 px-3 py-2 bg-white/[0.02] rounded-lg border border-white/5">
                                <div className="flex justify-between items-center text-[8px] font-mono text-zinc-600 uppercase tracking-tight">
                                    <span>Signal Strength</span>
                                    <span className="text-green-500/50">98%</span>
                                </div>
                                <div className="w-full h-1 bg-white/5 rounded-full mt-1 overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: "98%" }}
                                        className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                                    />
                                </div>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
