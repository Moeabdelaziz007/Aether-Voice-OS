/**
 * MASTER INTEGRATION EXAMPLE
 * ===========================
 * 
 * يوضح هذا الملف كيفية دمج جميع مكونات voice-first معاً
 * في تطبيق متكامل واحد.
 * 
 * Flow:
 * 1. AetherForgeEntrance (حيث يتحدث المستخدم)
 * 2. SoulBlueprintStep (اختيار الذكريات)
 * 3. SkillsDialStep (اختيار المهارات)
 * 4. IdentityCustomizationStep (تخصيص الشخصية)
 * 5. CommunicationSanctum (التفاعل مع العامل)
 */

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useCallback } from 'react';

// Import all components
import AetherForgeEntrance from '@/components/forge/AetherForgeEntrance';
import SoulBlueprintStep from '@/components/forge/steps/SoulBlueprintStep';
import SkillsDialStep from '@/components/forge/steps/SkillsDialStep';
import IdentityCustomizationStep from '@/components/forge/steps/IdentityCustomizationStep';
import CommunicationSanctum from '@/components/agent/CommunicationSanctum';

// Import hooks and services
import { useAetherGateway } from '@/hooks/useAetherGateway';
import { useAetherStore } from '@/store/useAetherStore';
import { createAgentFromVoice } from '@/services/agentService';

type FlowStep = 'forge' | 'blueprint' | 'skills' | 'identity' | 'sanctum';

interface AgentConfiguration {
  name: string;
  persona: string;
  skills: string[];
  memories: string[];
  auraLevel: number;
  toneResonance: number;
  personalityTraits: string[];
}

