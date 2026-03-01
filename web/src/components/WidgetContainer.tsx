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
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            className={cn(
                'relative overflow-hidden rounded-2xl carbon-panel p-6 shadow-2xl transition-all duration-500',
                isExpanded ? 'w-[420px] h-[600px]' : 'w-[340px] h-[140px]',
                isExpanded ? 'neon-glow-cyan' : 'border-white/5',
                className
            )}
            data-tauri-drag-region="true"
        >
            {/* Industrial Background Accents */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 blur-[80px] -mr-16 -mt-16 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-purple-500/5 blur-[80px] -ml-16 -mb-16 pointer-events-none" />

            {/* Top Border Glow Line */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            {/* Content wrapper to stay above the blurs */}
            <div className="relative z-10 flex h-full flex-col">
                {children}
            </div>
        </motion.div>
    );
}
