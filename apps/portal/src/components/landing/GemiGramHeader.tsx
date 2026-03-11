'use client';

import React from 'react';
import { motion } from 'framer-motion';
import GemigramLogo from '../shared/GemigramLogo';
import { User } from 'lucide-react';

export default function GemiGramHeader({ hideNav = false }: { hideNav?: boolean }) {
    const navItems = hideNav ? [] : [
        { name: 'Discover', href: '#' },
        { name: 'Create', href: '#' },
        { name: 'Hub', href: '#' },
        { name: 'Login', href: '#' }
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 px-10 py-6 flex items-center justify-between bg-black/10 backdrop-blur-xl border-b border-white/5">
            <GemigramLogo size="md" className="!items-start" />

            <nav className="flex items-center gap-12">
                {navItems.map((item) => (
                    <motion.a
                        key={item.name}
                        href={item.href}
                        whileHover={{ y: -2, color: '#22d3ee' }}
                        className="text-sm font-medium text-white/60 tracking-widest uppercase transition-colors"
                    >
                        {item.name}
                    </motion.a>
                ))}

                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-cyan-400 hover:border-cyan-500/50 transition-all shadow-[0_0_15px_rgba(34,211,238,0.1)]"
                >
                    <User className="w-5 h-5" />
                </motion.button>
            </nav>
        </header>
    );
}
