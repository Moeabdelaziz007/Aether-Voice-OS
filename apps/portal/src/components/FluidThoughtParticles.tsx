"use client";
/**
 * FluidThoughtParticles — Advanced 3D Conversation Visualization
 * 
 * Transforms conversation into an immersive particle field with:
 * - Physics-based fluid dynamics
 * - Emotional charge visualization
 * - Voice-synchronized quantum waves
 * - Neural topology connections
 * - Holographic text rendering
 * 
 * Color Palette: Quantum Neural Topology
 * - Neon Green (#39ff14) — Agent thoughts
 * - Medium Gray (#6b7280) — User thoughts
 * - Gold (#ffd700) — Important concepts
 */

import React, { useRef, useMemo, useEffect, useCallback, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Sparkles, Trail, Float, Text, Billboard } from "@react-three/drei";
import { EffectComposer, Bloom, ChromaticAberration } from "@react-three/postprocessing";
import { BlendFunction, KernelSize } from "postprocessing";
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
  charge: number;
  decay: number;
  birthTime: number;
  lifespan: number;
  type: "user" | "agent";
  importance: number;
  color: THREE.Color;
}

interface ParticleSystemProps {
  particles: ThoughtParticle[];
  audioLevel: number;
  engineState: string;
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
    gold: new THREE.Color("#ffd700"),
    crimson: new THREE.Color("#ff1744"),
  },
};

// ═══════════════════════════════════════════════════════════════════
// Custom Shaders
// ═══════════════════════════════════════════════════════════════════

const particleVertexShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  varying vec3 vPosition;
  varying vec3 vNormal;
  varying float vNoise;
  
  // Simplex noise
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
  
  float snoise(vec3 v) {
    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute(permute(permute(
      i.z + vec4(0.0, i1.z, i2.z, 1.0))
      + i.y + vec4(0.0, i1.y, i2.y, 1.0))
      + i.x + vec4(0.0, i1.x, i2.x, 1.0));
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    vec4 norm = 1.79284291400159 - 0.85373472095314 * vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
  }
  
  void main() {
    vNormal = normalize(normalMatrix * normal);
    
    // Noise-based displacement
    float noise = snoise(position * 3.0 + uTime * 0.5);
    vNoise = noise;
    
    // Audio-reactive pulsation
    float pulse = 1.0 + uAudioLevel * 0.4 * sin(uTime * 10.0);
    vec3 displaced = position * pulse + normal * noise * 0.1 * (1.0 + uAudioLevel);
    
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
  varying float vNoise;
  
  void main() {
    // Fresnel effect
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 2.5);
    
    // Quantum shimmer
    float shimmer = sin(uTime * 8.0 + vPosition.x * 15.0 + vPosition.y * 15.0) * 0.5 + 0.5;
    
    // Base color with charge influence
    vec3 baseColor = uColor;
    if (uCharge > 0.3) {
      baseColor = mix(baseColor, vec3(0.0, 1.0, 0.5), uCharge * 0.4);
    } else if (uCharge < -0.3) {
      baseColor = mix(baseColor, vec3(1.0, 0.5, 0.0), abs(uCharge) * 0.4);
    }
    
    // Importance glow
    vec3 glowColor = baseColor * (1.0 + fresnel * 2.0 * uImportance);
    glowColor += vec3(0.2, 1.0, 0.4) * shimmer * uAudioLevel * fresnel;
    
    // Energy core highlight
    float core = smoothstep(0.8, 1.0, fresnel);
    glowColor += vec3(1.0) * core * 0.3;
    
    gl_FragColor = vec4(glowColor, 0.85 + fresnel * 0.15);
  }
