"use client";
/**
 * QuantumNeuralAvatar — The Evolved AI Consciousness
 * 
 * An extraordinary 3D avatar representing Aether's neural voice interface.
 * Features advanced visualization with:
 * - Quantum field simulations with electromagnetic wave effects
 * - Dynamic neural topology with synaptic firing
 * - Holographic voice resonance rings
 * - Advanced post-processing (bloom, chromatic aberration)
 * - Physics-based particle systems
 * - State-responsive animations
 * 
 * Color Palette:
 * - Neon Green (#39ff14) — Primary neural accent
 * - Dark Carbon Fiber (#0a0a0a) — Deep background
 * - Medium Gray (#6b7280) — Secondary elements
 */

import React, { useRef, useMemo, useEffect, useCallback, useState } from "react";
import { Canvas, useFrame, useThree, extend } from "@react-three/fiber";
import * as THREE from "three";
import { 
  Float, 
  MeshDistortMaterial, 
  Sphere, 
  Trail, 
  Sparkles,
  Environment,
  MeshTransmissionMaterial,
  useTexture,
  Outlines,
  PointMaterial,
} from "@react-three/drei";
import { EffectComposer, Bloom, ChromaticAberration, Vignette, Noise, GodRays } from "@react-three/postprocessing";
import { BlendFunction, KernelSize } from "postprocessing";
import { useAetherStore, type EngineState } from "@/store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════

interface AvatarProps {
  size?: "icon" | "small" | "medium" | "large" | "fullscreen";
  variant?: "minimal" | "standard" | "detailed" | "immersive";
  showConnections?: boolean;
  interactive?: boolean;
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Neural Color System — Enhanced Palette
// ═══════════════════════════════════════════════════════════════════

const QUANTUM_COLORS = {
  neonGreen: {
    primary: new THREE.Color("#39ff14"),
    bright: new THREE.Color("#5fff3f"),
    electric: new THREE.Color("#00ff88"),
    dim: new THREE.Color("#1a5c1a"),
    glow: new THREE.Color("#00ff41"),
    plasma: new THREE.Color("#7fff00"),
  },
  carbonFiber: {
    void: new THREE.Color("#050505"),
    dark: new THREE.Color("#0a0a0a"),
    medium: new THREE.Color("#1a1a1a"),
    light: new THREE.Color("#2d2d2d"),
  },
  mediumGray: {
    primary: new THREE.Color("#6b7280"),
    light: new THREE.Color("#9ca3af"),
    dark: new THREE.Color("#4b5563"),
  },
  accent: {
    cyan: new THREE.Color("#00f3ff"),
    purple: new THREE.Color("#bc13fe"),
    amber: new THREE.Color("#f59e0b"),
    crimson: new THREE.Color("#ff1744"),
    gold: new THREE.Color("#ffd700"),
  },
  state: {
    idle: new THREE.Color("#1a5c1a"),
    listening: new THREE.Color("#39ff14"),
    thinking: new THREE.Color("#ffd700"),
    speaking: new THREE.Color("#00ff88"),
    interrupting: new THREE.Color("#ff1744"),
  },
};

// ═══════════════════════════════════════════════════════════════════
// Custom Shaders — Quantum Field Effects
// ═══════════════════════════════════════════════════════════════════

const quantumFieldVertexShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  varying vec2 vUv;
  varying vec3 vPosition;
  varying vec3 vNormal;
  
  // Simplex noise
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
  
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
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
  }
  
  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    
    // Quantum field displacement
    float noise = snoise(position * 2.0 + uTime * 0.3);
    float audioDisplacement = uAudioLevel * 0.15;
    vec3 displaced = position + normal * (noise * 0.1 + audioDisplacement);
    
    vPosition = displaced;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
  }
