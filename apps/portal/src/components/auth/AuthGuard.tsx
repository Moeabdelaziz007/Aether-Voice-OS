"use client";

import { useAuth } from "@/hooks/useAuth";
import { ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import LoginPage from "./LoginPage";

interface AuthGuardProps {
    children: ReactNode;
}

/**
 * AuthGuard — Wraps the app to require Firebase authentication.
 * Shows LoginPage when not authenticated, children when authenticated.
 * No routing required — renders inline for static export compatibility.
 */
export default function AuthGuard({ children }: AuthGuardProps) {
    const { user, loading } = useAuth();

    return (
        <AnimatePresence mode="wait">
            {loading ? (
                <motion.div
                    key="loader"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-[#050505]"
                >
                    <div className="relative group">
                        <motion.div
                            animate={{
                                scale: [1, 1.2, 1],
                                rotate: [0, 180, 360],
                                borderRadius: ["20%", "50%", "20%"]
                            }}
                            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                            className="w-16 h-16 border-2 border-cyan-500/20 group-hover:border-cyan-500/50"
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-2 h-2 bg-cyan-500 rounded-full animate-ping" />
                        </div>
                    </div>
                </motion.div>
            ) : !user ? (
                <motion.div
                    key="login"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="w-full h-full"
                >
                    <LoginPage />
                </motion.div>
            ) : (
                <motion.div
                    key="content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="w-full h-full"
                >
                    {children}
                </motion.div>
            )}
        </AnimatePresence>
    );
}
