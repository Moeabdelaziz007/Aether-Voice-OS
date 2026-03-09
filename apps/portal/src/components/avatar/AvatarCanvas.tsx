"use client";

import React from "react";
import { Canvas } from "@react-three/fiber";
import * as THREE from "three";

interface AvatarCanvasProps {
    children: React.ReactNode;
    cameraZ: number;
    dpr?: [number, number];
    bloom?: boolean;
}

/**
 * AvatarCanvas — High-Performance 3D Environment Wrapper
 * 
 * Handles all WebGL/Canvas setup logic, including camera system 
 * and render optimization tokens.
 */
export function AvatarCanvas({
    children,
    cameraZ,
    dpr = [1, 2],
}: AvatarCanvasProps) {
    return (
        <Canvas
            camera={{ position: [0, 0, cameraZ], fov: 45 }}
            gl={{
                antialias: true,
                alpha: true,
                powerPreference: "high-performance",
                toneMapping: THREE.ACESFilmicToneMapping,
                toneMappingExposure: 1.2,
            }}
            dpr={dpr}
            style={{ pointerEvents: "none" }}
        >
            {/* Universal Lighting Environment */}
            <ambientLight intensity={0.1} />
            <pointLight position={[10, 10, 10]} intensity={0.5} color="#39ff14" />
            <pointLight position={[-10, -10, -10]} intensity={0.3} color="#00ff41" />
            <pointLight position={[0, -10, 5]} intensity={0.2} color="#1a5c1a" />

            {children}
        </Canvas>
    );
}
