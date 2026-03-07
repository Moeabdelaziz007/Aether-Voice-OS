"use client";

import React, { useRef, useMemo, useEffect, useState, memo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Sparkles, Trail } from "@react-three/drei";
import { useAetherStore, type TranscriptMessage } from "@/store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════
// Types & Constants
// ═══════════════════════════════════════════════════════════════════

interface ThoughtParticle {
  id: string;
  content: string;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  mass: number;
  charge: number;
  birthTime: number;
  lifespan: number;
  type: "user" | "agent";
  importance: number;
  color: THREE.Color;
}

const QUANTUM_PALETTE = {
  neonGreen: {
    primary: new THREE.Color("#39ff14"),
    glow: new THREE.Color("#00ff41"),
    electric: new THREE.Color("#00ff88"),
    dim: new THREE.Color("#1a5c1a"),
  },
  carbonFiber: {
    dark: new THREE.Color("#0a0a0a"),
    medium: new THREE.Color("#1a1a1a"),
  },
  mediumGray: {
    primary: new THREE.Color("#6b7280"),
    glow: new THREE.Color("#9ca3af"),
    dim: new THREE.Color("#4b5563"),
  },
  accent: {
    amber: new THREE.Color("#f59e0b"),
    gold: new THREE.Color("#ffd700"),
  },
};

// ═══════════════════════════════════════════════════════════════════
// Shaders
// ═══════════════════════════════════════════════════════════════════

const quantumFieldVertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const quantumFieldFragmentShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  uniform vec3 uColor1;
  uniform vec3 uColor2;
  varying vec2 vUv;
  
  void main() {
    vec2 uv = vUv;
    float noise1 = sin(uv.x * 8.0 + uTime * 0.15) * sin(uv.y * 8.0 + uTime * 0.1);
    float audioBoost = uAudioLevel * 0.3;
    vec3 color = mix(uColor1, uColor2, noise1 * 0.5 + 0.5);
    float gridX = smoothstep(0.98, 1.0, sin(uv.x * 40.0 + uTime * 0.3));
    float gridY = smoothstep(0.98, 1.0, sin(uv.y * 40.0 + uTime * 0.2));
    color += vec3(0.2, 1.0, 0.4) * max(gridX, gridY) * 0.1 * (1.0 + audioBoost);
    float vignette = 1.0 - length(uv - 0.5) * 0.7;
    color *= vignette;
    gl_FragColor = vec4(color, 0.08);
  }