`;

// ═══════════════════════════════════════════════════════════════════
// Thought Particle Mesh
// ═══════════════════════════════════════════════════════════════════

function ThoughtParticleMesh({ 
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
  const trailRef = useRef<THREE.Group>(null);

  // Shader uniforms
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
      // Apply velocity with damping
      const dampedVelocity = particle.velocity.clone().multiplyScalar(0.016);
      meshRef.current.position.add(dampedVelocity);
      
      // Gentle organic rotation
      meshRef.current.rotation.x += 0.008 + audioLevel * 0.01;
      meshRef.current.rotation.y += 0.005 + audioLevel * 0.008;
      
      // Life-based scaling
      const age = time - particle.birthTime;
      const lifeRatio = Math.min(age / particle.lifespan, 1);
      const fadeScale = 1.0 - lifeRatio * 0.6;
      meshRef.current.scale.setScalar(fadeScale);
    }
  });

  // Calculate size based on importance
  const size = Math.max(0.4, particle.importance * 1.5);

  return (
    <group ref={trailRef}>
      <Trail
        width={0.08 + audioLevel * 0.05}
        length={6}
        color={particle.color}
        attenuation={(width) => width * width}
      >
        <mesh ref={meshRef} position={particle.position}>
          <icosahedronGeometry args={[size, 2]} />
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
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Neural Connection Filaments
// ═══════════════════════════════════════════════════════════════════

function NeuralFilaments({ 
  particles, 
  audioLevel 
}: { 
  particles: ThoughtParticle[];
  audioLevel: number;
}) {
  const linesRef = useRef<THREE.LineSegments>(null);

  const geometry = useMemo(() => {
    const positions: number[] = [];
    const colors: number[] = [];

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];
        const distance = p1.position.distanceTo(p2.position);

        if (distance < 4.0) {
          positions.push(
            p1.position.x, p1.position.y, p1.position.z,
            p2.position.x, p2.position.y, p2.position.z
          );

          // Color gradient based on connection strength
          const strength = 1.0 - distance / 4.0;
          const mixedColor = p1.color.clone().lerp(p2.color, 0.5);
          mixedColor.multiplyScalar(strength);

          colors.push(mixedColor.r, mixedColor.g, mixedColor.b);
          colors.push(mixedColor.r, mixedColor.g, mixedColor.b);
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
      <lineBasicMaterial 
        vertexColors 
        blending={THREE.AdditiveBlending} 
        transparent 
        opacity={0.25 + audioLevel * 0.2}
        linewidth={1}
      />
    </lineSegments>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Field Background
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
  
  // Simplex noise
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }
  
  float snoise(vec2 v) {
    const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                       -0.577350269189626, 0.024390243902439);
    vec2 i = floor(v + dot(v, C.yy));
    vec2 x0 = v - i + dot(i, C.xx);
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
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
    g.x = a0.x * x0.x + h.x * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
  }
  
  void main() {
    vec2 uv = vUv;
    
    // Multi-layer noise
    float noise1 = snoise(uv * 3.0 + uTime * 0.15);
    float noise2 = snoise(uv * 6.0 - uTime * 0.1);
    float noise3 = snoise(uv * 12.0 + uTime * 0.08);
    
    // Audio reactivity
    float audioBoost = uAudioLevel * 0.4;
    
    // Combine noises
    float finalNoise = (noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2) * (1.0 + audioBoost);
    
    // Color mixing
    vec3 color = mix(uColor1, uColor2, finalNoise * 0.5 + 0.5);
    
    // Quantum grid lines
    float gridX = smoothstep(0.97, 1.0, sin(uv.x * 60.0 + uTime * 0.5));
    float gridY = smoothstep(0.97, 1.0, sin(uv.y * 60.0 + uTime * 0.3));
    float grid = max(gridX, gridY);
    color += vec3(0.2, 1.0, 0.4) * grid * 0.15 * (1.0 + audioBoost);
    
    // Radial vignette
    float vignette = 1.0 - length(uv - 0.5) * 0.8;
    color *= vignette;
    
    gl_FragColor = vec4(color, 0.12);
  }
`;