export default function MasterVoiceFlowIntegration() {
  // ───── State Management ─────
  const [currentStep, setCurrentStep] = useState<FlowStep>('forge');
  const [agentConfig, setAgentConfig] = useState<Partial<AgentConfiguration>>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [createdAgent, setCreatedAgent] = useState<any>(null);

  // ───── Hooks ─────
  const gateway = useAetherGateway();
  const store = useAetherStore();

  // ───── Handler: Intent Captured in Forge ─────
  const handleIntentCaptured = useCallback(
    async (intent: string) => {
      console.log('[Master] Intent captured:', intent);

      setIsProcessing(true);

      try {
        // Call agent creation service
        // This would integrate with Gemini function calling
        const agent = await createAgentFromVoice(
          store.userId || 'anonymous',
          intent
        );

        // Update config with extracted data
        setAgentConfig((prev) => ({
          ...prev,
          name: agent.name,
          persona: agent.persona,
          skills: agent.skills || [],
          memories: agent.memories || [],
        }));

        // Add to platform feed
        store.pushToFeed({
          agentId: agent.id,
          agentName: agent.name,
          action: `Voice creation initiated: "${intent}"`,
          type: 'forge_start',
          auraLevel: 5,
        });

        // Advance to next step
        setCurrentStep('blueprint');
      } catch (error) {
        console.error('[Master] Error processing intent:', error);
        store.addError({
          code: 'INTENT_PROCESSING_FAILED',
          message: 'Failed to process your voice input',
          severity: 'high',
          retryable: true,
        });
      } finally {
        setIsProcessing(false);
      }
    },
    [store]
  );

  // ───── Handler: Soul Blueprint Complete ─────
  const handleBlueprintComplete = useCallback(
    (activatedMemories: string[]) => {
      console.log('[Master] Blueprint complete:', activatedMemories);

      setAgentConfig((prev) => ({
        ...prev,
        memories: activatedMemories,
      }));

      store.addSystemLog(
        'PERSONA',
        `Soul blueprinting activated ${activatedMemories.length} memory crystals`
      );

      setCurrentStep('skills');
    },
    [store]
  );

  // ───── Handler: Skills Selection Complete ─────
  const handleSkillsComplete = useCallback(
    (selectedSkills: string[]) => {
      console.log('[Master] Skills selected:', selectedSkills);

      setAgentConfig((prev) => ({
        ...prev,
        skills: selectedSkills,
      }));

      store.addSystemLog(
        'SKILLS',
        `Agent autonomy configured with ${selectedSkills.length} skills`
      );

      setCurrentStep('identity');
    },
    [store]
  );

  // ───── Handler: Identity Customization Complete ─────
  const handleIdentityComplete = useCallback(
    (
      auraLevel: number,
      toneResonance: number,
      personalityTraits: string[]
    ) => {
      console.log('[Master] Identity customized:', {
        auraLevel,
        toneResonance,
        personalityTraits,
      });

      setAgentConfig((prev) => ({
        ...prev,
        auraLevel,
        toneResonance,
        personalityTraits,
      }));

      store.addSystemLog(
        'PERSONA',
        `Identity resonance set to aura=${auraLevel} tone=${toneResonance}`
      );

      // Launch into Communication Sanctum
      setCurrentStep('sanctum');
    },
    [store]
  );

  // ───── Handler: Forge Complete ─────
  const handleForgeComplete = useCallback(() => {
    console.log('[Master] Forge complete, moving to communication');
    setCurrentStep('sanctum');
  }, []);

  // ───── Handler: Voice Input in Sanctum ─────
  const handleSanctumVoiceInput = useCallback(
    (text: string) => {
      console.log('[Master] Sanctum voice input:', text);

      // This would normally route to agent command handler
      store.addSystemLog('VOICE', `User: "${text}"`);

      // Could trigger widget generation, tool calls, etc.
    },
    [store]
  );

  // ───── Render: Voice-First UI Flow ─────
  return (
    <div className="relative w-full min-h-screen bg-black overflow-hidden">
      {/* Loading overlay during processing */}
      {isProcessing && (
        <motion.div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="text-center">
            <motion.div
              className="w-16 h-16 rounded-full border-2 border-cyan-500/30 border-t-cyan-500 mx-auto mb-4"
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            />
            <p className="text-gray-400 text-sm">Processing your voice input...</p>
          </div>
        </motion.div>
      )}

      {/* Main Flow - AnimatePresence for smooth transitions */}
      <AnimatePresence mode="wait">
        {/* Step 1: Aether Forge Entrance */}
        {currentStep === 'forge' && (
          <motion.div
            key="forge"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0"
          >
            <AetherForgeEntrance
              onIntentCaptured={handleIntentCaptured}
              onForgeComplete={handleForgeComplete}
            />
          </motion.div>
        )}

        {/* Step 2: Soul Blueprint */}
        {currentStep === 'blueprint' && (
          <motion.div
            key="blueprint"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="absolute inset-0"
          >
            <SoulBlueprintStep
              agentName={agentConfig.name || 'Agent'}
              agentPersona={agentConfig.persona || ''}
              onCrystalActivate={(crystalId) => {
                console.log('[Master] Crystal activated:', crystalId);
              }}
              isLoading={false}
            />

            {/* Navigation - Skip to next step (voice or button) */}
            <motion.button
              onClick={() => handleBlueprintComplete(agentConfig.memories || [])}
              className="absolute bottom-8 right-8 z-50 px-8 py-3 rounded-xl bg-cyan-500/20 border border-cyan-500/50 text-cyan-300 text-sm font-semibold hover:bg-cyan-500/30 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Continue to Skills ↓
            </motion.button>
          </motion.div>
        )}

        {/* Step 3: Skills Dial */}
        {currentStep === 'skills' && (
          <motion.div
            key="skills"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="absolute inset-0"
          >
            <SkillsDialStep
              selectedSkills={agentConfig.skills || []}
              onSkillToggle={(skillId) => {
                console.log('[Master] Skill toggled:', skillId);
              }}
              isListening={true}
            />

            {/* Navigation Button */}
            <motion.button
              onClick={() => handleSkillsComplete(agentConfig.skills || [])}
              className="absolute bottom-8 right-8 z-50 px-8 py-3 rounded-xl bg-purple-500/20 border border-purple-500/50 text-purple-300 text-sm font-semibold hover:bg-purple-500/30 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Continue to Identity ↓
            </motion.button>
          </motion.div>
        )}

        {/* Step 4: Identity Customization */}
        {currentStep === 'identity' && (
          <motion.div
            key="identity"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="absolute inset-0"
          >
            <IdentityCustomizationStep
              auraLevel={agentConfig.auraLevel || 50}
              onAuraChange={(level) => {
                console.log('[Master] Aura changed:', level);
              }}
              toneResonance={agentConfig.toneResonance || 50}
              onToneChange={(tone) => {
                console.log('[Master] Tone changed:', tone);
              }}
              personalityTraits={agentConfig.personalityTraits || []}
              onTraitToggle={(trait) => {
                console.log('[Master] Trait toggled:', trait);
              }}
            />

            {/* Navigation Button */}
            <motion.button
              onClick={() =>
                handleIdentityComplete(
                  agentConfig.auraLevel || 50,
                  agentConfig.toneResonance || 50,
                  agentConfig.personalityTraits || []
                )
              }
              className="absolute bottom-8 right-8 z-50 px-8 py-3 rounded-xl bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 text-sm font-semibold hover:bg-emerald-500/30 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Enter Sanctum ↓
            </motion.button>
          </motion.div>
        )}

        {/* Step 5: Communication Sanctum */}
        {currentStep === 'sanctum' && (
          <motion.div
            key="sanctum"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            className="absolute inset-0"
          >
            <CommunicationSanctum
              agentName={agentConfig.name || 'Agent'}
              agentAura={
                ((agentConfig.auraLevel || 50) > 66
                  ? 'emerald'
                  : (agentConfig.auraLevel || 50) > 33
                  ? 'purple'
                  : 'cyan') as any
              }
              emotionalState="listening"
              onVoiceInput={handleSanctumVoiceInput}
            />

            {/* Back button (minimal) */}
            <motion.button
              onClick={() => setCurrentStep('forge')}
              className="absolute top-8 left-8 z-50 px-6 py-2 rounded-lg bg-white/5 border border-white/20 text-white/60 text-sm hover:bg-white/10 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              ← Back
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Debug Info (remove in production) */}
      {process.env.NEXT_PUBLIC_DEV_MODE && (
        <motion.div
          className="fixed bottom-4 left-4 z-40 p-4 rounded-lg bg-black/80 border border-white/20 text-white/60 text-xs font-mono max-w-xs"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <p>📍 Current Step: {currentStep}</p>
          <p>🤖 Agent: {agentConfig.name || 'Not set'}</p>
          <p>⚡ Aura: {agentConfig.auraLevel || '-'}%</p>
          <p>🎵 Tone: {agentConfig.toneResonance || '-'}%</p>
          <p>🛠️ Skills: {agentConfig.skills?.length || 0}</p>
        </motion.div>
      )}
    </div>
  );
}

/**
 * USAGE:
 * ------
 * 
 * في app/voice-flow/page.tsx:
 * 
 * import MasterVoiceFlowIntegration from '@/path/to/this/file';
 * 
 * export default function VoiceFlowPage() {
 *   return <MasterVoiceFlowIntegration />;
 * }
 * 
 * ثم زيارة: http://localhost:3000/voice-flow
 */
