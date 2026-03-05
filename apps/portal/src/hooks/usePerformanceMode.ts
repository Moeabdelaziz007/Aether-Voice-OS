"use client";
/**
 * usePerformanceMode — Adaptive Quality System
 * 
 * Detects device capabilities and adjusts rendering quality accordingly.
 * Provides quality presets that components can use to optimize their rendering.
 * 
 * Performance tiers:
 * - high: Full effects, max particles, full post-processing
 * - medium: Reduced particles, simplified post-processing
 * - low: Minimal effects, basic rendering for mobile/low-end devices
 */

import { useState, useEffect, useMemo } from "react";

export type QualityTier = "high" | "medium" | "low";

export interface PerformanceConfig {
  quality: QualityTier;
  particleCount: number;
  postProcessingEnabled: boolean;
  bloomEnabled: boolean;
  trailsEnabled: boolean;
  neuralMeshNodes: number;
  dpr: [number, number];
  sparkleCount: number;
}

const QUALITY_PRESETS: Record<QualityTier, PerformanceConfig> = {
  high: {
    quality: "high",
    particleCount: 150,
    postProcessingEnabled: true,
    bloomEnabled: true,
    trailsEnabled: true,
    neuralMeshNodes: 40,
    dpr: [1, 2],
    sparkleCount: 150,
  },
  medium: {
    quality: "medium",
    particleCount: 80,
    postProcessingEnabled: true,
    bloomEnabled: true,
    trailsEnabled: true,
    neuralMeshNodes: 25,
    dpr: [1, 1.5],
    sparkleCount: 100,
  },
  low: {
    quality: "low",
    particleCount: 30,
    postProcessingEnabled: false,
    bloomEnabled: false,
    trailsEnabled: false,
    neuralMeshNodes: 15,
    dpr: [1, 1],
    sparkleCount: 50,
  },
};

/**
 * Detect device GPU tier using various heuristics
 */
function detectGPUTier(): number {
  if (typeof window === "undefined") return 2;
  
  try {
    // Check WebGL capabilities
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
    
    if (!gl) return 0;
    
    // Get renderer info
    const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
    const renderer = debugInfo 
      ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)?.toLowerCase() || ""
      : "";
    
    // High-end GPU keywords
    const highEndPatterns = [
      "nvidia", "rtx", "gtx", "radeon rx", "apple m1", "apple m2", "apple m3"
    ];
    
    // Low-end GPU keywords  
    const lowEndPatterns = [
      "intel", "mesa", "swiftshader", "llvmpipe", "mali", "adreno 5", "powervr"
    ];
    
    // Check renderer against patterns
    if (highEndPatterns.some(p => renderer.includes(p))) return 3;
    if (lowEndPatterns.some(p => renderer.includes(p))) return 1;
    
    // Check device memory (if available)
    const deviceMemory = (navigator as { deviceMemory?: number }).deviceMemory;
    if (deviceMemory !== undefined) {
      if (deviceMemory >= 8) return 3;
      if (deviceMemory <= 2) return 1;
    }
    
    // Check hardware concurrency
    const cores = navigator.hardwareConcurrency || 4;
    if (cores >= 8) return 3;
    if (cores <= 2) return 1;
    
    // Default to medium tier
    return 2;
    
  } catch {
    return 2; // Default to medium on error
  }
}

/**
 * Check if device is mobile
 */
function isMobileDevice(): boolean {
  if (typeof window === "undefined") return false;
  
  const userAgent = navigator.userAgent.toLowerCase();
  const mobileKeywords = ["android", "iphone", "ipad", "ipod", "mobile", "tablet"];
  
  return mobileKeywords.some(keyword => userAgent.includes(keyword)) ||
    ("ontouchstart" in window && navigator.maxTouchPoints > 0);
}

/**
 * Check if device prefers reduced motion
 */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Main hook for adaptive performance configuration
 */
export function usePerformanceMode(): PerformanceConfig {
  const [tier, setTier] = useState<QualityTier>("medium");
  
  useEffect(() => {
    // Detect quality tier on mount
    const gpuTier = detectGPUTier();
    const isMobile = isMobileDevice();
    const reducedMotion = prefersReducedMotion();
    
    let quality: QualityTier;
    
    if (reducedMotion || gpuTier === 0) {
      quality = "low";
    } else if (isMobile || gpuTier === 1) {
      quality = "low";
    } else if (gpuTier >= 3) {
      quality = "high";
    } else {
      quality = "medium";
    }
    
    setTier(quality);
    
    // Log detected quality (dev only)
    if (process.env.NODE_ENV === "development") {
      console.log(`[Performance] GPU Tier: ${gpuTier}, Mobile: ${isMobile}, Quality: ${quality}`);
    }
  }, []);
  
  return useMemo(() => QUALITY_PRESETS[tier], [tier]);
}

/**
 * Hook for manual quality override (for settings panel)
 */
export function useQualityOverride() {
  const [override, setOverride] = useState<QualityTier | null>(null);
  
  const config = usePerformanceMode();
  
  const effectiveConfig = useMemo(() => {
    if (override) {
      return QUALITY_PRESETS[override];
    }
    return config;
  }, [override, config]);
  
  return {
    config: effectiveConfig,
    override,
    setOverride,
  };
}

export { QUALITY_PRESETS };
