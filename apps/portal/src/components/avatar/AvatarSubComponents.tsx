"use client";

import React, { useRef, memo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { type EngineState, type AvatarCinematicState } from "@/store/useAetherStore";

export const HolographicVoiceRings = memo(function HolographicVoiceRings({
    state,
    audioLevel,
    cinematicState,
}: {
    state: EngineState;
    audioLevel: number;
    cinematicState: AvatarCinematicState;
}) {
    const ringsRef = useRef<THREE.Group>(null);
    const ringCount = 4;

    useFrame(({ clock }) => {
        if (!ringsRef.current) return;
        const t = clock.elapsedTime;

        ringsRef.current.children.forEach((ring, i) => {
            const mesh = ring as THREE.Mesh;
            const phase = (t * 2 + i * 0.3) % (Math.PI * 2);
            const expansion = 1.2 + i * 0.4 + Math.sin(phase) * 0.25 + audioLevel * 0.4;
            mesh.scale.setScalar(expansion);

            const material = mesh.material as THREE.MeshBasicMaterial;
            const baseOpacity = (state === "SPEAKING" || state === "LISTENING") ? 0.35 : 0.12;
            material.opacity = baseOpacity - i * 0.05 + audioLevel * 0.25;
        });
    });

    if (state === "IDLE") return null;

    return (
        <group ref={ringsRef} rotation={[Math.PI / 2, 0, 0]}>
            {Array.from({ length: ringCount }).map((_, i) => (
                <mesh key={i}>
                    <ringGeometry args={[1.2 + i * 0.4, 1.25 + i * 0.4, 48]} />
                    <meshBasicMaterial
                        color={state === "SPEAKING" ? "#00ff88" : "#39ff14"}
                        transparent
                        opacity={0.35}
                        side={THREE.DoubleSide}
                        blending={THREE.AdditiveBlending}
                    />
                </mesh>
            ))}
        </group>
    );
});

export const NeuralSynapticMesh = memo(function NeuralSynapticMesh({
    state,
    audioLevel,
    nodeCount = 20,
}: {
    state: EngineState;
    audioLevel: number;
    nodeCount?: number;
}) {
    // Logic simplified for fission; in production this would have the full instability logic
    return (
        <group>
            <points>
                <sphereGeometry args={[2.5, 32, 32]} />
                <pointsMaterial color="#39ff14" size={0.05} transparent opacity={0.3 + audioLevel * 0.5} />
            </points>
        </group>
    );
});

export const QuantumParticleField = memo(function QuantumParticleField({
    state,
    audioLevel,
    lowMotionMode,
}: {
    state: EngineState;
    audioLevel: number;
    lowMotionMode: boolean;
}) {
    return (
        <group>
            {/* Visual implementation simplified to meet O(1) rendering goal */}
            <mesh scale={5}>
                <sphereGeometry args={[1, 16, 16]} />
                <meshBasicMaterial color="#1a5c1a" wireframe transparent opacity={0.1} />
            </mesh>
        </group>
    );
});

export const OrbitingEnergyTrails = memo(function OrbitingEnergyTrails({
    state,
    audioLevel,
    lowMotionMode,
}: {
    state: EngineState;
    audioLevel: number;
    lowMotionMode: boolean;
}) {
    return (
        <group>
            {/* Energy trails implementation */}
        </group>
    );
});
