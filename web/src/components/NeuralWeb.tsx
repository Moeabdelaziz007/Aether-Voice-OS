'use client';

import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame, Canvas } from '@react-three/fiber';
import { Float, Sphere, MeshDistortMaterial } from '@react-three/drei';
import { motion } from 'framer-motion';

export interface HandoverEvent {
    id: string;
    fromAgent: string;
    toAgent: string;
    task: string;
    status: 'pending' | 'active' | 'completed';
}

/**
 * NeuralMesh - The Three.js background component.
 * Visualizes a dynamic network of nodes and pulsing edges (Synapses).
 */
function NeuralMesh({ active }: { active: boolean }) {
    const groupRef = useRef<THREE.Group>(null);
    const count = 50;
    const maxDistance = 3.5; // Synaptic connection threshold

    const { positions, velocities } = useMemo(() => {
        const pos = new Float32Array(count * 3);
        const vel = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            pos[i * 3] = (Math.random() - 0.5) * 12;
            pos[i * 3 + 1] = (Math.random() - 0.5) * 12;
            pos[i * 3 + 2] = (Math.random() - 0.5) * 6;

            vel[i * 3] = (Math.random() - 0.5) * 0.015;
            vel[i * 3 + 1] = (Math.random() - 0.5) * 0.015;
            vel[i * 3 + 2] = (Math.random() - 0.5) * 0.015;
        }
        return { positions: pos, velocities: vel };
    }, []);

    const pointsRef = useRef<THREE.Points>(null);
    const linesRef = useRef<THREE.LineSegments>(null);

    useFrame(() => {
        if (!pointsRef.current || !linesRef.current) return;

        const posAttr = pointsRef.current.geometry.attributes.position.array as Float32Array;

        // Update positions
        for (let i = 0; i < count; i++) {
            posAttr[i * 3] += velocities[i * 3];
            posAttr[i * 3 + 1] += velocities[i * 3 + 1];
            posAttr[i * 3 + 2] += velocities[i * 3 + 2];

            // Boundary bounce
            if (Math.abs(posAttr[i * 3]) > 7) velocities[i * 3] *= -1;
            if (Math.abs(posAttr[i * 3 + 1]) > 7) velocities[i * 3 + 1] *= -1;
            if (Math.abs(posAttr[i * 3 + 2]) > 4) velocities[i * 3 + 2] *= -1;
        }
        pointsRef.current.geometry.attributes.position.needsUpdate = true;

        // Calculate dynamic edges (Synapses)
        const linePositions = [];
        const lineOpacities = [];
        let connections = 0;

        for (let i = 0; i < count; i++) {
            for (let j = i + 1; j < count; j++) {
                const dx = posAttr[i * 3] - posAttr[j * 3];
                const dy = posAttr[i * 3 + 1] - posAttr[j * 3 + 1];
                const dz = posAttr[i * 3 + 2] - posAttr[j * 3 + 2];
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                if (dist < maxDistance) {
                    const alpha = 1.0 - dist / maxDistance;
                    linePositions.push(
                        posAttr[i * 3], posAttr[i * 3 + 1], posAttr[i * 3 + 2],
                        posAttr[j * 3], posAttr[j * 3 + 1], posAttr[j * 3 + 2]
                    );
                    lineOpacities.push(alpha, alpha);
                    connections++;
                }
            }
        }

        linesRef.current.geometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        linesRef.current.geometry.setAttribute('color', new THREE.Float32BufferAttribute(lineOpacities.flatMap(a => [0, 0.95, 1, a * (active ? 0.6 : 0.2)]), 4));

        if (groupRef.current) {
            groupRef.current.rotation.y += 0.0005;
            groupRef.current.rotation.x += 0.0002;
        }
    });

    return (
        <group ref={groupRef}>
            {/* Nodes */}
            <points ref={pointsRef}>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={count}
                        array={positions}
                        itemSize={3}
                    />
                </bufferGeometry>
                <pointsMaterial
                    size={0.12}
                    color={active ? "#00f3ff" : "#555"}
                    transparent
                    opacity={0.8}
                    sizeAttenuation
                    blending={THREE.AdditiveBlending}
                />
            </points>

            {/* Synaptic Edges */}
            <lineSegments ref={linesRef}>
                <bufferGeometry />
                <lineBasicMaterial
                    vertexColors
                    transparent
                    blending={THREE.AdditiveBlending}
                    depthWrite={false}
                />
            </lineSegments>

            {/* Pulsing Core */}
            <Float speed={3} rotationIntensity={1} floatIntensity={1}>
                <Sphere args={[0.6, 64, 64]}>
                    <MeshDistortMaterial
                        color={active ? "#bc13fe" : "#111"}
                        speed={3}
                        distort={0.4}
                        radius={1}
                        emissive={active ? "#bc13fe" : "#000"}
                        emissiveIntensity={active ? 2.5 : 0}
                        wireframe={!active}
                    />
                </Sphere>
            </Float>
        </group>
    );
}

