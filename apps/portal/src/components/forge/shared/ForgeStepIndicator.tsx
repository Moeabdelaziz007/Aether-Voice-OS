"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2 } from 'lucide-react';
import type { ForgeStep } from '@/store/useForgeStore';

export interface StepDef {
    id: ForgeStep;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
}

interface Props {
    steps: StepDef[];
    activeStep: ForgeStep;
    onStepClick?: (step: ForgeStep) => void;
}

export default function ForgeStepIndicator({ steps, activeStep, onStepClick }: Props) {
    const activeIdx = steps.findIndex((s) => s.id === activeStep);

    return (
        <div className="flex items-center justify-between px-10 py-6 border-b border-white/[0.04]">
            <div className="flex items-center gap-2">
                {steps.map((s, i) => {
                    const isActive = activeStep === s.id;
                    const isCompleted = activeIdx > i;
                    const Icon = s.icon;

                    return (
                        <React.Fragment key={s.id}>
                            <motion.button
                                onClick={() => onStepClick?.(s.id)}
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                                className={`relative w-9 h-9 rounded-full flex items-center justify-center transition-all ${
                                    isActive
                                        ? 'bg-cyan-500 text-black shadow-[0_0_20px_rgba(34,211,238,0.5)]'
                                        : isCompleted
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-white/5 text-white/20 hover:bg-white/10'
                                }`}
                            >
                                {isCompleted ? (
                                    <CheckCircle2 className="w-5 h-5" />
                                ) : (
                                    <Icon className="w-4 h-4" />
                                )}
                                {isActive && (
                                    <motion.div
                                        layoutId="step-ring"
                                        className="absolute -inset-1 rounded-full border-2 border-cyan-400/50"
                                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                    />
                                )}
                            </motion.button>
                            {i < steps.length - 1 && (
                                <div className={`w-6 h-[2px] rounded-full transition-colors ${
                                    isCompleted ? 'bg-green-500/40' : 'bg-white/5'
                                }`} />
                            )}
                        </React.Fragment>
                    );
                })}
            </div>
            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-cyan-400/60">
                Phase {activeIdx + 1} of {steps.length}
            </div>
        </div>
    );
}