`;

const quantumFieldFragmentShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  uniform vec3 uColor;
  uniform vec3 uSecondaryColor;
  uniform float uStateIntensity;
  
  varying vec2 vUv;
  varying vec3 vPosition;
  varying vec3 vNormal;
  
  void main() {
    // Fresnel effect for ethereal glow
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 3.0);
    
    // Quantum field pattern
    float pattern = sin(vPosition.x * 20.0 + uTime * 2.0) * 
                   sin(vPosition.y * 20.0 + uTime * 1.5) * 
                   sin(vPosition.z * 20.0 + uTime * 1.8);
    pattern = smoothstep(0.3, 0.7, pattern * 0.5 + 0.5);
    
    // Color mixing based on audio and state
    vec3 baseColor = mix(uColor, uSecondaryColor, pattern);
    vec3 glowColor = baseColor * (1.0 + fresnel * 2.0 + uAudioLevel * uStateIntensity);
    
    // Energy pulse waves
    float pulse = sin(uTime * 5.0 + length(vPosition) * 10.0) * 0.5 + 0.5;
    pulse *= uAudioLevel;
    
    vec3 finalColor = glowColor + vec3(0.2, 1.0, 0.3) * pulse * fresnel;
    
    gl_FragColor = vec4(finalColor, 0.85 + fresnel * 0.15);
  }
`;

// ═══════════════════════════════════════════════════════════════════
// Quantum Consciousness Core — The Heart of the Avatar
// ═══════════════════════════════════════════════════════════════════

function QuantumConsciousnessCore({ 
  audioLevel, 
  state 
}: { 
  audioLevel: number; 
  state: EngineState 
}) {
  const coreRef = useRef<THREE.Group>(null);
  const innerRef = useRef<THREE.Mesh>(null);
  const quantumShellRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  // State-based colors
  const colors = useMemo(() => {
    const stateColors = {
      IDLE: { primary: QUANTUM_COLORS.neonGreen.dim, secondary: QUANTUM_COLORS.carbonFiber.medium, intensity: 0.3 },
      LISTENING: { primary: QUANTUM_COLORS.neonGreen.primary, secondary: QUANTUM_COLORS.neonGreen.electric, intensity: 0.8 },
      THINKING: { primary: QUANTUM_COLORS.accent.gold, secondary: QUANTUM_COLORS.neonGreen.bright, intensity: 1.2 },
      SPEAKING: { primary: QUANTUM_COLORS.neonGreen.glow, secondary: QUANTUM_COLORS.neonGreen.plasma, intensity: 1.5 },
      INTERRUPTING: { primary: QUANTUM_COLORS.accent.crimson, secondary: QUANTUM_COLORS.accent.amber, intensity: 2.0 },
    };
    return stateColors[state] || stateColors.IDLE;
  }, [state]);

  // Shader uniforms
  const shaderUniforms = useMemo(() => ({
    uTime: { value: 0 },
    uAudioLevel: { value: 0 },
    uColor: { value: colors.primary },
    uSecondaryColor: { value: colors.secondary },
    uStateIntensity: { value: colors.intensity },
  }), [colors]);

  useFrame((frameState) => {
    const t = frameState.clock.elapsedTime;

    // Update shader uniforms
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = t;
      materialRef.current.uniforms.uAudioLevel.value = audioLevel;
      materialRef.current.uniforms.uColor.value = colors.primary;
      materialRef.current.uniforms.uSecondaryColor.value = colors.secondary;
      materialRef.current.uniforms.uStateIntensity.value = colors.intensity;
    }

    if (coreRef.current) {
      // Floating motion
      coreRef.current.position.y = Math.sin(t * 0.5) * 0.15;
      
      // State-based rotation speeds
      const rotSpeed = state === "THINKING" ? 0.03 : 
                       state === "SPEAKING" ? 0.02 : 
                       state === "INTERRUPTING" ? 0.05 : 0.008;
      coreRef.current.rotation.y += rotSpeed;
      coreRef.current.rotation.z = Math.sin(t * 0.3) * 0.08;
    }

    if (innerRef.current) {
      // QUANTUM BREATHING — Non-linear organic pulsation
      // Base breath: 0.98 → 1.02 range with complex sine layering
      const baseBreath = 1.0 + Math.sin(t * 0.8) * 0.02;
      const secondaryPulse = Math.sin(t * 1.3 + 1) * 0.01;
      const tertiaryRipple = Math.sin(t * 0.5 + 2) * 0.005;
      
      // Audio-synced pulse
      const audioPulse = audioLevel * 0.15 * Math.sin(t * 8);
      
      // Combined quantum breathing effect
      const totalScale = baseBreath + secondaryPulse + tertiaryRipple + audioPulse;
      innerRef.current.scale.setScalar(totalScale);
    }

    if (quantumShellRef.current) {
      // Outer quantum shell breathing with enhanced non-linearity
      const breathe = 1.0 + 
                      Math.sin(t * 0.6) * 0.04 + 
                      Math.sin(t * 1.1) * 0.02 +
                      audioLevel * 0.2;
      quantumShellRef.current.scale.setScalar(breathe);
      quantumShellRef.current.rotation.x += 0.003;
      quantumShellRef.current.rotation.z -= 0.002;
    }
  });

  return (
    <group ref={coreRef}>
      {/* Outer Quantum Shell — Wireframe icosahedron */}
      <mesh ref={quantumShellRef}>
        <icosahedronGeometry args={[1.6, 2]} />
        <meshBasicMaterial
          color={colors.primary}
          wireframe
          transparent
          opacity={0.25 + audioLevel * 0.2}
        />
      </mesh>

      {/* Secondary Rotating Shell */}
      <mesh rotation={[Math.PI / 4, 0, Math.PI / 4]}>
        <icosahedronGeometry args={[1.4, 1]} />
        <meshBasicMaterial
          color={colors.secondary}
          wireframe
          transparent
          opacity={0.15}
        />
      </mesh>

      {/* Main Consciousness Core — Custom shader */}
      <mesh ref={innerRef}>
        <sphereGeometry args={[0.9, 64, 64]} />
        <shaderMaterial
          ref={materialRef}
          vertexShader={quantumFieldVertexShader}
          fragmentShader={quantumFieldFragmentShader}
          uniforms={shaderUniforms}
          transparent
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Inner Energy Core */}
      <mesh>
        <sphereGeometry args={[0.4, 32, 32]} />
        <MeshDistortMaterial
          color={colors.primary}
          speed={5 + audioLevel * 10}
          distort={0.4 + audioLevel * 0.3}
          radius={1}
          emissive={colors.primary}
          emissiveIntensity={1.5 + audioLevel * 2}
        />
      </mesh>

      {/* Central Point Light */}
      <pointLight
        color={colors.primary}
        intensity={2 + audioLevel * 5}
        distance={8}
        decay={2}
      />
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Holographic Voice Resonance Rings
// ═══════════════════════════════════════════════════════════════════