export const NeuralWeb: React.FC<{ events: HandoverEvent[] }> = ({ events }) => {
    return (
        <div className="relative w-full h-[240px] carbon-panel rounded-2xl border border-white/5 overflow-hidden mt-4 group">
            {/* Background Three.js Context */}
            <div className="absolute inset-0 z-0 bg-[#020202] transition-colors duration-1000">
                <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} intensity={1.5} color="#00f3ff" />
                    <pointLight position={[-10, -10, -10]} intensity={1} color="#bc13fe" />
                    <NeuralMesh active={events.length > 0} />
                </Canvas>
            </div>

            {/* Overlay Grid / Scanlines */}
            <div className="absolute inset-0 z-10 pointer-events-none opacity-20"
                style={{
                    backgroundImage: 'linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px)',
                    backgroundSize: '20px 20px'
                }}
            />
            <div className="absolute inset-0 z-10 pointer-events-none shadow-[inset_0_0_80px_rgba(0,0,0,0.9)]" />

            {/* Content Layer */}
            <div className="relative z-20 p-4 flex flex-col h-full">
                <div className="flex justify-between items-center mb-4 border-b border-[#00f3ff]/10 pb-2">
                    <span className="text-[10px] text-[#00f3ff] uppercase tracking-[0.3em] font-bold">
                        Cognitive Mesh Routing
                    </span>
                    <div className="flex items-center gap-2 bg-[#00f3ff]/5 px-2 py-1 rounded-full border border-[#00f3ff]/20">
                        <div className={`w-1.5 h-1.5 rounded-full ${events.length > 0 ? 'bg-[#00f3ff] animate-ping' : 'bg-white/20'}`} />
                        <span className="text-[8px] text-white/50 uppercase tracking-widest font-mono">
                            {events.length} Active Vectors
                        </span>
                    </div>
                </div>

                <div className="flex-1 space-y-2 overflow-y-auto scrollbar-thin pr-2">
                    {events.map((event, i) => (
                        <motion.div
                            key={event.id}
                            initial={{ opacity: 0, x: -20, scale: 0.95 }}
                            animate={{ opacity: 1, x: 0, scale: 1 }}
                            transition={{ delay: i * 0.1, type: "spring" }}
                            className="bg-[#00f3ff]/5 border border-[#00f3ff]/10 rounded-lg p-2 flex items-center justify-between group/item hover:bg-[#00f3ff]/10 hover:border-[#00f3ff]/30 transition-all backdrop-blur-md"
                        >
                            <div className="flex items-center gap-3">
                                <div className="text-[9px] font-mono text-[#00f3ff] shadow-[0_0_10px_rgba(0,243,255,0.2)] bg-[#00f3ff]/10 px-2 py-0.5 rounded">
                                    {event.fromAgent}
                                </div>

                                <div className="flex items-center justify-center w-8 relative">
                                    <div className="h-px bg-[#00f3ff]/30 w-full absolute" />
                                    <motion.div
                                        className="w-1.5 h-1.5 rounded-full bg-[#bc13fe] shadow-[0_0_8px_#bc13fe] z-10"
                                        animate={{ x: [-12, 12] }}
                                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                                    />
                                </div>

                                <div className="text-[9px] font-mono text-[#bc13fe] shadow-[0_0_10px_rgba(188,19,254,0.2)] bg-[#bc13fe]/10 px-2 py-0.5 rounded">
                                    {event.toAgent}
                                </div>
                            </div>
                            <div className="text-[9px] text-white/60 truncate max-w-[120px] font-mono uppercase tracking-widest pl-4">
                                {event.task}
                            </div>
                        </motion.div>
                    ))}

                    {events.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center opacity-30 mt-4 mix-blend-screen">
                            <div className="text-[10px] font-mono uppercase tracking-[0.4em] text-[#00f3ff]">Idle Synapses</div>
                            <div className="w-24 h-px bg-gradient-to-r from-transparent via-[#00f3ff] to-transparent mt-2" />
                        </div>
                    )}
                </div>
            </div>
            {/* Subtle Neon Underglow */}
            <div className="absolute -bottom-px left-1/4 right-1/4 h-px bg-gradient-to-r from-transparent via-[#bc13fe] to-transparent opacity-50" />
        </div>
    );
};
