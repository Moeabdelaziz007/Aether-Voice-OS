"use client";
/**
 * FluidThoughtParticlesScene — Extracted Scene Content
 * 
 * Contains all 3D thought particle elements WITHOUT the Canvas wrapper.
 * Used by UnifiedScene for consolidated rendering.
 */

import React, { useRef, useMemo, useEffect, useState, memo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Sparkles, Trail } from "@react-three/drei";
import type { TranscriptMessage } from "@/store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════
// Types
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

// ═══════════════════════════════════════════════════════════════════
// Quantum Neural Color Palette
// ═══════════════════════════════════════════════════════════════════

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
// Optimized Shaders
// ═══════════════════════════════════════════════════════════════════

const particleVertexShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  varying vec3 vPosition;
  varying vec3 vNormal;
  
  void main() {
    vNormal = normalize(normalMatrix * normal);
    float pulse = 1.0 + uAudioLevel * 0.3 * sin(uTime * 8.0);
    vec3 displaced = position * pulse;
    vPosition = displaced;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
  }
`;

const particleFragmentShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  uniform vec3 uColor;
  uniform float uCharge;
  uniform float uImportance;
  
  varying vec3 vPosition;
  varying vec3 vNormal;
  
  void main() {
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 2.5);
    
    vec3 baseColor = uColor;
    if (uCharge > 0.3) {
      baseColor = mix(baseColor, vec3(0.0, 1.0, 0.5), uCharge * 0.3);
    }
    
    vec3 glowColor = baseColor * (1.0 + fresnel * 1.5 * uImportance);
    glowColor += vec3(0.2, 1.0, 0.4) * uAudioLevel * fresnel * 0.5;
    
    gl_FragColor = vec4(glowColor, 0.8 + fresnel * 0.2);
  }
`;

// ═══════════════════════════════════════════════════════════════════
// Thought Particle Mesh (Optimized)
// ═══════════════════════════════════════════════════════════════════

const ThoughtParticleMesh = memo(function ThoughtParticleMesh({ 
  particle, 
  audioLevel, 
  time 
}: { 
  particle: ThoughtParticle; 
  audioLevel: number;
  time: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uAudioLevel: { value: 0 },
    uColor: { value: particle.color },
    uCharge: { value: particle.charge },
    uImportance: { value: particle.importance },
  }), [particle.color, particle.charge, particle.importance]);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
      materialRef.current.uniforms.uAudioLevel.value = audioLevel;
    }
    
    if (meshRef.current) {
      const dampedVelocity = particle.velocity.clone().multiplyScalar(0.014);
      meshRef.current.position.add(dampedVelocity);
      meshRef.current.rotation.x += 0.006 + audioLevel * 0.008;
      meshRef.current.rotation.y += 0.004 + audioLevel * 0.006;
      
      const age = time - particle.birthTime;
      const lifeRatio = Math.min(age / particle.lifespan, 1);
      meshRef.current.scale.setScalar(1.0 - lifeRatio * 0.5);
    }
  });

  const size = Math.max(0.35, particle.importance * 1.2);

  return (
    <Trail
      width={0.06 + audioLevel * 0.04}
      length={4}
      color={particle.color}
      attenuation={(width) => width * width}
    >
      <mesh ref={meshRef} position={particle.position}>
        <icosahedronGeometry args={[size, 1]} />
        <shaderMaterial
          ref={materialRef}
          vertexShader={particleVertexShader}
          fragmentShader={particleFragmentShader}
          uniforms={uniforms}
          transparent
          side={THREE.DoubleSide}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
    </Trail>
  );
});

// ═══════════════════════════════════════════════════════════════════
// Neural Filaments (Simplified)
// ═══════════════════════════════════════════════════════════════════

const NeuralFilaments = memo(function NeuralFilaments({ 
  particles, 
  audioLevel 
}: { 
  particles: ThoughtParticle[];
  audioLevel: number;
}) {
  const geometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];
        const distance = p1.position.distanceTo(p2.position);

        if (distance < 3.5) {
          positions.push(
            p1.position.x, p1.position.y, p1.position.z,
            p2.position.x, p2.position.y, p2.position.z
          );

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

  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial 
        vertexColors 
        blending={THREE.AdditiveBlending} 
        transparent 
        opacity={0.2 + audioLevel * 0.15}
      />
    </lineSegments>
  );
});

// ═══════════════════════════════════════════════════════════════════
// Quantum Field Background (Optimized shader)
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
    
    // Simplified noise pattern
    float noise1 = sin(uv.x * 8.0 + uTime * 0.15) * sin(uv.y * 8.0 + uTime * 0.1);
    float audioBoost = uAudioLevel * 0.3;
    
    vec3 color = mix(uColor1, uColor2, noise1 * 0.5 + 0.5);
    
    // Subtle grid
    float gridX = smoothstep(0.98, 1.0, sin(uv.x * 40.0 + uTime * 0.3));
    float gridY = smoothstep(0.98, 1.0, sin(uv.y * 40.0 + uTime * 0.2));
    color += vec3(0.2, 1.0, 0.4) * max(gridX, gridY) * 0.1 * (1.0 + audioBoost);
    
    // Vignette
    float vignette = 1.0 - length(uv - 0.5) * 0.7;
    color *= vignette;
    
    gl_FragColor = vec4(color, 0.08);
  }
