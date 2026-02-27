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
                'relative overflow-hidden rounded-3xl carbon-panel neon-border p-6 shadow-2xl transition-all duration-300',
                isExpanded ? 'w-[400px] h-[550px]' : 'w-[320px] h-[120px]',
                className
            )}
            data-tauri-drag-region="true"
        >
            {/* Background Neon Accent */}
            <div className="absolute -top-20 -left-20 h-40 w-40 rounded-full bg-cyan-500/10 blur-3xl" />
            <div className="absolute -bottom-20 -right-20 h-40 w-40 rounded-full bg-cyan-500/10 blur-3xl" />

            {/* Content wrapper to stay above the blurs */}
            <div className="relative z-10 flex h-full flex-col">
                {children}
            </div>
        </motion.div>
    );
}
