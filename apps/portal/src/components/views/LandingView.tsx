
import React from 'react';
import { motion } from 'framer-motion';
import BackgroundEngine from '../utility/BackgroundEngine';
import NeuralBackground from '../shared/NeuralBackground';
import ParticleField from '../shared/ParticleField';
import GemiGramHeader from '../landing/GemiGramHeader';
import GemiGramSplash from '../landing/GemiGramSplash';
import NeuralIdentityGrid from '../landing/NeuralIdentityGrid';
import VoiceSynthesisDashboard from '../landing/VoiceSynthesisDashboard';
import GemiGramFooter from '../landing/GemiGramFooter';

interface LandingViewProps {
    onEnterPortal: (panel?: any) => void;
}

export default function LandingView({ onEnterPortal }: LandingViewProps) {
    return (
        <motion.div
            key="landing-view"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 1.05, filter: 'blur(20px)' }}
            transition={{ duration: 0.8 }}
            className="relative min-h-screen bg-[#050505] text-white selection:bg-cyan-500/30 overflow-x-hidden"
        >
            <BackgroundEngine />
            <NeuralBackground />
            <ParticleField count={40} />
            <div className="carbon-fiber-overlay fixed inset-0 opacity-20 pointer-events-none" />

            <GemiGramHeader />

            <main className="relative z-10">
                <GemiGramSplash
                    onConnect={() => onEnterPortal('dashboard')}
                    onCreate={() => onEnterPortal('hub')}
                />

                <NeuralIdentityGrid />

                <div className="py-20">
                    <VoiceSynthesisDashboard />
                </div>
            </main>

            <GemiGramFooter />
        </motion.div>
    );
}