`;

const QuantumFieldBackground = memo(function QuantumFieldBackground({ audioLevel }: { audioLevel: number }) {
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uAudioLevel: { value: 0 },
    uColor1: { value: QUANTUM_PALETTE.carbonFiber.dark },
    uColor2: { value: QUANTUM_PALETTE.neonGreen.dim },
  }), []);

  useFrame((state) => {
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

// ═══════════════════════════════════════════════════════════════════
// Ambient Sparkles
// ═══════════════════════════════════════════════════════════════════

const AmbientSparkles = memo(function AmbientSparkles({ 
  audioLevel, 
  engineState 
}: { 
  audioLevel: number; 
  engineState: string;
}) {
  const sparkleColor = useMemo(() => {
    switch (engineState) {
      case "SPEAKING": return "#00ff88";
      case "LISTENING": return "#39ff14";
      case "THINKING": return "#ffd700";
      default: return "#1a5c1a";
    }
  }, [engineState]);

  return (
    <Sparkles
      count={100}  // Reduced from 150
      scale={18}
      size={1.5 + audioLevel * 3}
      speed={0.25 + audioLevel * 0.8}
      opacity={0.35 + audioLevel * 0.25}
      color={sparkleColor}
    />
  );
});

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
// Main Particle Scene Content Export
// ═══════════════════════════════════════════════════════════════════

interface ParticleSceneProps {
  audioLevel: number;
  engineState: string;
  transcript: TranscriptMessage[];
}

export const ParticleSceneContent = memo(function ParticleSceneContent({ 
  audioLevel, 
  engineState,
  transcript,
}: ParticleSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const { clock } = useThree();
  const [particles, setParticles] = useState<ThoughtParticle[]>([]);
  const particlesRef = useRef<ThoughtParticle[]>([]);

  // Convert transcript messages to particles (limit to prevent overload)
  useEffect(() => {
    if (transcript.length === 0) return;

    const latestMessage = transcript[transcript.length - 1];
    const words = latestMessage.content.split(/\s+/).filter(w => w.length > 0).slice(0, 15); // Limit words

    const newParticles: ThoughtParticle[] = words.map((word, index) => {
      const charge = calculateEmotionalCharge(word);
      const importance = calculateImportance(word);
      
      let color: THREE.Color;
      if (latestMessage.role === "agent") {
        color = QUANTUM_PALETTE.neonGreen.primary.clone();
        if (charge > 0.3) color.lerp(QUANTUM_PALETTE.neonGreen.electric, charge);
        else if (charge < -0.3) color.lerp(QUANTUM_PALETTE.accent.amber, Math.abs(charge));
      } else {
        color = QUANTUM_PALETTE.mediumGray.primary.clone();
        color.lerp(QUANTUM_PALETTE.neonGreen.dim, 0.2);
      }

      return {
        id: `${latestMessage.id}-${index}`,
        content: word,
        position: new THREE.Vector3(
          (Math.random() - 0.5) * 8,
          (Math.random() - 0.5) * 4,
          (Math.random() - 0.5) * 4
        ),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.012,
          0.006 + Math.random() * 0.012,
          (Math.random() - 0.5) * 0.012
        ),
        mass: importance * 2,
        charge,
        birthTime: performance.now() / 1000,
        lifespan: 15 + importance * 10,
        type: latestMessage.role,
        importance,
        color,
      };
    });

    // Limit total particles
    particlesRef.current = [...particlesRef.current.slice(-30), ...newParticles];
    setParticles([...particlesRef.current]);
  }, [transcript]);

  // Cleanup old particles
  useEffect(() => {
    const interval = setInterval(() => {
      const now = performance.now() / 1000;
      particlesRef.current = particlesRef.current.filter(p => now - p.birthTime < p.lifespan);
      setParticles([...particlesRef.current]);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.0008;
      if (engineState === "SPEAKING") {
        groupRef.current.scale.setScalar(1.0 + audioLevel * 0.06);
      } else {
        groupRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.04);
      }
    }
  });

  // Filter alive particles
  const aliveParticles = particles.filter(p => clock.elapsedTime - p.birthTime < p.lifespan);

  return (
    <group ref={groupRef} position={[0, 0, -2]}>
      <QuantumFieldBackground audioLevel={audioLevel} />
      {aliveParticles.length > 0 && <NeuralFilaments particles={aliveParticles} audioLevel={audioLevel} />}
      <AmbientSparkles audioLevel={audioLevel} engineState={engineState} />
      
      {aliveParticles.slice(0, 20).map((particle) => (  // Limit rendered particles
        <ThoughtParticleMesh
          key={particle.id}
          particle={particle}
          audioLevel={audioLevel}
          time={clock.elapsedTime}
        />
      ))}
    </group>
  );
});
