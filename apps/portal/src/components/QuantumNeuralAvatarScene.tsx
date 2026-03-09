"use client";
/**
 * QuantumNeuralAvatarScene — Extracted Scene Content
 * 
 * Contains all 3D elements for the avatar WITHOUT the Canvas wrapper.
 * Used by UnifiedScene for consolidated rendering.
 */

import React, { useRef, useMemo, memo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import {
  Float,
  MeshDistortMaterial,
  Sparkles,
  Trail,
} from "@react-three/drei";
import {
  useAetherStore,
  type AvatarCinematicState,
  type EngineState,
} from "@/store/useAetherStore";

// ═══════════════════════════════════════════════════════════════════
// Quantum Neural Color System
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
  accent: {
    cyan: new THREE.Color("#00f3ff"),
    purple: new THREE.Color("#bc13fe"),
    amber: new THREE.Color("#f59e0b"),
    crimson: new THREE.Color("#ff1744"),
    gold: new THREE.Color("#ffd700"),
  },
};

// ═══════════════════════════════════════════════════════════════════
// Custom Shaders — Quantum Field Effects (Optimized)
// ═══════════════════════════════════════════════════════════════════

const quantumFieldVertexShader = `
  uniform float uTime;
  uniform float uAudioLevel;
  varying vec2 vUv;
  varying vec3 vPosition;
  varying vec3 vNormal;
  
  // Simplified noise function for better performance
  float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1);
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
  }
  
  float noise(vec3 x) {
    vec3 p = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(mix(hash(p), hash(p + vec3(1,0,0)), f.x),
          mix(hash(p + vec3(0,1,0)), hash(p + vec3(1,1,0)), f.x), f.y),
      mix(mix(hash(p + vec3(0,0,1)), hash(p + vec3(1,0,1)), f.x),
          mix(hash(p + vec3(0,1,1)), hash(p + vec3(1,1,1)), f.x), f.y), f.z
    );
  }
  
  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    
    float n = noise(position * 2.0 + uTime * 0.3);
    float audioDisplacement = uAudioLevel * 0.12;
    vec3 displaced = position + normal * (n * 0.08 + audioDisplacement);
    
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
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = pow(1.0 - max(dot(viewDir, vNormal), 0.0), 3.0);
    
    float pattern = sin(vPosition.x * 15.0 + uTime * 1.5) *
                   sin(vPosition.y * 15.0 + uTime * 1.2) *
                   sin(vPosition.z * 15.0 + uTime * 1.4);
    pattern = smoothstep(0.3, 0.7, pattern * 0.5 + 0.5);
    
    vec3 baseColor = mix(uColor, uSecondaryColor, pattern);
    vec3 glowColor = baseColor * (1.0 + fresnel * 1.5 + uAudioLevel * uStateIntensity);
    
    float pulse = sin(uTime * 4.0 + length(vPosition) * 8.0) * 0.5 + 0.5;
    pulse *= uAudioLevel;
    
    vec3 finalColor = glowColor + vec3(0.2, 1.0, 0.3) * pulse * fresnel;
    
    gl_FragColor = vec4(finalColor, 0.85 + fresnel * 0.15);
  }
`;

// ═══════════════════════════════════════════════════════════════════
// Quantum Consciousness Core
// ═══════════════════════════════════════════════════════════════════

interface AvatarSceneProps {
  size: number;
  showConnections: boolean;
  state: EngineState;
  cinematicState: AvatarCinematicState;
  variant: string;
  gazeTarget: [number, number, number];
  lowMotionMode: boolean;
}

