'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface WidgetContainerProps {
    children: ReactNode;
    className?: string;
    isExpanded?: boolean;
}

export function WidgetContainer({ children, className, isExpanded = false }: WidgetContainerProps) {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 20 }}
            className={cn(
                'relative overflow-hidden rounded-[2.5rem] carbon-panel shadow-[0_32px_64px_rgba(0,0,0,0.6)]',
                'transition-all duration-700 ease-out border-white/5',
                isExpanded ? 'w-[440px] h-[640px] p-8' : 'w-[360px] h-[160px] p-6',
                isExpanded ? 'neon-glow-cyan' : 'hover:border-white/10',
                className
            )}
            data-tauri-drag-region="true"
        >
            {/* Draggable Surface Glow */}
            <div
                className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none"
                data-tauri-drag-region="true"
            />

            {/* Industrial Background Accents */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/10 blur-[100px] -mr-24 -mt-24 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/10 blur-[100px] -ml-24 -mb-24 pointer-events-none" />

            {/* Inner Glass Reflection */}
            <div className="absolute inset-0 glass-reflection pointer-events-none opacity-50" />

            {/* Content wrapper to stay above the blurs */}
            <div className="relative z-10 flex h-full flex-col">
                {children}
            </div>

            {/* Subtle Diagnostic Light (Bottom) */}
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-8 h-1 rounded-full bg-white/5" />
        </motion.div>
    );
}
