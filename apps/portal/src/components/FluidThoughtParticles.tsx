"use client";
/**
 * FluidThoughtParticles — Immersive 3D Conversation Experience
 * 
 * Transforms text messages into floating physical particles in 3D space.
 * Each word becomes a particle with mass, velocity, and emotional charge.
 * 
 * Features:
 * - Physics-based particle simulation
 * - Emotional color coding (Quantum Neural Topology palette)
 * - Voice-synced pulsation
 * - Spatial audio positioning
 * - Liquid morphing effects
 */

import React, { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { useAetherStore } from "@/store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════

interface ThoughtParticle {
  id: string;
  content: string;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  mass: number;
  charge: number; // Emotional charge: -1 (negative) to +1 (positive)
  decay: number;
  birthTime: number;
  lifespan: number;
  type: "user" | "agent";
  importance: number; // 0-1 scale
}

interface ParticleSystemProps {
  particles: ThoughtParticle[];
  audioLevel: number;
  engineState: string;
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Neural Topology Color Palette
// ═══════════════════════════════════════════════════════════════════

const QUANTUM_PALETTE = {
  neonGreen: {
    primary: new THREE.Color("#39ff14"),
    glow: new THREE.Color("#00ff41"),
    dim: new THREE.Color("#1a5c1a"),
  },
  carbonFiber: {
    dark: new THREE.Color("#0a0a0a"),
    medium: new THREE.Color("#1a1a1a"),
    light: new THREE.Color("#2d2d2d"),
  },
  mediumGray: {
    primary: new THREE.Color("#6b7280"),
    glow: new THREE.Color("#9ca3af"),
    dim: new THREE.Color("#4b5563"),
  },
  accent: {
    cyan: new THREE.Color("#00f3ff"),
    purple: new THREE.Color("#bc13fe"),
    amber: new THREE.Color("#f59e0b"),
  },
};

// ═══════════════════════════════════════════════════════════════════
// Particle Mesh Component
// ═══════════════════════════════════════════════════════════════════

function ParticleMesh({ particle, audioLevel, time }: { 
  particle: ThoughtParticle; 
  audioLevel: number;
  time: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  // Calculate color based on emotional charge and type
  const color = useMemo(() => {
    if (particle.type === "agent") {
      // Agent particles: Neon green with emotional modulation
      const baseColor = QUANTUM_PALETTE.neonGreen.primary.clone();
      if (particle.charge > 0.5) {
        baseColor.lerp(QUANTUM_PALETTE.accent.cyan, particle.charge - 0.5);
      } else if (particle.charge < -0.5) {
        baseColor.lerp(QUANTUM_PALETTE.accent.amber, Math.abs(particle.charge) - 0.5);
      }
      return baseColor;
    } else {
      // User particles: Medium gray with subtle green tint
      const baseColor = QUANTUM_PALETTE.mediumGray.primary.clone();
      baseColor.lerp(QUANTUM_PALETTE.neonGreen.dim, 0.3);
      return baseColor;
    }
  }, [particle.type, particle.charge]);

  // Custom shader for glowing effect
  const shaderData = useMemo(() => ({
    uniforms: {
      uTime: { value: 0 },
      uAudioLevel: { value: 0 },
      uColor: { value: color },
      uGlowIntensity: { value: particle.importance * 2 },
      uCharge: { value: particle.charge },
    },
    vertexShader: `
      uniform float uTime;
      uniform float uAudioLevel;
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        
        // Pulsate with audio
        float pulse = 1.0 + uAudioLevel * 0.3 * sin(uTime * 10.0);
        vec3 newPosition = position * pulse;
        
        gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uColor;
      uniform float uGlowIntensity;
      uniform float uCharge;
      uniform float uTime;
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        // Fresnel effect for glow
        vec3 viewDirection = normalize(cameraPosition - vPosition);
        float fresnel = pow(1.0 - dot(viewDirection, vNormal), 3.0);
        
        // Quantum entanglement visual effect
        float quantum = sin(uTime * 5.0 + vPosition.x * 10.0) * 0.5 + 0.5;
        
        vec3 glowColor = uColor * (1.0 + uGlowIntensity * fresnel * quantum);
        
        // Add charge-based color modulation
        if (uCharge > 0.0) {
          glowColor += vec3(0.0, uCharge * 0.5, uCharge * 0.3);
        } else {
          glowColor += vec3(-uCharge * 0.3, 0.0, 0.0);
        }
        
        gl_FragColor = vec4(glowColor, 0.9);
      }
    `,
  }), [color, particle.importance, particle.charge]);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
      materialRef.current.uniforms.uAudioLevel.value = audioLevel;
    }
    
    if (meshRef.current) {
      // Apply velocity
      meshRef.current.position.add(particle.velocity.clone().multiplyScalar(0.016));
      
      // Gentle rotation
      meshRef.current.rotation.x += 0.01;
      meshRef.current.rotation.y += 0.005;
      
      // Apply decay
      const age = time - particle.birthTime;
      const lifeRatio = age / particle.lifespan;
      meshRef.current.scale.setScalar(1.0 - lifeRatio * 0.5);
    }
  });

  // Calculate size based on importance and content length
  const size = Math.max(0.5, particle.importance * 2);

  return (
    <mesh ref={meshRef} position={particle.position}>
      <sphereGeometry args={[size, 32, 32]} />
      <shaderMaterial
        ref={materialRef}
        {...shaderData}
        transparent
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </mesh>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Neural Connection Lines
// ═══════════════════════════════════════════════════════════════════

function NeuralConnections({ particles }: { particles: ThoughtParticle[] }) {
  const linesRef = useRef<THREE.LineSegments>(null);

  const geometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];

    // Create connections between nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];
        const distance = p1.position.distanceTo(p2.position);

        if (distance < 5.0) {
          positions.push(
            p1.position.x, p1.position.y, p1.position.z,
            p2.position.x, p2.position.y, p2.position.z
          );

          // Color based on connection strength
          const strength = 1.0 - distance / 5.0;
          const color = QUANTUM_PALETTE.neonGreen.glow.clone();
          color.multiplyScalar(strength);

          colors.push(color.r, color.g, color.b);
          colors.push(color.r, color.g, color.b);
        }
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    return geo;
  }, [particles]);

  return (
    <lineSegments ref={linesRef} geometry={geometry}>
      <lineBasicMaterial vertexColors blending={THREE.AdditiveBlending} transparent opacity={0.3} />
    </lineSegments>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Field Background
// ═══════════════════════════════════════════════════════════════════

function QuantumField({ audioLevel }: { audioLevel: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const shaderData = useMemo(() => ({
    uniforms: {
      uTime: { value: 0 },
      uAudioLevel: { value: 0 },
      uColor1: { value: QUANTUM_PALETTE.carbonFiber.dark },
      uColor2: { value: QUANTUM_PALETTE.neonGreen.dim },
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform float uAudioLevel;
      uniform vec3 uColor1;
      uniform vec3 uColor2;
      varying vec2 vUv;
      
      // Simplex noise function
      vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }
      
      float snoise(vec2 v) {
        const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                           -0.577350269189626, 0.024390243902439);
        vec2 i  = floor(v + dot(v, C.yy));
        vec2 x0 = v -   i + dot(i, C.xx);
        vec2 i1;
        i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod289(i);
        vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0))
          + i.x + vec3(0.0, i1.x, 1.0));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
          dot(x12.zw,x12.zw)), 0.0);
        m = m*m;
        m = m*m;
        vec3 x = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
      }
      
      void main() {
        vec2 uv = vUv;
        
        // Animated quantum field
        float noise1 = snoise(uv * 3.0 + uTime * 0.2);
        float noise2 = snoise(uv * 5.0 - uTime * 0.15);
        float noise3 = snoise(uv * 8.0 + uTime * 0.1);
        
        // Audio reactivity
        float audioBoost = uAudioLevel * 0.3;
        
        // Combine noises
        float finalNoise = (noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2) * (1.0 + audioBoost);
        
        // Color mixing
        vec3 color = mix(uColor1, uColor2, finalNoise * 0.5 + 0.5);
        
        // Add quantum entanglement lines
        float lines = sin(uv.x * 50.0 + uTime) * sin(uv.y * 50.0 + uTime);
        lines = smoothstep(0.98, 1.0, lines);
        color += vec3(0.0, 1.0, 0.2) * lines * 0.3 * (1.0 + audioBoost);
        
        gl_FragColor = vec4(color, 0.15);
      }
    `,
  }), []);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
      materialRef.current.uniforms.uAudioLevel.value = audioLevel;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -10]}>
      <planeGeometry args={[30, 20]} />
      <shaderMaterial
        ref={materialRef}
        {...shaderData}
        transparent
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </mesh>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Particle System
// ═══════════════════════════════════════════════════════════════════

function ParticleSystem({ particles, audioLevel, engineState }: ParticleSystemProps) {
  const groupRef = useRef<THREE.Group>(null);
  const { camera } = useThree();

  useFrame((state) => {
    if (groupRef.current) {
      // Gentle rotation of the entire system
      groupRef.current.rotation.y += 0.001;
      
      // React to speaking state
      if (engineState === "SPEAKING") {
        groupRef.current.scale.setScalar(1.0 + audioLevel * 0.1);
      } else {
        groupRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
      }
    }
  });

  // Filter out dead particles
  const { clock } = useThree();
  const aliveParticles = particles.filter(
    (p) => clock.elapsedTime - p.birthTime < p.lifespan
  );

  return (
    <group ref={groupRef}>
      <QuantumField audioLevel={audioLevel} />
      <NeuralConnections particles={aliveParticles} />
      {aliveParticles.map((particle) => (
        <ParticleMesh
          key={particle.id}
          particle={particle}
          audioLevel={audioLevel}
          time={0}
        />
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Component Export
// ═══════════════════════════════════════════════════════════════════

export default function FluidThoughtParticles() {
  const transcript = useAetherStore((s) => s.transcript);
  const micLevel = useAetherStore((s) => s.micLevel);
  const speakerLevel = useAetherStore((s) => s.speakerLevel);
  const engineState = useAetherStore((s) => s.engineState);

  const [particles, setParticles] = React.useState<ThoughtParticle[]>([]);
  const particlesRef = useRef<ThoughtParticle[]>([]);

  // Convert transcript messages to particles
  useEffect(() => {
    if (transcript.length === 0) return;

    const latestMessage = transcript[transcript.length - 1];
    const words = latestMessage.content.split(/\s+/);

    // Create particles for each word
    const newParticles: ThoughtParticle[] = words.map((word, index) => {
      // Calculate emotional charge based on word sentiment
      const charge = calculateEmotionalCharge(word);
      const importance = calculateImportance(word);

      return {
        id: `${latestMessage.id}-${index}`,
        content: word,
        position: new THREE.Vector3(
          (Math.random() - 0.5) * 8,
          (Math.random() - 0.5) * 4,
          (Math.random() - 0.5) * 4
        ),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.02,
          0.01 + Math.random() * 0.02,
          (Math.random() - 0.5) * 0.02
        ),
        mass: importance * 2,
        charge,
        decay: 0.001,
        birthTime: performance.now() / 1000,
        lifespan: 15 + importance * 10,
        type: latestMessage.role,
        importance,
      };
    });

    particlesRef.current = [...particlesRef.current, ...newParticles];
    setParticles(particlesRef.current);
  }, [transcript]);

  // Cleanup old particles
  useEffect(() => {
    const interval = setInterval(() => {
      const now = performance.now() / 1000;
      particlesRef.current = particlesRef.current.filter(
        (p) => now - p.birthTime < p.lifespan
      );
      setParticles(particlesRef.current);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Determine audio level based on engine state
  const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

  return (
    <div className="fixed inset-0 z-5 pointer-events-none">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 60 }}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: "high-performance"
        }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={0.5} color="#39ff14" />
        <pointLight position={[-10, -10, -10]} intensity={0.3} color="#00ff41" />
        
        <ParticleSystem
          particles={particles}
          audioLevel={audioLevel}
          engineState={engineState}
        />
      </Canvas>
    </div>
  );
}

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
  // Technical terms get higher importance
  const techTerms = ["function", "class", "api", "database", "server", "client", "async", "await", "error", "debug"];
  const lowerWord = word.toLowerCase();
  
  if (techTerms.includes(lowerWord)) return 1.0;
  if (word.length > 6) return 0.8;
  if (word.length > 4) return 0.6;
  return 0.4;
}
