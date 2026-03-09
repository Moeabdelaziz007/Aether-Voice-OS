"use client";

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { LucideIcon, Brain, Code, Search, MessageSquare } from 'lucide-react';

interface MemoryCrystalProps {
    id: string;
    label: string;
    type: 'research' | 'code' | 'chat' | 'other';
    color?: string;
    isDragging?: boolean;
}

const TYPE_ICONS: Record<string, LucideIcon> = {
    research: Search,
    code: Code,
    chat: MessageSquare,
    other: Brain,
};

/**
 * MemoryCrystal — A 3D-styled refractive crystal component.
 * Features:
 * - CSS-3D transforms for "depth"
 * - Glow effects based on semantic matching
 * - Physics-based drag-and-sync feel
 */
export const MemoryCrystal: React.FC<MemoryCrystalProps> = ({
    id,
    label,
    type,
    color = '#00f3ff',
    isDragging
}) => {
    const Icon = TYPE_ICONS[type] || Brain;

    // Generate random facets for the refractive effect
    const facets = useMemo(() => {
        return Array.from({ length: 6 }).map((_, i) => ({
            id: i,
            rotateZ: i * 60,
            opacity: 0.1 + Math.random() * 0.2,
        }));
    }, []);

    return (
        <motion.div
            layoutId={`crystal-${id}`}
            whileHover={{ scale: 1.1, rotateY: 15 }}
            whileTap={{ scale: 0.95 }}
            className="relative w-20 h-24 flex flex-col items-center justify-center cursor-grab active:cursor-grabbing group"
            style={{ perspective: '800px' }}
        >
            {/* Crystal Core */}
            <div className="relative w-12 h-16 flex items-center justify-center">
                {/* Refractive Facets */}
                {facets.map((facet) => (
                    <motion.div
                        key={facet.id}
                        className="absolute inset-0 bg-white"
                        style={{
                            clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                            rotateZ: facet.rotateZ,
                            opacity: facet.opacity,
                            background: `linear-gradient(135deg, ${color}33, transparent 80%)`,
                        }}
                        animate={{
                            rotateY: [0, 360],
                            opacity: [facet.opacity, facet.opacity * 1.5, facet.opacity],
                        }}
                        transition={{
                            duration: 10 + Math.random() * 10,
                            repeat: Infinity,
                            ease: "linear"
                        }}
                    />
                ))}

                {/* Glassy Overlay */}
                <div
                    className="absolute inset-0 border border-white/20 backdrop-blur-[2px]"
                    style={{
                        clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                        background: `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2) 0%, transparent 70%)`
                    }}
                />

                {/* Inner Icon */}
                <Icon
                    size={20}
                    className="relative z-10 text-white/80 group-hover:text-white transition-colors duration-300"
                    style={{ filter: `drop-shadow(0 0 8px ${color})` }}
                />
            </div>

            {/* Label */}
            <span className="mt-2 text-[10px] font-mono uppercase tracking-widest text-white/40 group-hover:text-white/80 transition-colors truncate max-w-full px-1">
                {label}
            </span>

            {/* Ambient Glow */}
            <div
                className="absolute inset-0 -z-10 blur-2xl opacity-20 group-hover:opacity-40 transition-opacity"
                style={{ backgroundColor: color }}
            />
        </motion.div>
    );
};

export default MemoryCrystal;