function HolographicVoiceRings({ 
  audioLevel, 
  state 
}: { 
  audioLevel: number; 
  state: EngineState 
}) {
  const ringsRef = useRef<THREE.Group>(null);
  const ringCount = 5;

  const ringColor = useMemo(() => {
    switch (state) {
      case "SPEAKING": return QUANTUM_COLORS.neonGreen.glow;
      case "LISTENING": return QUANTUM_COLORS.neonGreen.primary;
      case "THINKING": return QUANTUM_COLORS.accent.gold;
      case "INTERRUPTING": return QUANTUM_COLORS.accent.crimson;
      default: return QUANTUM_COLORS.neonGreen.dim;
    }
  }, [state]);

  useFrame((frameState) => {
    if (!ringsRef.current) return;
    const t = frameState.clock.elapsedTime;
    
    ringsRef.current.children.forEach((ring, i) => {
      const mesh = ring as THREE.Mesh;
      
      // Expanding wave effect
      const phase = (t * 2 + i * 0.3) % (Math.PI * 2);
      const expansion = 1.2 + i * 0.4 + Math.sin(phase) * 0.3 + audioLevel * 0.5;
      mesh.scale.setScalar(expansion);
      
      // Rotation
      mesh.rotation.z = t * (0.2 + i * 0.1) * (i % 2 === 0 ? 1 : -1);
      
      // Opacity based on audio
      const material = mesh.material as THREE.MeshBasicMaterial;
      const baseOpacity = (state === "SPEAKING" || state === "LISTENING") ? 0.4 : 0.15;
      material.opacity = baseOpacity - i * 0.06 + audioLevel * 0.3;
    });
  });

  if (state === "IDLE") return null;

  return (
    <group ref={ringsRef} rotation={[Math.PI / 2, 0, 0]}>
      {Array.from({ length: ringCount }).map((_, i) => (
        <mesh key={i}>
          <ringGeometry args={[1.2 + i * 0.4, 1.25 + i * 0.4, 64]} />
          <meshBasicMaterial
            color={ringColor}
            transparent
            opacity={0.4 - i * 0.06}
            side={THREE.DoubleSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Electromagnetic Field Lines
// ═══════════════════════════════════════════════════════════════════

function ElectromagneticField({ 
  audioLevel, 
  state 
}: { 
  audioLevel: number; 
  state: EngineState 
}) {
  const fieldRef = useRef<THREE.Group>(null);
  const lineCount = 12;

  useFrame((frameState) => {
    if (!fieldRef.current) return;
    const t = frameState.clock.elapsedTime;

    fieldRef.current.children.forEach((child, i) => {
      const line = child as THREE.Line;
      const positions = line.geometry.attributes.position.array as Float32Array;
      
      // Animate field lines
      for (let j = 0; j < positions.length / 3; j++) {
        const angle = (i / lineCount) * Math.PI * 2 + t * 0.5;
        const radius = 2 + Math.sin(j * 0.5 + t * 2) * 0.3 + audioLevel * 0.5;
        const height = (j - 10) * 0.2;
        
        positions[j * 3] = Math.cos(angle + j * 0.1) * radius;
        positions[j * 3 + 1] = height;
        positions[j * 3 + 2] = Math.sin(angle + j * 0.1) * radius;
      }
      
      line.geometry.attributes.position.needsUpdate = true;
    });
  });

  const fieldColor = useMemo(() => {
    switch (state) {
      case "SPEAKING": return QUANTUM_COLORS.neonGreen.electric;
      case "LISTENING": return QUANTUM_COLORS.neonGreen.primary;
      case "THINKING": return QUANTUM_COLORS.accent.gold;
      default: return QUANTUM_COLORS.neonGreen.dim;
    }
  }, [state]);

  // Pre-generate geometries
  const geometries = useMemo(() => {
    return Array.from({ length: lineCount }).map((_, i) => {
      const points = Array.from({ length: 20 }, (_, j) => {
        const angle = (i / lineCount) * Math.PI * 2;
        const radius = 2 + Math.sin(j * 0.5) * 0.3;
        const height = (j - 10) * 0.2;
        return new THREE.Vector3(
          Math.cos(angle) * radius,
          height,
          Math.sin(angle) * radius
        );
      });
      return new THREE.BufferGeometry().setFromPoints(points);
    });
  }, [lineCount]);

  return (
    <group ref={fieldRef}>
      {geometries.map((geometry, i) => (
        <primitive key={i} object={new THREE.Line(
          geometry,
          new THREE.LineBasicMaterial({
            color: fieldColor,
            transparent: true,
            opacity: 0.3 + audioLevel * 0.3,
            blending: THREE.AdditiveBlending,
          })
        )} />
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Neural Network Synaptic Mesh
// ═══════════════════════════════════════════════════════════════════

function NeuralSynapticMesh({ 
  audioLevel, 
  state,
  nodeCount = 40 
}: { 
  audioLevel: number; 
  state: EngineState;
  nodeCount?: number;
}) {
  const networkRef = useRef<THREE.Group>(null);
  const nodesRef = useRef<THREE.InstancedMesh>(null);
  const connectionsRef = useRef<THREE.LineSegments>(null);

  // Generate stable node positions
  const { nodePositions, connections } = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    const conns: [number, number][] = [];
    
    for (let i = 0; i < nodeCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 2.5 + Math.random() * 1.5;
      
      positions.push(new THREE.Vector3(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      ));
    }
    
    // Generate connections
    for (let i = 0; i < positions.length; i++) {
      for (let j = i + 1; j < positions.length; j++) {
        const dist = positions[i].distanceTo(positions[j]);
        if (dist < 1.8 && Math.random() > 0.6) {
          conns.push([i, j]);
        }
      }
    }
    
    return { nodePositions: positions, connections: conns };
  }, [nodeCount]);

  const nodeColor = useMemo(() => {
    switch (state) {
      case "SPEAKING": return QUANTUM_COLORS.neonGreen.glow;
      case "LISTENING": return QUANTUM_COLORS.neonGreen.primary;
      case "THINKING": return QUANTUM_COLORS.accent.gold;
      case "INTERRUPTING": return QUANTUM_COLORS.accent.crimson;
      default: return QUANTUM_COLORS.neonGreen.dim;
    }
  }, [state]);

  // Create connection geometry
  const connectionGeometry = useMemo(() => {
    const positions: number[] = [];
    connections.forEach(([i, j]) => {
      positions.push(
        nodePositions[i].x, nodePositions[i].y, nodePositions[i].z,
        nodePositions[j].x, nodePositions[j].y, nodePositions[j].z
      );
    });
    
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    return geo;
  }, [nodePositions, connections]);

  useFrame((frameState) => {
    const t = frameState.clock.elapsedTime;

    if (networkRef.current) {
      networkRef.current.rotation.y += 0.002;
      
      if (state === "SPEAKING") {
        networkRef.current.scale.setScalar(1.0 + audioLevel * 0.15);
      }
    }

    // Animate node instances
    if (nodesRef.current) {
      const matrix = new THREE.Matrix4();
      const position = new THREE.Vector3();
      const scale = new THREE.Vector3();
      const quaternion = new THREE.Quaternion();

      for (let i = 0; i < nodeCount; i++) {
        const basePos = nodePositions[i];
        const pulse = 1.0 + Math.sin(t * 5 + i) * 0.2 * audioLevel;
        
        position.copy(basePos);
        scale.setScalar(0.06 * pulse);
        matrix.compose(position, quaternion, scale);
        nodesRef.current.setMatrixAt(i, matrix);
      }
      nodesRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <group ref={networkRef}>
      {/* Neural Nodes */}
      <instancedMesh ref={nodesRef} args={[undefined, undefined, nodeCount]}>
        <sphereGeometry args={[1, 8, 8]} />
        <meshBasicMaterial 
          color={nodeColor} 
          transparent 
          opacity={0.8 + audioLevel * 0.2}
        />
      </instancedMesh>

      {/* Synaptic Connections */}
      <lineSegments ref={connectionsRef} geometry={connectionGeometry}>
        <lineBasicMaterial
          color={nodeColor}
          transparent
          opacity={0.2 + audioLevel * 0.3}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Particle Field
// ═══════════════════════════════════════════════════════════════════

function QuantumParticleField({ 
  audioLevel, 
  state 
}: { 
  audioLevel: number; 
  state: EngineState 
}) {
  const particleColor = useMemo(() => {
    switch (state) {
      case "SPEAKING": return "#00ff88";
      case "LISTENING": return "#39ff14";
      case "THINKING": return "#ffd700";
      case "INTERRUPTING": return "#ff1744";
      default: return "#1a5c1a";
    }
  }, [state]);

  return (
    <Sparkles
      count={200}
      scale={8}
      size={3 + audioLevel * 5}
      speed={0.5 + audioLevel * 2}
      opacity={0.6 + audioLevel * 0.4}
      color={particleColor}
    />
  );
}

// ═══════════════════════════════════════════════════════════════════
// Orbiting Energy Trails
// ═══════════════════════════════════════════════════════════════════

function OrbitingEnergyTrails({ 
  audioLevel, 
  state 
}: { 
  audioLevel: number; 
  state: EngineState 
}) {
  const orbitersRef = useRef<THREE.Group>(null);
  const orbiterCount = 3;

  const trailColor = useMemo(() => {
    switch (state) {
      case "SPEAKING": return QUANTUM_COLORS.neonGreen.glow;
      case "LISTENING": return QUANTUM_COLORS.neonGreen.primary;
      case "THINKING": return QUANTUM_COLORS.accent.gold;
      default: return QUANTUM_COLORS.neonGreen.dim;
    }
  }, [state]);

  useFrame((frameState) => {
    if (!orbitersRef.current) return;
    const t = frameState.clock.elapsedTime;

    orbitersRef.current.children.forEach((orbiter, i) => {
      const speed = 0.5 + i * 0.3 + audioLevel * 0.5;
      const angle = t * speed + (i * Math.PI * 2) / orbiterCount;
      const radius = 2.2 + i * 0.3;
      const tilt = (i * Math.PI) / 6;

      orbiter.position.x = Math.cos(angle) * radius;
      orbiter.position.y = Math.sin(angle * 0.5) * 0.5;
      orbiter.position.z = Math.sin(angle) * radius * Math.cos(tilt);
    });
  });

  return (
    <group ref={orbitersRef}>
      {Array.from({ length: orbiterCount }).map((_, i) => (
        <Trail
          key={i}
          width={0.15 + audioLevel * 0.1}
          length={8}
          color={trailColor}
          attenuation={(width) => width}
        >
          <mesh>
            <sphereGeometry args={[0.08, 16, 16]} />
            <meshBasicMaterial color={trailColor} />
          </mesh>
        </Trail>
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Post-Processing Effects
// ═══════════════════════════════════════════════════════════════════

function PostProcessingEffects({ audioLevel, state }: { audioLevel: number; state: EngineState }) {
  const bloomIntensity = useMemo(() => {
    switch (state) {
      case "SPEAKING": return 1.5 + audioLevel * 0.5;
      case "LISTENING": return 1.0 + audioLevel * 0.3;
      case "THINKING": return 1.2;
      case "INTERRUPTING": return 2.0;
      default: return 0.6;
    }
  }, [state, audioLevel]);

  return (
    <EffectComposer>
      <Bloom
        intensity={bloomIntensity}
        luminanceThreshold={0.2}
        luminanceSmoothing={0.9}
        kernelSize={KernelSize.LARGE}
      />
      <ChromaticAberration
        offset={new THREE.Vector2(0.002 + audioLevel * 0.001, 0.002 + audioLevel * 0.001)}
        blendFunction={BlendFunction.NORMAL}
      />
      <Vignette
        offset={0.3}
        darkness={0.8}
        blendFunction={BlendFunction.NORMAL}
      />
      <Noise 
        opacity={0.02} 
        blendFunction={BlendFunction.OVERLAY}
      />
    </EffectComposer>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Avatar Scene
// ═══════════════════════════════════════════════════════════════════

function AvatarScene({ 
  size, 
  showConnections, 
  audioLevel, 
  state,
  variant 
}: {
  size: number;
  showConnections: boolean;
  audioLevel: number;
  state: EngineState;
  variant: string;
}) {
  const { camera } = useThree();

  useEffect(() => {
    camera.position.z = size;
  }, [camera, size]);

  return (
    <>
      {/* Ambient Lighting */}
      <ambientLight intensity={0.1} />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#39ff14" />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#00ff41" />
      <pointLight position={[0, -10, 5]} intensity={0.2} color="#1a5c1a" />

      {/* Main Consciousness Core */}
      <Float
        speed={1.5}
        rotationIntensity={0.3}
        floatIntensity={0.4}
      >
        <QuantumConsciousnessCore audioLevel={audioLevel} state={state} />
      </Float>

      {/* Holographic Voice Rings */}
      <HolographicVoiceRings audioLevel={audioLevel} state={state} />

      {/* Electromagnetic Field */}
      {variant === "detailed" || variant === "immersive" ? (
        <ElectromagneticField audioLevel={audioLevel} state={state} />
      ) : null}

      {/* Neural Synaptic Mesh */}
      {showConnections && (
        <NeuralSynapticMesh 
          audioLevel={audioLevel} 
          state={state} 
          nodeCount={variant === "immersive" ? 60 : 40}
        />
      )}

      {/* Quantum Particles */}
      <QuantumParticleField audioLevel={audioLevel} state={state} />

      {/* Orbiting Energy Trails */}
      {variant !== "minimal" && (
        <OrbitingEnergyTrails audioLevel={audioLevel} state={state} />
      )}

      {/* Post-Processing */}
      <PostProcessingEffects audioLevel={audioLevel} state={state} />
    </>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Component Export
// ═══════════════════════════════════════════════════════════════════

export default function QuantumNeuralAvatar({
  size = "medium",
  variant = "standard",
  showConnections = true,
  interactive = false,
}: AvatarProps) {
  const micLevel = useAetherStore((s) => s.micLevel);
  const speakerLevel = useAetherStore((s) => s.speakerLevel);
  const engineState = useAetherStore((s) => s.engineState);

  // Determine audio level based on state
  const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

  // Size mapping
  const sizeMap = {
    icon: 4,
    small: 6,
    medium: 10,
    large: 14,
    fullscreen: 18,
  };

  const canvasSize = sizeMap[size];

  // Container styles
  const containerStyles = {
    icon: { width: 64, height: 64 },
    small: { width: 160, height: 160 },
    medium: { width: 320, height: 320 },
    large: { width: 500, height: 500 },
    fullscreen: { width: "100%", height: "100%" },
  };

  // State indicator color
  const stateIndicatorColor = useMemo(() => {
    switch (engineState) {
      case "SPEAKING": return "#00ff88";
      case "LISTENING": return "#39ff14";
      case "THINKING": return "#ffd700";
      case "INTERRUPTING": return "#ff1744";
      default: return "#4b5563";
    }
  }, [engineState]);

  return (
    <div
      className="quantum-neural-avatar relative"
      style={{
        ...containerStyles[size],
        borderRadius: size === "icon" ? "50%" : "32px",
        overflow: "hidden",
        background: "radial-gradient(circle at center, #0f0f0f 0%, #050505 100%)",
      }}
    >
      {/* Carbon fiber texture overlay */}
      <div
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(45deg, transparent 48%, #1a1a1a 49%, #1a1a1a 51%, transparent 52%),
            linear-gradient(-45deg, transparent 48%, #1a1a1a 49%, #1a1a1a 51%, transparent 52%)
          `,
          backgroundSize: "6px 6px",
        }}
      />

      {/* Glow effect behind canvas */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle at center, ${stateIndicatorColor}20 0%, transparent 60%)`,
          filter: "blur(20px)",
        }}
      />

      <Canvas
        camera={{ position: [0, 0, canvasSize], fov: 45 }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
        }}
        dpr={[1, 2]}
      >
        <AvatarScene
          size={canvasSize}
          showConnections={showConnections && variant !== "minimal"}
          audioLevel={audioLevel}
          state={engineState}
          variant={variant}
        />
      </Canvas>

      {/* State indicator pulse */}
      {size !== "fullscreen" && (
        <div
          className="absolute bottom-2 right-2 rounded-full"
          style={{
            width: size === "icon" ? 8 : 12,
            height: size === "icon" ? 8 : 12,
            backgroundColor: stateIndicatorColor,
            boxShadow: engineState !== "IDLE" 
              ? `0 0 12px ${stateIndicatorColor}, 0 0 24px ${stateIndicatorColor}40` 
              : "none",
            animation: engineState !== "IDLE" ? "pulse 2s ease-in-out infinite" : "none",
          }}
        />
      )}

      {/* CSS for pulse animation */}
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.8; }
        }
      `}</style>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Static Avatar Variants for Export
// ═══════════════════════════════════════════════════════════════════

export function AvatarIcon() {
  return <QuantumNeuralAvatar size="icon" variant="minimal" showConnections={false} />;
}

export function AvatarSmall() {
  return <QuantumNeuralAvatar size="small" variant="minimal" showConnections={false} />;
}

export function AvatarMedium() {
  return <QuantumNeuralAvatar size="medium" variant="standard" showConnections={true} />;
}

export function AvatarLarge() {
  return <QuantumNeuralAvatar size="large" variant="detailed" showConnections={true} />;
}

export function AvatarFullscreen() {
  return <QuantumNeuralAvatar size="fullscreen" variant="immersive" showConnections={true} />;
}
