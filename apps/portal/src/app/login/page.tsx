"use client";

import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { LogIn, ShieldCheck, Zap } from "lucide-react";

export default function LoginPage() {
    const { user, loginWithGoogle, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (user && !loading) {
            router.push("/");
        }
    }, [user, loading, router]);

    const handleLogin = async () => {
        try {
            await loginWithGoogle();
        } catch (error) {
            console.error("Auth error:", error);
        }
    };

    if (loading) return null;

    return (
        <div className="relative min-h-screen w-full flex items-center justify-center bg-[#050505] overflow-hidden">
            {/* Background Neural Grid */}
            <div className="absolute inset-0 opacity-20 pointer-events-none"
                style={{ backgroundImage: 'radial-gradient(#1a1a1a 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

            {/* Ambient Gloom */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/10 blur-[120px] rounded-full" />
            <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-cyan-500/5 blur-[100px] rounded-full" />

            {/* Login Card */}
            <motion.div
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="relative z-10 w-full max-w-md p-8 rounded-2xl border border-white/5 bg-white/[0.02] backdrop-blur-xl shadow-2xl"
            >
                {/* Scanner Line Animation */}
                <motion.div
                    animate={{ top: ["0%", "100%", "0%"] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent z-20 pointer-events-none"
                />

                <div className="text-center mb-10">
                    <motion.div
                        initial={{ rotate: -10, scale: 0.8 }}
                        animate={{ rotate: 0, scale: 1 }}
                        transition={{ duration: 1, type: "spring" }}
                        className="inline-flex p-4 rounded-full bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-white/10 mb-6"
                    >
                        <Zap className="w-12 h-12 text-cyan-400 fill-cyan-400/20" />
                    </motion.div>

                    <h1 className="text-4xl font-black tracking-tighter text-white mb-2">
                        AETHER <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 uppercase">OS</span>
                    </h1>
                    <p className="text-zinc-500 font-medium text-sm tracking-widest uppercase">
                        Neural Interface Terminal v2.1
                    </p>
                </div>

                <div className="space-y-4">
                    <button
                        onClick={handleLogin}
                        className="group relative w-full py-4 bg-white text-black font-bold rounded-lg overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98]"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-500 opacity-0 group-hover:opacity-10 transition-opacity" />
                        <span className="relative flex items-center justify-center gap-2">
                            <LogIn className="w-5 h-5" />
                            SYNC IDENTITY WITH GOOGLE
                        </span>
                    </button>

                    <div className="flex items-center justify-center gap-8 text-[10px] text-zinc-600 font-mono tracking-tighter uppercase mt-8 border-t border-white/5 pt-6">
                        <div className="flex items-center gap-1.5">
                            <ShieldCheck className="w-3 h-3 text-cyan-500/50" />
                            GTP HANDSHAKE ACTIVE
                        </div>
                        <div className="flex items-center gap-1.5 text-zinc-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500/40 animate-pulse" />
                            SYSTEMS NOMINAL
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Bottom Credits */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-center">
                <p className="text-[10px] text-zinc-500 font-mono tracking-[0.3em] uppercase opacity-50">
                    Designed by Aether Architect • 10x Neural Sync
                </p>
            </div>
        </div>
    );
}