`;

// ═══════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════

function calculateEmotionalCharge(word: string): number {
  const positiveWords = ["great", "awesome", "excellent", "love", "perfect", "amazing", "good", "happy", "thanks", "yes"];
  const negativeWords = ["bad", "error", "fail", "wrong", "problem", "issue", "bug", "crash", "no", "sorry"];
  const lowerWord = word.toLowerCase();
  if (positiveWords.includes(lowerWord)) return 0.8;
  if (negativeWords.includes(lowerWord)) return -0.8;
  return 0;
}

function calculateImportance(word: string): number {
  const techTerms = ["function", "class", "api", "database", "server", "async", "error", "debug", "component"];
  const lowerWord = word.toLowerCase();
  if (techTerms.includes(lowerWord)) return 1.0;
  if (word.length > 8) return 0.8;
  if (word.length > 5) return 0.6;
  return 0.4;
}

// ═══════════════════════════════════════════════════════════════════
// Sub-Components (Optimized)
// ═══════════════════════════════════════════════════════════════════

const QuantumFieldBackground = memo(function QuantumFieldBackground() {
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uAudioLevel: { value: 0 },
    uColor1: { value: QUANTUM_PALETTE.carbonFiber.dark },
    uColor2: { value: QUANTUM_PALETTE.neonGreen.dim },
  }), []);

  useFrame((state) => {
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
      materialRef.current.uniforms.uAudioLevel.value = audioLevel;
    }
  });

  return (
    <mesh position={[0, 0, -12]}>
      <planeGeometry args={[35, 25]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={quantumFieldVertexShader}
        fragmentShader={quantumFieldFragmentShader}
        uniforms={uniforms}
        transparent
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </mesh>
  );
});

const AmbientSparkles = memo(function AmbientSparkles() {
  const [sparkleState, setSparkleState] = useState({ audioLevel: 0, engineState: "IDLE" });

  useFrame(() => {
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    setSparkleState({
      audioLevel: engineState === "SPEAKING" ? speakerLevel : micLevel,
      engineState
    });
  });

  const sparkleColor = useMemo(() => {
    switch (sparkleState.engineState) {
      case "SPEAKING": return "#00ff88";
      case "LISTENING": return "#39ff14";
      case "THINKING": return "#ffd700";
      default: return "#1a5c1a";
    }
  }, [sparkleState.engineState]);

  return (
    <Sparkles
      count={100}
      scale={18}
      size={1.5 + sparkleState.audioLevel * 3}
      speed={0.25 + sparkleState.audioLevel * 0.8}
      opacity={0.35 + sparkleState.audioLevel * 0.25}
      color={sparkleColor}
    />
  );
});

const NeuralFilaments = memo(function NeuralFilaments({ particles }: { particles: ThoughtParticle[] }) {
  const filamentsRef = useRef<THREE.LineSegments>(null);

  const geometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];
        const distance = p1.position.distanceTo(p2.position);
        if (distance < 3.5) {
          positions.push(p1.position.x, p1.position.y, p1.position.z, p2.position.x, p2.position.y, p2.position.z);
          const strength = 1.0 - distance / 3.5;
          const mixedColor = p1.color.clone().lerp(p2.color, 0.5).multiplyScalar(strength);
          colors.push(mixedColor.r, mixedColor.g, mixedColor.b, mixedColor.r, mixedColor.g, mixedColor.b);
        }
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    return geo;
  }, [particles]);

  useFrame(() => {
    if (filamentsRef.current) {
      const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
      const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;
      (filamentsRef.current.material as THREE.LineBasicMaterial).opacity = 0.2 + audioLevel * 0.15;
    }
  });

  return (
    <lineSegments ref={filamentsRef} geometry={geometry}>
      <lineBasicMaterial vertexColors blending={THREE.AdditiveBlending} transparent />
    </lineSegments>
  );
});

// ═══════════════════════════════════════════════════════════════════
// Main Optimized Scene Content
// ═══════════════════════════════════════════════════════════════════

export const ParticleSceneContent = memo(function ParticleSceneContent() {
  const groupRef = useRef<THREE.Group>(null);
  const instancedRef = useRef<THREE.InstancedMesh>(null);

  const { clock } = useThree();
  const [particles, setParticles] = useState<ThoughtParticle[]>([]);
  const particlesRef = useRef<ThoughtParticle[]>([]);
  const transcript = useAetherStore(state => state.transcript);

  useEffect(() => {
    if (transcript.length === 0) return;
    const latestMessage = transcript[transcript.length - 1];
    const words = latestMessage.content.split(/\s+/).filter(w => w.length > 0).slice(0, 15);

    const newParticles: ThoughtParticle[] = words.map((word, index) => {
      const charge = calculateEmotionalCharge(word);
      const importance = calculateImportance(word);
      const color = latestMessage.role === "agent"
        ? QUANTUM_PALETTE.neonGreen.primary.clone()
        : QUANTUM_PALETTE.mediumGray.primary.clone();

      if (latestMessage.role === "agent") {
        if (charge > 0.3) color.lerp(QUANTUM_PALETTE.neonGreen.electric, charge);
        else if (charge < -0.3) color.lerp(QUANTUM_PALETTE.accent.amber, Math.abs(charge));
      } else {
        color.lerp(QUANTUM_PALETTE.neonGreen.dim, 0.2);
      }

      return {
        id: `${latestMessage.id}-${index}`,
        content: word,
        position: new THREE.Vector3((Math.random() - 0.5) * 8, (Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4),
        velocity: new THREE.Vector3((Math.random() - 0.5) * 0.012, 0.006 + Math.random() * 0.012, (Math.random() - 0.5) * 0.012),
        mass: importance * 2,
        charge,
        birthTime: performance.now() / 1000,
        lifespan: 15 + importance * 10,
        type: latestMessage.role as "user" | "agent",
        importance,
        color,
      };
    });

    particlesRef.current = [...particlesRef.current.slice(-30), ...newParticles];
    setParticles([...particlesRef.current]);
  }, [transcript]);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = performance.now() / 1000;
      const initialCount = particlesRef.current.length;
      particlesRef.current = particlesRef.current.filter(p => now - p.birthTime < p.lifespan);
      if (particlesRef.current.length !== initialCount) setParticles([...particlesRef.current]);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useFrame((state) => {
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;
    const t = state.clock.elapsedTime;

    if (groupRef.current) {
      groupRef.current.rotation.y += 0.0008;
      if (engineState === "SPEAKING") groupRef.current.scale.setScalar(1.0 + audioLevel * 0.06);
      else groupRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.04);
    }

    if (instancedRef.current) {
      const mesh = instancedRef.current;
      const matrix = new THREE.Matrix4();
      const pos = new THREE.Vector3();
      const scale = new THREE.Vector3();
      const quat = new THREE.Quaternion();

      particles.forEach((p, i) => {
        const age = t - (p.birthTime - (performance.now() / 1000 - t));
        const lifeRatio = Math.min(age / p.lifespan, 1);
        p.position.addScaledVector(p.velocity, 1.0);
        const pulse = 1.0 + audioLevel * 0.3 * Math.sin(t * 8.0 + i);
        const s = Math.max(0, (1.0 - lifeRatio * 0.5) * pulse * p.importance * 1.5);
        pos.copy(p.position);
        scale.set(s, s, s);
        matrix.compose(pos, quat, scale);
        mesh.setMatrixAt(i, matrix);
        mesh.setColorAt(i, p.color);
      });

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      mesh.count = particles.length;
    }
  });

  return (
    <group ref={groupRef} position={[0, 0, -2]}>
      <QuantumFieldBackground />
      {particles.length > 0 && <NeuralFilaments particles={particles} />}
      <AmbientSparkles />
      <instancedMesh ref={instancedRef} args={[undefined, undefined, 50]}>
        <icosahedronGeometry args={[1, 1]} />
        <meshStandardMaterial transparent opacity={0.8} emissiveIntensity={2} metalness={0.9} roughness={0.1} />
      </instancedMesh>
    </group>
  );
});