export const AvatarSceneContent = memo(function AvatarSceneContent({
  size,
  showConnections,
  state,
  cinematicState,
  variant,
  gazeTarget,
  lowMotionMode,
}: AvatarSceneProps) {
  const { camera } = useThree();
  const sceneRootRef = useRef<THREE.Group>(null);
  const targetVector = useMemo(
    () => new THREE.Vector3(...gazeTarget),
    [gazeTarget]
  );
  const lookAtMatrix = useMemo(() => new THREE.Matrix4(), []);
  const targetQuaternion = useMemo(() => new THREE.Quaternion(), []);

  // Update camera position based on size
  React.useEffect(() => {
    camera.position.z = size;
  }, [camera, size]);

  useFrame(() => {
    if (!sceneRootRef.current) return;
    lookAtMatrix.lookAt(
      sceneRootRef.current.position,
      targetVector,
      new THREE.Vector3(0, 1, 0)
    );
    targetQuaternion.setFromRotationMatrix(lookAtMatrix);
    sceneRootRef.current.quaternion.slerp(
      targetQuaternion,
      lowMotionMode ? 0.03 : 0.08
    );
  });

  return (
    <group ref={sceneRootRef}>
      {/* Main Consciousness Core */}
      <Float
        speed={lowMotionMode ? 0.35 : 1.2}
        rotationIntensity={lowMotionMode ? 0.08 : 0.25}
        floatIntensity={lowMotionMode ? 0.1 : 0.35}
      >
        <QuantumConsciousnessCore state={state} lowMotionMode={lowMotionMode} />
      </Float>

      {/* Holographic Voice Rings */}
      <HolographicVoiceRings state={state} cinematicState={cinematicState} />

      {/* Neural Synaptic Mesh */}
      {showConnections && (
        <NeuralSynapticMesh
          state={state}
          cinematicState={cinematicState}
          nodeCount={variant === "immersive" ? 35 : 20}
          lowMotionMode={lowMotionMode}
        />
      )}

      {/* Quantum Particles */}
      <QuantumParticleField
        state={state}
        cinematicState={cinematicState}
        lowMotionMode={lowMotionMode}
      />

      {/* Orbiting Energy Trails */}
      {variant !== "minimal" && (
        <OrbitingEnergyTrails
          state={state}
          cinematicState={cinematicState}
          lowMotionMode={lowMotionMode}
        />
      )}
    </group>
  );
});

// Implementation for QuantumConsciousnessCore with direct state access
const QuantumConsciousnessCore = memo(function QuantumConsciousnessCore({
  state,
  lowMotionMode,
}: {
  state: EngineState;
  lowMotionMode: boolean;
}) {
  const coreRef = useRef<THREE.Group>(null);
  const innerRef = useRef<THREE.Mesh>(null);
  const quantumShellRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const colors = useMemo(() => {
    const stateColors = {
      IDLE: { primary: QUANTUM_COLORS.neonGreen.dim, secondary: QUANTUM_COLORS.carbonFiber.medium, intensity: 0.3 },
      LISTENING: { primary: QUANTUM_COLORS.neonGreen.primary, secondary: QUANTUM_COLORS.neonGreen.electric, intensity: 0.8 },
      THINKING: { primary: QUANTUM_COLORS.accent.gold, secondary: QUANTUM_COLORS.neonGreen.bright, intensity: 1.2 },
      SPEAKING: { primary: QUANTUM_COLORS.neonGreen.glow, secondary: QUANTUM_COLORS.neonGreen.plasma, intensity: 1.5 },
      INTERRUPTING: { primary: QUANTUM_COLORS.accent.crimson, secondary: QUANTUM_COLORS.accent.amber, intensity: 2.0 },
    };
    return (stateColors[state as keyof typeof stateColors] || stateColors.IDLE) as any;
  }, [state]);

  const shaderUniforms = useMemo(() => ({
    uTime: { value: 0 },
    uAudioLevel: { value: 0 },
    uColor: { value: colors.primary },
    uSecondaryColor: { value: colors.secondary },
    uStateIntensity: { value: colors.intensity },
  }), [colors]);

  useFrame((frameState) => {
    const t = frameState.clock.elapsedTime;
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = t;
      materialRef.current.uniforms.uAudioLevel.value = audioLevel;
    }

    const cinematicState = useAetherStore.getState().avatarCinematicState;

    if (coreRef.current) {
      coreRef.current.position.y = Math.sin(t * 0.5) * 0.12;
      const rotSpeed =
        cinematicState === "EUREKA"
          ? 0.04
          : cinematicState === "ERROR"
            ? 0.01
            : state === "THINKING"
              ? 0.025
              : state === "SPEAKING"
                ? 0.015
                : 0.006;
      coreRef.current.rotation.y += lowMotionMode ? rotSpeed * 0.35 : rotSpeed;
    }

    if (innerRef.current) {
      const pulse = lowMotionMode
        ? 1.0 + Math.sin(t * 1.1) * 0.02 + audioLevel * 0.08 * Math.sin(t * 3)
        : 1.0 + Math.sin(t * 3) * 0.06 + audioLevel * 0.3 * Math.sin(t * 10);
      innerRef.current.scale.setScalar(pulse);
    }

    if (quantumShellRef.current) {
      const breathe = lowMotionMode
        ? 1.0 + Math.sin(t * 0.8) * 0.02 + audioLevel * 0.08
        : 1.0 + Math.sin(t * 1.5) * 0.05 + audioLevel * 0.2;
      quantumShellRef.current.scale.setScalar(breathe);
      quantumShellRef.current.rotation.x += lowMotionMode ? 0.0007 : 0.002;
    }
  });

  return (
    <group ref={coreRef}>
      <mesh ref={quantumShellRef}>
        <icosahedronGeometry args={[1.6, 2]} />
        <meshBasicMaterial
          color={colors.primary}
          wireframe
          transparent
          opacity={0.2} // Opacity also updated in frame if needed, but fixed is fine for wireframe
        />
      </mesh>

      <mesh rotation={[Math.PI / 4, 0, Math.PI / 4]}>
        <icosahedronGeometry args={[1.4, 1]} />
        <meshBasicMaterial
          color={colors.secondary}
          wireframe
          transparent
          opacity={0.12}
        />
      </mesh>

      <mesh ref={innerRef}>
        <sphereGeometry args={[0.9, 48, 48]} />
        <shaderMaterial
          ref={materialRef}
          vertexShader={quantumFieldVertexShader}
          fragmentShader={quantumFieldFragmentShader}
          uniforms={shaderUniforms}
          transparent
          side={THREE.DoubleSide}
        />
      </mesh>

      <mesh>
        <sphereGeometry args={[0.4, 24, 24]} />
        <MeshDistortMaterial
          color={colors.primary}
          speed={4}
          distort={0.35}
          radius={1}
          emissive={colors.primary}
          emissiveIntensity={1.2}
        />
      </mesh>

      <pointLight
        color={colors.primary}
        intensity={1.5}
        distance={6}
        decay={2}
      />
    </group>
  );
});

