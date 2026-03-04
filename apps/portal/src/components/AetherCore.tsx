"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial, Float } from "@react-three/drei";
import * as THREE from "three";
import { useAetherStore, type EngineState } from "@/store/useAetherStore";

/**
 * AetherCore — The 3D Neural Heart of AetherOS.
 * 
 * A living, generative WebGL orb that shifts form and color based on AI state.
 * Replaces the 2D Canvas orb with a high-fidelity 3D entity.
 */

const STATE_CONFIG: Record<EngineState, { color: string; speed: number; factor: number }> = {
    IDLE: { color: "#1a1a3e", speed: 2, factor: 0.6 },
    LISTENING: { color: "#3b4bff", speed: 4, factor: 1.2 },
    THINKING: { color: "#f59e0b", speed: 8, factor: 2.0 },
    SPEAKING: { color: "#06b6d4", speed: 5, factor: 1.5 },
    INTERRUPTING: { color: "#ef4444", speed: 10, factor: 3.0 },
};

function ScanningRing({ radius, speed, axis }: { radius: number; speed: number; axis: "x" | "y" | "z" }) {
    const ringRef = useRef<THREE.Mesh>(null);
    useFrame((state) => {
        if (!ringRef.current) return;
        const t = state.clock.getElapsedTime();
        if (axis === "x") ringRef.current.rotation.x = t * speed;
        if (axis === "y") ringRef.current.rotation.y = t * speed;
        if (axis === "z") ringRef.current.rotation.z = t * speed;
    });

    return (
        <mesh ref={ringRef}>
            <torusGeometry args={[radius, 0.005, 16, 100]} />
            <meshStandardMaterial
                color="rgba(var(--accent-r),var(--accent-g),var(--accent-b),0.5)"
                emissive="rgba(var(--accent-r),var(--accent-g),var(--accent-b),1)"
                emissiveIntensity={2}
                transparent
                opacity={0.3}
            />
        </mesh>
    );
}

function NeuralOrb() {
    const meshRef = useRef<THREE.Mesh>(null);
    const materialRef = useRef<any>(null);

    const engineState = useAetherStore((s) => s.engineState);
    const micLevel = useAetherStore((s) => s.micLevel);
    const speakerLevel = useAetherStore((s) => s.speakerLevel);

    const config = useMemo(() => STATE_CONFIG[engineState] || STATE_CONFIG.IDLE, [engineState]);

    useFrame((state) => {
        if (!materialRef.current) return;

        const t = state.clock.getElapsedTime();
        const energy = engineState === "SPEAKING" ? speakerLevel : micLevel;

        // Dynamic distortion based on audio energy
        materialRef.current.distort = THREE.MathUtils.lerp(
            materialRef.current.distort,
            config.factor + energy * 2,
            0.1
        );

        materialRef.current.speed = THREE.MathUtils.lerp(
            materialRef.current.speed,
            config.speed + energy * 5,
            0.1
        );

        // Subtle rotation
        if (meshRef.current) {
            meshRef.current.rotation.y = t * 0.2;
            meshRef.current.rotation.z = t * 0.1;
        }
    });

    return (
        <group>
            <Sphere args={[1, 64, 64]} ref={meshRef}>
                <MeshDistortMaterial
                    ref={materialRef}
                    color={config.color}
                    attach="material"
                    distort={config.factor}
                    speed={config.speed}
                    roughness={0.2}
                    metalness={0.8}
                    emissive={config.color}
                    emissiveIntensity={0.5}
                />
            </Sphere>

            {/* Scanning Rings */}
            <ScanningRing radius={1.4} speed={0.5} axis="y" />
            <ScanningRing radius={1.6} speed={-0.3} axis="x" />
            <ScanningRing radius={1.8} speed={0.8} axis="z" />
        </group>
    );
}

export default function AetherCore() {
    return (
        <div className="w-full h-full flex items-center justify-center relative">
            <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <pointLight position={[-10, -10, -10]} color="#4a3080" intensity={0.5} />

                <Float speed={2} rotationIntensity={1} floatIntensity={1}>
                    <NeuralOrb />
                </Float>
            </Canvas>

            {/* Background radial glow that syncs with the orb */}
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <div className="w-64 h-64 rounded-full blur-[100px] opacity-20 bg-[var(--accent)]" />
            </div>
        </div>
    );
}
