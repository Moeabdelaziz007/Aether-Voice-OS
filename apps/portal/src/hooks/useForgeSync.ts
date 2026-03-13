import { useEffect } from 'react';
import { useForgeStore } from '@/store/useForgeStore';
import { db } from '@/lib/firebase';
import { doc, onSnapshot } from 'firebase/firestore';

export function useForgeSync(uid?: string) {
  const updateDNA = useForgeStore((state) => state.updateDNA);
  const setStep = useForgeStore((state) => state.setStep);
  const activeStep = useForgeStore((state) => state.activeStep);

  useEffect(() => {
    if (!uid || !db) return;

    // Listen to real-time DNA mutations from the Forge Engine
    const unsubscribe = onSnapshot(doc(db, 'user_dna', uid), (snapshot) => {
      if (snapshot.exists()) {
        const data = snapshot.data();
        
        // If there's an active synthesis running in the cloud
        if (data.activeForge) {
          updateDNA({
            name: data.activeForge.name || '',
            role: data.activeForge.role || '',
            tone: data.activeForge.tone || '',
            skills: data.activeForge.expertise ? Object.keys(data.activeForge.expertise) : [],
          });

          // Transition to Review once registry load completes
          if (data.activeForge.status === 'registry_load' && activeStep === 'synthesizing') {
            setStep('review');
          }
        }
      }
    }, (error) => {
      console.error("🔥 Forge Sync Error:", error);
    });

    return () => unsubscribe();
  }, [uid, updateDNA, setStep, activeStep]);
}
