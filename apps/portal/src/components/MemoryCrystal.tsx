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
        return Array.from({ length: 8 }).map((_, i) => ({
            id: i,
            rotateZ: i * 45,
            opacity: 0.15 + (i % 3) * 0.1,
            scale: 0.8 + Math.random() * 0.4,
        }));
    }, []);

    return (
        <motion.div
            layoutId={`crystal-${id}`}
            whileHover={{
                scale: 1.15,
                rotateY: 25,
                rotateX: -10,
                z: 50
            }}
            whileTap={{ scale: 0.9, z: 0 }}
            className="relative w-24 h-32 flex flex-col items-center justify-center cursor-grab active:cursor-grabbing group preserve-3d"
            style={{ perspective: '1200px' }}
        >
            {/* The Refractive Diamond Body */}
            <div className="relative w-16 h-20 flex items-center justify-center preserve-3d">

                {/* Magnetic Aura Pulse */}
                <motion.div
                    animate={{
                        scale: [1, 1.4, 1],
                        opacity: [0.2, 0.5, 0.2]
                    }}
                    transition={{ duration: 4, repeat: Infinity }}
                    className="absolute inset-0 blur-3xl rounded-full -z-10"
                    style={{ backgroundColor: color }}
                />

                {/* Crystal Facets Layering */}
                {facets.map((facet) => (
                    <motion.div
                        key={facet.id}
                        className="absolute inset-0"
                        style={{
                            clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                            rotateZ: facet.rotateZ,
                            scale: facet.scale,
                            opacity: facet.opacity,
                            background: `linear-gradient(135deg, ${color}, transparent 60%)`,
                            border: `1px solid ${color}44`,
                        }}
                        animate={{
                            rotateY: [0, 360],
                            rotateX: [0, 180, 0],
                            opacity: [facet.opacity, facet.opacity * 1.8, facet.opacity],
                        }}
                        transition={{
                            duration: 12 + Math.random() * 8,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    />
                ))}

                {/* Main Glass Prism */}
                <div
                    className="absolute inset-0 border border-white/30 backdrop-blur-[6px] shadow-[inset_0_0_20px_rgba(255,255,255,0.2)]"
                    style={{
                        clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                        background: `radial-gradient(circle at 20% 20%, rgba(255,255,255,0.4) 0%, transparent 80%), 
                                     linear-gradient(to bottom, ${color}22, ${color}66)`
                    }}
                />

                {/* Semantic Icon Core */}
                <Icon
                    size={24}
                    className="relative z-10 text-white group-hover:drop-shadow-[0_0_12px_rgba(255,255,255,0.8)] transition-all duration-300"
                    style={{ filter: `drop-shadow(0 0 10px ${color})` }}
                />
            </div>

            {/* Glowing Tag */}
            <div className="mt-4 px-2 py-0.5 rounded-full bg-black/40 border border-white/5 backdrop-blur-md">
                <span className="text-[9px] font-black font-mono uppercase tracking-[0.2em] text-white/50 group-hover:text-white transition-colors">
                    {label}
                </span>
            </div>

            {/* Floor Projection Shadow */}
            <div
                className="absolute -bottom-4 w-12 h-2 blur-xl opacity-40 rounded-full bg-black"
            />
        </motion.div>
    );
};

export default MemoryCrystal;
