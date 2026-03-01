'use client';

import React, { useRef, useMemo, useEffect } from 'react';
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
 * Visualizes a dynamic network of nodes and pulsing edges.
 */
function NeuralMesh({ active }: { active: boolean }) {
    const groupRef = useRef<THREE.Group>(null);
    const count = 40;

    const particles = useMemo(() => {
        const positions = new Float32Array(count * 3);
        const velocities = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 10;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 5;

            velocities[i * 3] = (Math.random() - 0.5) * 0.01;
            velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.01;
            velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.01;
        }
        return { positions, velocities };
    }, []);

    const pointsRef = useRef<THREE.Points>(null);

    useFrame((state) => {
        if (!pointsRef.current) return;

        const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
        for (let i = 0; i < count; i++) {
            positions[i * 3] += particles.velocities[i * 3];
            positions[i * 3 + 1] += particles.velocities[i * 3 + 1];
            positions[i * 3 + 2] += particles.velocities[i * 3 + 2];

            // Boundary check
            if (Math.abs(positions[i * 3]) > 6) particles.velocities[i * 3] *= -1;
            if (Math.abs(positions[i * 3 + 1]) > 6) particles.velocities[i * 3 + 1] *= -1;
        }
        pointsRef.current.geometry.attributes.position.needsUpdate = true;

        if (groupRef.current) {
            groupRef.current.rotation.y += 0.001;
        }
    });

    return (
        <group ref={groupRef}>
            <points ref={pointsRef}>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={count}
                        array={particles.positions}
                        itemSize={3}
                    />
                </bufferGeometry>
                <pointsMaterial
                    size={0.08}
                    color={active ? "#00f3ff" : "#444"}
                    transparent
                    opacity={0.6}
                    sizeAttenuation
                />
            </points>

            {/* Pulsing Core */}
            <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
                <Sphere args={[0.5, 32, 32]}>
                    <MeshDistortMaterial
                        color={active ? "#bc13fe" : "#222"}
                        speed={2}
                        distort={0.4}
                        radius={1}
                        emissive={active ? "#bc13fe" : "#000"}
                        emissiveIntensity={active ? 2 : 0}
                    />
                </Sphere>
            </Float>
        </group>
    );
}

export const NeuralWeb: React.FC<{ events: HandoverEvent[] }> = ({ events }) => {
    return (
        <div className="relative w-full h-[240px] carbon-panel rounded-xl overflow-hidden mt-4 group">
            {/* Background Three.js Context */}
            <div className="absolute inset-0 z-0 opacity-40 group-hover:opacity-60 transition-opacity duration-1000">
                <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} intensity={1} color="#00f3ff" />
                    <NeuralMesh active={events.length > 0} />
                </Canvas>
            </div>

            {/* Overlay Grid */}
            <div className="absolute inset-0 z-10 pointer-events-none opacity-20"
                style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />

            {/* Content Layer */}
            <div className="relative z-20 p-4 flex flex-col h-full bg-gradient-to-t from-[#050505] via-transparent to-transparent">
                <div className="flex justify-between items-center mb-4 border-b border-white/[0.06] pb-2">
                    <span className="text-[10px] text-cyan-400 uppercase tracking-[0.3em] font-bold sci-fi-text">
                        Neural Synchronizer
                    </span>
                    <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${events.length > 0 ? 'bg-cyan-400 animate-pulse shadow-[0_0_8px_#00f3ff]' : 'bg-white/10'}`} />
                        <span className="text-[8px] text-white/40 uppercase tracking-widest font-mono">
                            {events.length} Handovers Linked
                        </span>
                    </div>
                </div>

                <div className="flex-1 space-y-2 overflow-y-auto scrollbar-thin pr-2">
                    {events.map((event, i) => (
                        <motion.div
                            key={event.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="bg-white/[0.02] border border-white/[0.05] rounded p-2 flex items-center justify-between group/item hover:bg-white/[0.05] transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className="text-[9px] font-mono text-cyan-400/80 bg-cyan-400/5 px-1.5 py-0.5 rounded border border-cyan-400/10">
                                    {event.fromAgent}
                                </div>
                                <div className="w-4 h-px bg-white/10 relative">
                                    <div className="absolute inset-0 bg-cyan-400 scale-x-0 group-hover/item:scale-x-100 transition-transform origin-left duration-500" />
                                </div>
                                <div className="text-[9px] font-mono text-purple-400/80 bg-purple-400/5 px-1.5 py-0.5 rounded border border-purple-400/10">
                                    {event.toAgent}
                                </div>
                            </div>
                            <div className="text-[8px] text-white/30 truncate max-w-[120px] font-mono uppercase tracking-tighter">
                                {event.task}
                            </div>
                        </motion.div>
                    ))}

                    {events.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center opacity-20 mt-4">
                            <div className="text-[9px] font-mono uppercase tracking-[0.2em]">Awaiting Uplink</div>
                            <div className="w-12 h-px bg-gradient-to-r from-transparent via-white to-transparent mt-1" />
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom Accent */}
            <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
        </div>
    );
};