function QuantumFieldBackground({ audioLevel }: { audioLevel: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
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
    <mesh ref={meshRef} position={[0, 0, -15]}>
      <planeGeometry args={[40, 30]} />
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
}

// ═══════════════════════════════════════════════════════════════════
// Ambient Sparkle Field
// ═══════════════════════════════════════════════════════════════════

function AmbientSparkles({ audioLevel, engineState }: { audioLevel: number; engineState: string }) {
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
      count={150}
      scale={20}
      size={2 + audioLevel * 4}
      speed={0.3 + audioLevel * 1}
      opacity={0.4 + audioLevel * 0.3}
      color={sparkleColor}
    />
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Particle System
// ═══════════════════════════════════════════════════════════════════

function ParticleSystem({ particles, audioLevel, engineState }: ParticleSystemProps) {
  const groupRef = useRef<THREE.Group>(null);
  const { clock } = useThree();

  useFrame((state) => {
    if (groupRef.current) {
      // Gentle system rotation
      groupRef.current.rotation.y += 0.001;
      
      // React to speaking state
      if (engineState === "SPEAKING") {
        groupRef.current.scale.setScalar(1.0 + audioLevel * 0.08);
      } else {
        groupRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.05);
      }
    }
  });

  // Filter alive particles
  const aliveParticles = particles.filter(
    (p) => clock.elapsedTime - p.birthTime < p.lifespan
  );

  return (
    <group ref={groupRef}>
      <QuantumFieldBackground audioLevel={audioLevel} />
      <NeuralFilaments particles={aliveParticles} audioLevel={audioLevel} />
      <AmbientSparkles audioLevel={audioLevel} engineState={engineState} />
      
      {aliveParticles.map((particle) => (
        <ThoughtParticleMesh
          key={particle.id}
          particle={particle}
          audioLevel={audioLevel}
          time={clock.elapsedTime}
        />
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Post-Processing
// ═══════════════════════════════════════════════════════════════════

function PostEffects({ audioLevel }: { audioLevel: number }) {
  return (
    <EffectComposer>
      <Bloom
        intensity={0.8 + audioLevel * 0.4}
        luminanceThreshold={0.3}
        luminanceSmoothing={0.9}
        kernelSize={KernelSize.LARGE}
      />
      <ChromaticAberration
        offset={new THREE.Vector2(0.001 + audioLevel * 0.0005, 0.001 + audioLevel * 0.0005)}
        blendFunction={BlendFunction.NORMAL}
      />
    </EffectComposer>
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

  const [particles, setParticles] = useState<ThoughtParticle[]>([]);
  const particlesRef = useRef<ThoughtParticle[]>([]);

  // Convert transcript messages to particles
  useEffect(() => {
    if (transcript.length === 0) return;

    const latestMessage = transcript[transcript.length - 1];
    const words = latestMessage.content.split(/\s+/).filter(w => w.length > 0);

    const newParticles: ThoughtParticle[] = words.map((word, index) => {
      const charge = calculateEmotionalCharge(word);
      const importance = calculateImportance(word);
      
      // Color based on type and charge
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
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 5,
          (Math.random() - 0.5) * 5
        ),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.015,
          0.008 + Math.random() * 0.015,
          (Math.random() - 0.5) * 0.015
        ),
        mass: importance * 2,
        charge,
        decay: 0.001,
        birthTime: performance.now() / 1000,
        lifespan: 18 + importance * 12,
        type: latestMessage.role,
        importance,
        color,
      };
    });

    particlesRef.current = [...particlesRef.current, ...newParticles];
    setParticles([...particlesRef.current]);
  }, [transcript]);

  // Cleanup old particles
  useEffect(() => {
    const interval = setInterval(() => {
      const now = performance.now() / 1000;
      particlesRef.current = particlesRef.current.filter(
        (p) => now - p.birthTime < p.lifespan
      );
      setParticles([...particlesRef.current]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

  return (
    <div className="fixed inset-0 z-5 pointer-events-none">
      <Canvas
        camera={{ position: [0, 0, 12], fov: 55 }}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: "high-performance",
          toneMapping: THREE.ACESFilmicToneMapping,
        }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.15} />
        <pointLight position={[10, 10, 10]} intensity={0.4} color="#39ff14" />
        <pointLight position={[-10, -10, -10]} intensity={0.25} color="#00ff41" />
        
        <ParticleSystem
          particles={particles}
          audioLevel={audioLevel}
          engineState={engineState}
        />
        
        <PostEffects audioLevel={audioLevel} />
      </Canvas>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════

function calculateEmotionalCharge(word: string): number {
  const positiveWords = [
    "great", "awesome", "excellent", "love", "perfect", "amazing", "good", 
    "happy", "thanks", "yes", "beautiful", "fantastic", "wonderful", "brilliant"
  ];
  const negativeWords = [
    "bad", "error", "fail", "wrong", "problem", "issue", "bug", "crash", 
    "no", "sorry", "broken", "stuck", "frustrated", "confused"
  ];
  
  const lowerWord = word.toLowerCase();
  if (positiveWords.includes(lowerWord)) return 0.8;
  if (negativeWords.includes(lowerWord)) return -0.8;
  return 0;
}

function calculateImportance(word: string): number {
  const techTerms = [
    "function", "class", "api", "database", "server", "client", "async", 
    "await", "error", "debug", "component", "module", "interface", "type",
    "algorithm", "optimization", "performance", "security", "authentication"
  ];
  const lowerWord = word.toLowerCase();
  
  if (techTerms.includes(lowerWord)) return 1.0;
  if (word.length > 8) return 0.85;
  if (word.length > 5) return 0.65;
  return 0.45;
}
