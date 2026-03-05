"use client";
/**
 * QuantumNeuralAvatar — The Living AI Presence
 * 
 * A 3D avatar representing Aether's neural voice interface.
 * Based on Quantum Neural Topology concept with:
 * - Neural network mesh structure
 * - Voice-synced pulsation and glow
 * - Emotional state visualization
 * - Multiple size variants for different contexts
 * 
 * Color Palette:
 * - Neon Green (#39ff14) — Primary accent
 * - Dark Carbon Fiber (#0a0a0a) — Background
 * - Medium Gray (#6b7280) — Secondary details
 */

import React, { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Float, MeshDistortMaterial, Sphere, Trail } from "@react-three/drei";
import { useAetherStore, type EngineState } from "@/store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════

interface AvatarProps {
  size?: "icon" | "small" | "medium" | "large" | "fullscreen";
  variant?: "minimal" | "standard" | "detailed";
  showConnections?: boolean;
  interactive?: boolean;
}

interface NeuralNodeProps {
  position: THREE.Vector3;
  intensity: number;
  audioLevel: number;
  state: EngineState;
}

interface SynapticConnectionProps {
  start: THREE.Vector3;
  end: THREE.Vector3;
  activity: number;
  audioLevel: number;
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Neural Color System
// ═══════════════════════════════════════════════════════════════════

const QUANTUM_COLORS = {
  neonGreen: {
    primary: new THREE.Color("#39ff14"),
    bright: new THREE.Color("#5fff3f"),
    dim: new THREE.Color("#1a5c1a"),
    glow: new THREE.Color("#00ff41"),
  },
  carbonFiber: {
    dark: new THREE.Color("#0a0a0a"),
    medium: new THREE.Color("#1a1a1a"),
    light: new THREE.Color("#2d2d2d"),
  },
  mediumGray: {
    primary: new THREE.Color("#6b7280"),
    light: new THREE.Color("#9ca3af"),
    dark: new THREE.Color("#4b5563"),
  },
};

// ═══════════════════════════════════════════════════════════════════
// Neural Node Component
// ═══════════════════════════════════════════════════════════════════

function NeuralNode({ position, intensity, audioLevel, state }: NeuralNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const lightRef = useRef<THREE.PointLight>(null);

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsate with audio
      const pulse = 1.0 + audioLevel * 0.5 * Math.sin(state.clock.elapsedTime * 10);
      meshRef.current.scale.setScalar(pulse);
      
      // Rotate slowly
      meshRef.current.rotation.x += 0.01;
      meshRef.current.rotation.y += 0.005;
    }

    if (lightRef.current) {
      // Light intensity follows audio
      lightRef.current.intensity = 0.5 + audioLevel * 2 * intensity;
    }
  });

  // Color based on state
  const color = useMemo(() => {
    switch (state) {
      case "LISTENING":
        return QUANTUM_COLORS.neonGreen.primary;
      case "THINKING":
        return QUANTUM_COLORS.neonGreen.bright;
      case "SPEAKING":
        return QUANTUM_COLORS.neonGreen.glow;
      case "INTERRUPTING":
        return new THREE.Color("#ff4444");
      default:
        return QUANTUM_COLORS.neonGreen.dim;
    }
  }, [state]);

  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.08 * intensity, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.8 + audioLevel * 0.2}
        />
      </mesh>
      <pointLight
        ref={lightRef}
        color={color}
        distance={3}
        intensity={0.5 + audioLevel}
      />
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Synaptic Connection Component
// ═══════════════════════════════════════════════════════════════════

