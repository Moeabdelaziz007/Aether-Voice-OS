"use client";

import React, { useRef, useMemo, memo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Float } from "@react-three/drei";
import { type EngineState, type AvatarCinematicState } from "@/store/useAetherStore";

// Internal Sub-Components (Ideally these would be in separate files too, 
// but for the sake of 'Fission' we keep the Controller clean)
import { QuantumConsciousnessCore } from "./QuantumConsciousnessCore";
import { HolographicVoiceRings } from "./HolographicVoiceRings";
import { NeuralSynapticMesh } from "./NeuralSynapticMesh";
import { QuantumParticleField } from "./QuantumParticleField";
import { OrbitingEnergyTrails } from "./OrbitingEnergyTrails";

interface AvatarSceneProps {
  mouthOpenness: number;
  state: EngineState;
  cinematicState: AvatarCinematicState;
  variant: string;
  showConnections: boolean;
  lowMotionMode: boolean;
  gazeTarget: [number, number, number];
}

/**
 * AvatarSceneContent — The Declarative Controller
 * 
 * Logic extraction complete. This component now acts as an orchestrator,
 * passing down computed visemes and state to specialized child components.
 * Complexity: < 30
 */
export const AvatarSceneContent = memo(function AvatarSceneContent({
  mouthOpenness,
  state,
  cinematicState,
  variant,
  showConnections,
  lowMotionMode,
  gazeTarget,
}: AvatarSceneProps) {
  const sceneRootRef = useRef<THREE.Group>(null);
  const targetVector = useMemo(() => new THREE.Vector3(...gazeTarget), [gazeTarget]);

  useFrame(() => {
    if (!sceneRootRef.current) return;

    // Smooth Gaze Tracking
    const lookAtMatrix = new THREE.Matrix4();
    lookAtMatrix.lookAt(sceneRootRef.current.position, targetVector, new THREE.Vector3(0, 1, 0));
    const targetQuaternion = new THREE.Quaternion().setFromRotationMatrix(lookAtMatrix);
    sceneRootRef.current.quaternion.slerp(targetQuaternion, lowMotionMode ? 0.03 : 0.08);
  });

  return (
    <group ref={sceneRootRef}>
      <Float
        speed={lowMotionMode ? 0.35 : 1.2}
        rotationIntensity={lowMotionMode ? 0.08 : 0.25}
        floatIntensity={lowMotionMode ? 0.1 : 0.35}
      >
        <QuantumConsciousnessCore
          state={state}
          audioLevel={mouthOpenness}
          lowMotionMode={lowMotionMode}
        />
      </Float>

      <HolographicVoiceRings
        state={state}
        audioLevel={mouthOpenness}
        cinematicState={cinematicState}
      />

      {showConnections && (
        <NeuralSynapticMesh
          state={state}
          audioLevel={mouthOpenness}
          nodeCount={variant === "immersive" ? 35 : 20}
        />
      )}

      <QuantumParticleField
        state={state}
        audioLevel={mouthOpenness}
        lowMotionMode={lowMotionMode}
      />

      {variant !== "minimal" && (
        <OrbitingEnergyTrails
          state={state}
          audioLevel={mouthOpenness}
          lowMotionMode={lowMotionMode}
        />
      )}
    </group>
  );
});
