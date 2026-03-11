
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Zap } from 'lucide-react';

interface ForgeConfirmationProps {
    state: string;
    onConfirm: () => void;
}

export default function ForgeConfirmation({ state, onConfirm }: ForgeConfirmationProps) {
    const isVisible = (state === 'REFINING_WITH_VISION' || state === 'AWAITING_CONFIRMATION' || state === 'COMMITTING_TO_FIRESTORE');

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex items-center justify-center bg-black/95 backdrop-blur-xl z-30 p-12 text-center"
                >
                    <motion.div 
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        className="space-y-10"
                    >
                        <div className="w-24 h-24 bg-cyan-500/10 border-2 border-cyan-500/40 rounded-full flex items-center justify-center mx-auto shadow-[0_0_80px_rgba(34,211,238,0.3)]">
                            {state === 'COMMITTING_TO_FIRESTORE' || state === 'REFINING_WITH_VISION' ? 
                                <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" /> : 
                                <motion.div animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
                                    <Zap className="w-10 h-10 text-cyan-400 fill-cyan-400" />
                                </motion.div>
                            }
                        </div>
                        <div className="space-y-4">
                            <h4 className="text-3xl font-black uppercase tracking-tighter text-white">
                                {state === 'REFINING_WITH_VISION' ? 'Grounding_Context' : 'Commit_Required'}
                            </h4>
                            <p className="text-white/40 text-[10px] uppercase tracking-[0.4em] font-mono leading-relaxed">
                                {state === 'REFINING_WITH_VISION' ? 
                                    'Synchronizing personality quarks with visual environment...' :
                                    'Neural_Weight_Stabilization_Complete. Say "Confirm" to proceed.'
                                }
                            </p>
                        </div>
                        {state === 'AWAITING_CONFIRMATION' && (
                            <motion.button
                                whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(34,211,238,0.6)' }}
                                whileTap={{ scale: 0.95 }}
                                onClick={onConfirm}
                                className="px-16 py-6 bg-cyan-500 text-black rounded-[4px] text-xs font-black uppercase tracking-[0.3em] shadow-2xl transition-all"
                            >
                                INITIATE_FORGE_SEQUENCE
                            </motion.button>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