function SynapticConnection({ start, end, activity, audioLevel }: SynapticConnectionProps) {
  const lineRef = useRef<any>(null);
  const particlesRef = useRef<THREE.Points>(null);

  // Calculate curve points
  const curve = useMemo(() => {
    const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
    mid.z += 0.5; // Add curve
    return new THREE.QuadraticBezierCurve3(start, mid, end);
  }, [start, end]);

  const points = useMemo(() => curve.getPoints(20), [curve]);

  useFrame((state) => {
    if (particlesRef.current) {
      // Animate particles along the curve
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
      const time = state.clock.elapsedTime;
      
      for (let i = 0; i < 5; i++) {
        const t = (time * 0.5 + i * 0.2) % 1;
        const point = curve.getPoint(t);
        positions[i * 3] = point.x;
        positions[i * 3 + 1] = point.y;
        positions[i * 3 + 2] = point.z;
      }
      
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <group>
      {/* Connection line */}
      <line ref={lineRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array(points.flatMap(p => [p.x, p.y, p.z])), 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color={QUANTUM_COLORS.neonGreen.primary}
          transparent
          opacity={0.2 + activity * 0.3 + audioLevel * 0.3}
          blending={THREE.AdditiveBlending}
        />
      </line>

      {/* Traveling particles */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array(15), 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          color={QUANTUM_COLORS.neonGreen.glow}
          size={0.05}
          transparent
          opacity={0.8}
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Quantum Core — The Central Presence
// ═══════════════════════════════════════════════════════════════════

function QuantumCore({ audioLevel, state }: { audioLevel: number; state: EngineState }) {
  const coreRef = useRef<THREE.Group>(null);
  const innerRef = useRef<THREE.Mesh>(null);
  const outerRef = useRef<THREE.Mesh>(null);

  useFrame((frameState) => {
    const t = frameState.clock.elapsedTime;

    if (coreRef.current) {
      // Gentle floating
      coreRef.current.position.y = Math.sin(t * 0.5) * 0.1;
      
      // Rotation based on state
      const rotSpeed = state === "THINKING" ? 0.02 : 0.005;
      coreRef.current.rotation.y += rotSpeed;
      coreRef.current.rotation.z = Math.sin(t * 0.3) * 0.05;
    }

    if (innerRef.current) {
      // Inner core pulsation
      const pulse = 1.0 + audioLevel * 0.3 * Math.sin(t * 8);
      innerRef.current.scale.setScalar(pulse);
    }

    if (outerRef.current) {
      // Outer shell breathing
      const breathe = 1.0 + Math.sin(t * 2) * 0.05 + audioLevel * 0.2;
      outerRef.current.scale.setScalar(breathe);
    }
  });

  // State-based colors
  const coreColor = useMemo(() => {
    switch (state) {
      case "LISTENING":
        return QUANTUM_COLORS.neonGreen.primary;
      case "THINKING":
        return QUANTUM_COLORS.neonGreen.bright;
      case "SPEAKING":
        return QUANTUM_COLORS.neonGreen.glow;
      default:
        return QUANTUM_COLORS.neonGreen.dim;
    }
  }, [state]);

  return (
    <group ref={coreRef}>
      {/* Outer protective shell */}
      <mesh ref={outerRef}>
        <icosahedronGeometry args={[1.2, 1]} />
        <meshBasicMaterial
          color={QUANTUM_COLORS.carbonFiber.medium}
          wireframe
          transparent
          opacity={0.3}
        />
      </mesh>

      {/* Main core */}
      <mesh ref={innerRef}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <MeshDistortMaterial
          color={coreColor}
          speed={3}
          distort={0.3 + audioLevel * 0.2}
          radius={1}
          emissive={coreColor}
          emissiveIntensity={0.5 + audioLevel}
        />
      </mesh>

      {/* Inner glow */}
      <pointLight
        color={coreColor}
        intensity={1 + audioLevel * 3}
        distance={5}
      />

      {/* Orbiting rings */}
      {[0, 1, 2].map((i) => (
        <mesh
          key={i}
          rotation={[Math.PI / 2, (i * Math.PI) / 3, 0]}
        >
          <torusGeometry args={[1.5 + i * 0.3, 0.02, 16, 100]} />
          <meshBasicMaterial
            color={QUANTUM_COLORS.neonGreen.primary}
            transparent
            opacity={0.2 + audioLevel * 0.3}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Neural Network Mesh
// ═══════════════════════════════════════════════════════════════════

function NeuralNetwork({ nodeCount, audioLevel, state }: { 
  nodeCount: number; 
  audioLevel: number; 
  state: EngineState;
}) {
  const networkRef = useRef<THREE.Group>(null);

  // Generate neural nodes
  const nodes = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    for (let i = 0; i < nodeCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 2 + Math.random() * 2;
      
      positions.push(new THREE.Vector3(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      ));
    }
    return positions;
  }, [nodeCount]);

  // Generate connections
  const connections = useMemo(() => {
    const conns: [number, number][] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dist = nodes[i].distanceTo(nodes[j]);
        if (dist < 2.5 && Math.random() > 0.7) {
          conns.push([i, j]);
        }
      }
    }
    return conns;
  }, [nodes]);

  useFrame((frameState) => {
    if (networkRef.current) {
      // Rotate entire network
      networkRef.current.rotation.y += 0.002;
      
      // React to speaking state
      if (state === "SPEAKING") {
        networkRef.current.scale.setScalar(1.0 + audioLevel * 0.1);
      }
    }
  });

  return (
    <group ref={networkRef}>
      {/* Render nodes */}
      {nodes.map((pos, i) => (
        <NeuralNode
          key={i}
          position={pos}
          intensity={0.5 + Math.random() * 0.5}
          audioLevel={audioLevel}
          state={state}
        />
      ))}

      {/* Render connections */}
      {connections.map(([i, j], idx) => (
        <SynapticConnection
          key={idx}
          start={nodes[i]}
          end={nodes[j]}
          activity={Math.random()}
          audioLevel={audioLevel}
        />
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Voice Resonance Waves
// ═══════════════════════════════════════════════════════════════════

function VoiceResonance({ audioLevel, state }: { audioLevel: number; state: EngineState }) {
  const wavesRef = useRef<THREE.Group>(null);

  useFrame((frameState) => {
    if (!wavesRef.current) return;
    
    const t = frameState.clock.elapsedTime;
    
    wavesRef.current.children.forEach((child, i) => {
      const mesh = child as THREE.Mesh;
      const scale = 1 + (i * 0.5) + Math.sin(t * 3 + i) * 0.2 + audioLevel * 0.5;
      mesh.scale.setScalar(scale);
      
      const material = mesh.material as THREE.MeshBasicMaterial;
      material.opacity = (0.3 - i * 0.05) * (1 - audioLevel * 0.3);
    });
  });

  if (state !== "SPEAKING" && state !== "LISTENING") return null;

  return (
    <group ref={wavesRef}>
      {[0, 1, 2, 3].map((i) => (
        <mesh key={i} rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[1 + i * 0.5, 1.1 + i * 0.5, 64]} />
          <meshBasicMaterial
            color={QUANTUM_COLORS.neonGreen.primary}
            transparent
            opacity={0.3 - i * 0.05}
            side={THREE.DoubleSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
    </group>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Avatar Scene
// ═══════════════════════════════════════════════════════════════════

function AvatarScene({ size, showConnections, audioLevel, state }: {
  size: number;
  showConnections: boolean;
  audioLevel: number;
  state: EngineState;
}) {
  const { camera } = useThree();

  useEffect(() => {
    camera.position.z = size;
  }, [camera, size]);

  return (
    <>
      <ambientLight intensity={0.1} />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#39ff14" />
      <pointLight position={[-10, -10, -10]} intensity={0.3} color="#00ff41" />
      
      <Float
        speed={2}
        rotationIntensity={0.5}
        floatIntensity={0.5}
      >
        <QuantumCore audioLevel={audioLevel} state={state} />
      </Float>

      {showConnections && (
        <NeuralNetwork
          nodeCount={30}
          audioLevel={audioLevel}
          state={state}
        />
      )}

      <VoiceResonance audioLevel={audioLevel} state={state} />
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
    icon: 3,
    small: 5,
    medium: 8,
    large: 12,
    fullscreen: 15,
  };

  const canvasSize = sizeMap[size];

  // Container styles based on size
  const containerStyles = {
    icon: { width: 48, height: 48 },
    small: { width: 120, height: 120 },
    medium: { width: 240, height: 240 },
    large: { width: 400, height: 400 },
    fullscreen: { width: "100%", height: "100%" },
  };

  return (
    <div
      className="quantum-avatar"
      style={{
        ...containerStyles[size],
        position: "relative",
        borderRadius: size === "icon" ? "50%" : "24px",
        overflow: "hidden",
        background: "radial-gradient(circle at center, #1a1a1a 0%, #0a0a0a 100%)",
      }}
    >
      {/* Carbon fiber texture overlay */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(45deg, transparent 48%, #2d2d2d 49%, #2d2d2d 51%, transparent 52%),
            linear-gradient(-45deg, transparent 48%, #2d2d2d 49%, #2d2d2d 51%, transparent 52%)
          `,
          backgroundSize: "8px 8px",
        }}
      />

      <Canvas
        camera={{ position: [0, 0, canvasSize], fov: 50 }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        dpr={[1, 2]}
      >
        <AvatarScene
          size={canvasSize}
          showConnections={showConnections && variant !== "minimal"}
          audioLevel={audioLevel}
          state={engineState}
        />
      </Canvas>

      {/* Status indicator for icon size */}
      {size === "icon" && (
        <div
          className="absolute bottom-1 right-1 w-2 h-2 rounded-full"
          style={{
            backgroundColor: engineState === "SPEAKING" ? "#39ff14" : 
                            engineState === "LISTENING" ? "#00ff41" : "#4b5563",
            boxShadow: engineState !== "IDLE" ? "0 0 8px #39ff14" : "none",
          }}
        />
      )}
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
  return <QuantumNeuralAvatar size="fullscreen" variant="detailed" showConnections={true} />;
}