// ═══════════════════════════════════════════════════════════════════
// Holographic Voice Rings (Optimized)
// ═══════════════════════════════════════════════════════════════════

const HolographicVoiceRings = memo(function HolographicVoiceRings({
  state,
  cinematicState,
}: {
  state: EngineState;
  cinematicState: AvatarCinematicState;
}) {
  const ringsRef = useRef<THREE.Group>(null);
  const ringCount = 4;

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
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

    ringsRef.current.children.forEach((ring, i) => {
      const mesh = ring as THREE.Mesh;
      const phase = (t * 2 + i * 0.3) % (Math.PI * 2);
      const expansion = 1.2 + i * 0.4 + Math.sin(phase) * 0.25 + audioLevel * 0.4;
      mesh.scale.setScalar(expansion);
      mesh.rotation.z = t * (0.15 + i * 0.08) * (i % 2 === 0 ? 1 : -1);
      const material = mesh.material as THREE.MeshBasicMaterial;
      const baseOpacity =
        state === "SPEAKING" || state === "LISTENING" ? 0.35 : 0.12;
      const cinematicBoost = cinematicState === "EUREKA" ? 0.18 : 0;
      const cinematicPenalty = cinematicState === "ERROR" ? 0.08 : 0;
      material.opacity =
        baseOpacity - i * 0.05 + audioLevel * 0.25 + cinematicBoost - cinematicPenalty;
    });
  });

  if (state === "IDLE") return null;

  return (
    <group ref={ringsRef} rotation={[Math.PI / 2, 0, 0]}>
      {Array.from({ length: ringCount }).map((_, i) => (
        <mesh key={i}>
          <ringGeometry args={[1.2 + i * 0.4, 1.25 + i * 0.4, 48]} />
          <meshBasicMaterial
            color={ringColor}
            transparent
            opacity={0.35 - i * 0.05}
            side={THREE.DoubleSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
    </group>
  );
});

// ═══════════════════════════════════════════════════════════════════
// Neural Synaptic Mesh (Optimized)
// ═══════════════════════════════════════════════════════════════════

const NeuralSynapticMesh = memo(function NeuralSynapticMesh({
  state,
  cinematicState,
  nodeCount = 30,
  lowMotionMode,
}: {
  state: EngineState;
  cinematicState: AvatarCinematicState;
  nodeCount?: number;
  lowMotionMode: boolean;
}) {
  const networkRef = useRef<THREE.Group>(null);
  const nodesRef = useRef<THREE.InstancedMesh>(null);

  const { nodePositions, connectionGeometry } = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    const conns: [number, number][] = [];

    for (let i = 0; i < nodeCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 2.5 + Math.random() * 1.2;

      positions.push(new THREE.Vector3(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      ));
    }

    for (let i = 0; i < positions.length; i++) {
      for (let j = i + 1; j < positions.length; j++) {
        const dist = positions[i].distanceTo(positions[j]);
        if (dist < 1.6 && Math.random() > 0.65) {
          conns.push([i, j]);
        }
      }
    }

    const posArr: number[] = [];
    conns.forEach(([i, j]) => {
      posArr.push(positions[i].x, positions[i].y, positions[i].z, positions[j].x, positions[j].y, positions[j].z);
    });

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(posArr, 3));

    return { nodePositions: positions, connectionGeometry: geo };
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

  useFrame((frameState) => {
    const t = frameState.clock.elapsedTime;
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

    if (networkRef.current) {
      networkRef.current.rotation.y += lowMotionMode ? 0.0004 : 0.0015;
      if (state === "SPEAKING" || cinematicState === "EUREKA") {
        networkRef.current.scale.setScalar(
          1.0 + audioLevel * (lowMotionMode ? 0.03 : 0.1)
        );
      } else if (cinematicState === "ERROR") {
        networkRef.current.scale.setScalar(0.95);
      }
    }

    if (nodesRef.current) {
      const matrix = new THREE.Matrix4();
      const position = new THREE.Vector3();
      const scale = new THREE.Vector3();
      const quaternion = new THREE.Quaternion();

      for (let i = 0; i < nodeCount; i++) {
        const pulse = lowMotionMode
          ? 1.0 + Math.sin(t * 1.3 + i) * 0.04 * audioLevel
          : 1.0 + Math.sin(t * 4 + i) * 0.15 * audioLevel;
        position.copy(nodePositions[i]);
        scale.setScalar(0.05 * pulse);
        matrix.compose(position, quaternion, scale);
        nodesRef.current.setMatrixAt(i, matrix);
      }
      nodesRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <group ref={networkRef}>
      <instancedMesh ref={nodesRef} args={[undefined, undefined, nodeCount]}>
        <sphereGeometry args={[1, 6, 6]} />
        <meshBasicMaterial color={nodeColor} transparent opacity={0.7} />
      </instancedMesh>

      <lineSegments geometry={connectionGeometry}>
        <lineBasicMaterial
          color={nodeColor}
          transparent
          opacity={0.15}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>
    </group>
  );
});

// ═══════════════════════════════════════════════════════════════════
// Quantum Particle Field (Uses drei Sparkles)
// ═══════════════════════════════════════════════════════════════════

const QuantumParticleField = memo(function QuantumParticleField({
  state,
  cinematicState,
  lowMotionMode,
}: {
  state: EngineState;
  cinematicState: AvatarCinematicState;
  lowMotionMode: boolean;
}) {
  const [audioLevel, setAudioLevel] = React.useState(0);

  useFrame(() => {
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    setAudioLevel(engineState === "SPEAKING" ? speakerLevel : micLevel);
  });

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
      count={lowMotionMode ? 70 : 150}
      scale={7}
      size={lowMotionMode ? 1.8 + audioLevel * 2.2 : 2.5 + audioLevel * 4}
      opacity={lowMotionMode ? 0.28 + audioLevel * 0.18 : 0.5 + audioLevel * 0.35}
      color={particleColor}
      speed={lowMotionMode ? 0.18 : cinematicState === "EUREKA" ? 2.5 : 0.4 + audioLevel * 1.5}
    />
  );
});

// ═══════════════════════════════════════════════════════════════════
// Orbiting Energy Trails (Reduced count)
// ═══════════════════════════════════════════════════════════════════

const OrbitingEnergyTrails = memo(function OrbitingEnergyTrails({
  state,
  cinematicState,
  lowMotionMode,
}: {
  state: EngineState;
  cinematicState: AvatarCinematicState;
  lowMotionMode: boolean;
}) {
  const orbitersRef = useRef<THREE.Group>(null);
  const orbiterCount = 2;

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
    const { micLevel, speakerLevel, engineState } = useAetherStore.getState();
    const audioLevel = engineState === "SPEAKING" ? speakerLevel : micLevel;

    orbitersRef.current.children.forEach((orbiter, i) => {
      const speed = lowMotionMode
        ? 0.16 + i * 0.08 + audioLevel * 0.12
        : 0.4 + i * 0.25 + audioLevel * 0.4;
      const cinematicMultiplier =
        cinematicState === "EUREKA" ? 1.8 : cinematicState === "ERROR" ? 0.7 : 1.0;
      const cinematicRadius =
        cinematicState === "EUREKA" ? 0.25 : cinematicState === "ERROR" ? -0.2 : 0.0;
      const angle = t * speed + (i * Math.PI * 2) / orbiterCount;
      const radius = 2.0 + i * 0.25 + cinematicRadius;

      orbiter.position.x = Math.cos(angle * cinematicMultiplier) * radius;
      orbiter.position.y = Math.sin(angle * 0.5) * 0.4;
      orbiter.position.z = Math.sin(angle * cinematicMultiplier) * radius;
    });
  });

  return (
    <group ref={orbitersRef}>
      {Array.from({ length: orbiterCount }).map((_, i) => (
        <Trail
          key={i}
          width={lowMotionMode ? 0.08 : 0.12}
          length={lowMotionMode ? 3 : 6}
          color={trailColor}
          attenuation={(width) => width}
        >
          <mesh>
            <sphereGeometry args={[0.06, 12, 12]} />
            <meshBasicMaterial color={trailColor} />
          </mesh>
        </Trail>
      ))}
    </group>
  );
});
