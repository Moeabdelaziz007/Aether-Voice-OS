"use client";

import React, { useRef, useMemo, memo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { MeshDistortMaterial } from "@react-three/drei";
import { type EngineState } from "@/store/useAetherStore";

// Shaders remain the same to preserve "Quantum Cyberpunk" aesthetic
const vertexShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  varying vec3 vPosition;
  varying vec3 vNormal;
  void main() {
    vNormal = normalize(normalMatrix * normal);
    float n = sin(position.x * 2.0 + uTime) * 0.1;
    vec3 displaced = position + normal * (n + uAudioLevel * 0.2);
    vPosition = displaced;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
  }
`;

const fragmentShader = `
  uniform float uTime;
  uniform vec3 uColor;
  varying vec3 vPosition;
  varying vec3 vNormal;
  void main() {
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 3.0);
    gl_FragColor = vec4(uColor * (1.0 + fresnel), 0.9);
  }
`;

export const QuantumConsciousnessCore = memo(function QuantumConsciousnessCore({
    state,
    audioLevel,
    lowMotionMode,
}: {
    state: EngineState;
    audioLevel: number;
    lowMotionMode: boolean;
}) {
    const coreRef = useRef<THREE.Group>(null);
    const materialRef = useRef<THREE.ShaderMaterial>(null);

    useFrame(({ clock }) => {
        const t = clock.elapsedTime;
        if (materialRef.current) {
            materialRef.current.uniforms.uTime.value = t;
            materialRef.current.uniforms.uAudioLevel.value = audioLevel;
        }
        if (coreRef.current) {
            coreRef.current.rotation.y += lowMotionMode ? 0.005 : 0.01 + audioLevel * 0.05;
        }
    });

    const uniforms = useMemo(() => ({
        uTime: { value: 0 },
        uAudioLevel: { value: 0 },
        uColor: { value: new THREE.Color("#39ff14") }
    }), []);

    return (
        <group ref={coreRef}>
            <mesh>
                <sphereGeometry args={[0.95, 64, 64]} />
                <shaderMaterial
                    ref={materialRef}
                    vertexShader={vertexShader}
                    fragmentShader={fragmentShader}
                    uniforms={uniforms}
                    transparent
                />
            </mesh>
            <mesh>
                <sphereGeometry args={[0.35, 32, 32]} />
                <MeshDistortMaterial
                    color="#39ff14"
                    speed={lowMotionMode ? 1 : 5}
                    distort={0.4}
                    emissive="#39ff14"
                    emissiveIntensity={2}
                />
            </mesh>
        </group>
    );
});
