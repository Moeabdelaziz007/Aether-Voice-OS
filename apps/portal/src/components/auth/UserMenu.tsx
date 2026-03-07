'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LogOut, Settings, User, ChevronDown } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface UserMenuProps {
    onOpenSettings?: () => void;
}

/**
 * UserMenu — Avatar dropdown with user info, settings link, and logout.
 */
export default function UserMenu({ onOpenSettings }: UserMenuProps) {
    const { user, logout } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    // Close on outside click
    useEffect(() => {
        const handleClick = (e: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    if (!user) return null;

    return (
        <div ref={menuRef} className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
            >
                {user.photoURL ? (
                    <img
                        src={user.photoURL}
                        alt={user.displayName || 'User'}
                        className="w-7 h-7 rounded-full border border-white/10"
                    />
                ) : (
                    <div className="w-7 h-7 rounded-full bg-cyan-500/20 flex items-center justify-center">
                        <User className="w-3.5 h-3.5 text-cyan-400" />
                    </div>
                )}
                <ChevronDown className={`w-3 h-3 text-white/40 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -8, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -8, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
                        className="absolute right-0 top-full mt-2 w-56 ultra-glass rounded-xl border border-white/10 overflow-hidden z-50"
                    >
                        {/* User info */}
                        <div className="px-4 py-3 border-b border-white/5">
                            <p className="text-sm text-white/90 font-medium truncate">
                                {user.displayName || 'Operator'}
                            </p>
                            <p className="text-xs text-white/30 font-mono truncate mt-0.5">
                                {user.email}
                            </p>
                        </div>

                        {/* Menu items */}
                        <div className="py-1">
                            <button
                                onClick={() => {
                                    setIsOpen(false);
                                    onOpenSettings?.();
                                }}
                                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                            >
                                <Settings className="w-4 h-4" />
                                Settings
                            </button>
                            <button
                                onClick={() => {
                                    setIsOpen(false);
                                    logout();
                                }}
                                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400/60 hover:text-red-400 hover:bg-red-500/5 transition-colors"
                            >
                                <LogOut className="w-4 h-4" />
                                Sign Out
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
