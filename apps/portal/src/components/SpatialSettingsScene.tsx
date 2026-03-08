'use client';

import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sphere, MeshDistortMaterial, Text, PerspectiveCamera, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { motion, AnimatePresence } from 'framer-motion';

interface SettingNodeProps {
    position: [number, number, number];
    label: string;
    icon: string;
    color: string;
    active: boolean;
    onClick: () => void;
}

const SettingNode: React.FC<SettingNodeProps> = ({ position, label, icon, color, active, onClick }) => {
    const meshRef = useRef<THREE.Mesh>(null);
    const [hovered, setHovered] = useState(false);

    useFrame((state) => {
        if (!meshRef.current) return;
        const t = state.clock.getElapsedTime();
        meshRef.current.position.y = position[1] + Math.sin(t * 1.5 + position[0]) * 0.1;
        meshRef.current.rotation.x = t * 0.2;
        meshRef.current.rotation.z = t * 0.3;
    });

    return (
        <group position={position}>
            <Float speed={2} rotationIntensity={1} floatIntensity={2}>
                <Sphere
                    ref={meshRef}
                    args={[0.6, 64, 64]}
                    onClick={onClick}
                    onPointerEnter={() => setHovered(true)}
                    onPointerLeave={() => setHovered(false)}
                >
                    <MeshDistortMaterial
                        color={active ? color : (hovered ? color : '#333')}
                        speed={3}
                        distort={active ? 0.4 : 0.2}
                        radius={1}
                        emissive={color}
                        emissiveIntensity={active ? 1.5 : (hovered ? 0.8 : 0.2)}
                        metalness={0.9}
                        roughness={0.1}
                    />
                </Sphere>
            </Float>
            <Text
                position={[0, -1.2, 0]}
                fontSize={0.25}
                color="white"
                font="/fonts/Inter-Bold.woff" // Assuming font exists or fallback
                anchorX="center"
                anchorY="middle"
            >
                {label}
            </Text>
            <Text
                position={[0, 0, 0.7]}
                fontSize={0.4}
                color="white"
                anchorX="center"
                anchorY="middle"
            >
                {icon}
            </Text>
        </group>
    );
};

interface SpatialSettingsSceneProps {
    activeTab: string;
    onTabSelect: (tab: any) => void;
}

export const SpatialSettingsScene: React.FC<SpatialSettingsSceneProps> = ({ activeTab, onTabSelect }) => {
    const tabs = [
        { id: 'theme', label: 'Theme', icon: '🎨', color: '#06B6D4', pos: [-2.5, 1, 0] },
        { id: 'agents', label: 'Agents', icon: '🤖', color: '#8B5CF6', pos: [0, 2, -1] },
        { id: 'audio', label: 'Audio', icon: '🔊', color: '#EC4899', pos: [2.5, 1, 0] },
        { id: 'shortcuts', label: 'Keys', icon: '⌨️', color: '#F59E0B', pos: [-1.5, -1.5, 1] },
        { id: 'profile', label: 'User', icon: '👤', color: '#10B981', pos: [1.5, -1.5, 1] },
    ];

    return (
        <div className="w-full h-[60vh] relative bg-black/40 rounded-xl overflow-hidden border border-white/5">
            <Canvas shadows dpr={[1, 2]}>
                <PerspectiveCamera makeDefault position={[0, 0, 7]} fov={50} />
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#06B6D4" />
                <pointLight position={[-10, -10, -10]} intensity={0.5} color="#8B5CF6" />

                <group>
                    {tabs.map((tab) => (
                        <SettingNode
                            key={tab.id}
                            position={tab.pos as any}
                            label={tab.label}
                            icon={tab.icon}
                            color={tab.color}
                            active={activeTab === tab.id}
                            onClick={() => onTabSelect(tab.id)}
                        />
                    ))}
                </group>

                {/* Central Brain Glow */}
                <Sphere args={[0.2, 32, 32]}>
                    <meshStandardMaterial color="#fff" emissive="#fff" emissiveIntensity={2} />
                </Sphere>

                <OrbitControls
                    enableZoom={false}
                    enablePan={false}
                    maxPolarAngle={Math.PI / 1.5}
                    minPolarAngle={Math.PI / 3}
                />
            </Canvas>

            {/* Hint Overlay */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs text-white/40 font-mono pointer-events-none uppercase tracking-widest">
                Drag to orbit • Click nodes to configure
            </div>
        </div>
    );
};
