
import React from 'react';
import { motion } from 'framer-motion';
import VoiceOrb from '../shared/VoiceOrb';
import QuantumNeuralAvatar from '../../QuantumNeuralAvatar';

interface ForgeStatusProps {
    state: string;
    micLevel: number;
    isListening: boolean;
    onInitiate: () => void;
}

export default function ForgeStatus({ state, micLevel, isListening, onInitiate }: ForgeStatusProps) {
    return (
        <div className="flex flex-col items-center justify-center space-y-16">
            <motion.div 
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 1.5 }}
                className="relative"
            >
                <div className="absolute inset-0 bg-cyan-500/10 blur-[120px] rounded-full animate-pulse" />
                <VoiceOrb
                    size="lg"
                    onTap={() => state === 'IDLE' ? onInitiate() : null}
                />

                <motion.div 
                    animate={{ 
                        scale: 1 + (micLevel / 100) * 0.5,
                        opacity: isListening ? 0.3 : 0
                    }}
                    className="absolute inset-[-32px] rounded-full border border-cyan-500/30 pointer-events-none"
                />
            </motion.div>

            <div className="text-center space-y-6 max-w-sm">
                <motion.h2 
                    key={state}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-4xl font-black tracking-tighter uppercase text-white/90 italic"
                >
                    {state === 'IDLE' ? 'Neural_Genesis' :
                        state === 'LISTENING_SPEC' ? 'Soul_Ingestion' :
                            state === 'REFINING_WITH_VISION' ? 'Visual_Grounding' :
                                state === 'AWAITING_CONFIRMATION' ? 'Validation_Lock' :
                                    'Synthesizing...'}
                </motion.h2>

                <p className="text-white/40 text-[10px] uppercase tracking-[0.4em] leading-relaxed font-mono">
                    {state === 'IDLE' ? '// INITIATE_V_GENESIS_PROTOCOL' :
                        state === 'LISTENING_SPEC' ? '// DECODING_AUDIO_VECTOR_STREAM' :
                            state === 'REFINING_WITH_VISION' ? '// CROSS_REFERENCING_VISUAL_LOBE' :
                                state === 'AWAITING_CONFIRMATION' ? '// BLUEPRINT_STABILIZED_PENDING_COMMIT' :
                                    '// COMMITTING_NEURAL_WEIGHTS_TO_GRID'}
                </p>
            </div>

            <div className="flex items-center gap-6 text-[9px] font-black uppercase tracking-widest text-white/10 italic">
                {['IDLE', 'DECODE', 'BLUEPRINT', 'COMMIT'].map((s, i) => {
                    const isActive = (i === 0 && state === 'IDLE') ||
                                 (i === 1 && state === 'LISTENING_SPEC') ||
                                 (i === 2 && state === 'AWAITING_CONFIRMATION') ||
                                 (i === 3 && state === 'COMMITTING_TO_FIRESTORE');
                    return (
                        <React.Fragment key={s}>
                            <span className={isActive ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]' : ''}>{s}</span>
                            {i < 3 && <div className={`h-px w-4 ${isActive ? 'bg-cyan-400' : 'bg-white/10'}`} />}
                        </React.Fragment>
                    );
                })}
            </div>
        </div>
    );
}
