/**
 * usePerformanceMonitor Hook
 * 
 * Monitors and tracks performance metrics including:
 * - FPS (frames per second)
 * - Render time
 * - Memory usage
 * - Custom performance events
 */

import { useRef, useEffect, useCallback, useState } from 'react';

export interface PerformanceMetrics {
    fps: number;
    avgFps: number;
    minFps: number;
    maxFps: number;
    renderTime: number;
    avgRenderTime: number;
    memoryUsage?: number;
    frameCount: number;
    timestamp: number;
}

export interface PerformanceThresholds {
    minFps: number;
    maxRenderTime: number;
    maxMemoryMB: number;
}

const DEFAULT_THRESHOLDS: PerformanceThresholds = {
    minFps: 30,
    maxRenderTime: 16.67, // ~60fps
    maxMemoryMB: 512,
};

const FPS_SAMPLE_SIZE = 60;

export default function usePerformanceMonitor(
    enabled: boolean = true,
    thresholds: PerformanceThresholds = DEFAULT_THRESHOLDS
) {
    const [metrics, setMetrics] = useState<PerformanceMetrics>({
        fps: 60,
        avgFps: 60,
        minFps: 60,
        maxFps: 60,
        renderTime: 0,
        avgRenderTime: 0,
        frameCount: 0,
        timestamp: Date.now(),
    });

    const [isPerformanceGood, setIsPerformanceGood] = useState(true);
    
    const frameTimesRef = useRef<number[]>([]);
    const lastTimeRef = useRef<number>(0);
    const frameCountRef = useRef(0);
    const animationFrameRef = useRef<number | null>(null);
    const fpsHistoryRef = useRef<number[]>([]);

    const calculateMetrics = useCallback((deltaTime: number): PerformanceMetrics => {
        const fps = 1000 / deltaTime;
        const renderTime = deltaTime;

        // Update FPS history
        fpsHistoryRef.current.push(fps);
        if (fpsHistoryRef.current.length > FPS_SAMPLE_SIZE) {
            fpsHistoryRef.current.shift();
        }

        // Calculate averages
        const avgFps = fpsHistoryRef.current.reduce((a, b) => a + b, 0) / fpsHistoryRef.current.length;
        const minFps = Math.min(...fpsHistoryRef.current);
        const maxFps = Math.max(...fpsHistoryRef.current);
        const avgRenderTime = renderTime;

        // Get memory usage if available
        let memoryUsage: number | undefined;
        if ('memory' in performance) {
            const mem = (performance as any).memory;
            memoryUsage = mem.usedJSHeapSize / (1024 * 1024); // Convert to MB
        }

        return {
            fps: Math.round(fps),
            avgFps: Math.round(avgFps),
            minFps: Math.round(minFps),
            maxFps: Math.round(maxFps),
            renderTime: Math.round(renderTime * 100) / 100,
            avgRenderTime: Math.round(avgRenderTime * 100) / 100,
            memoryUsage,
            frameCount: frameCountRef.current,
            timestamp: Date.now(),
        };
    }, []);

    const measurePerformance = useCallback(() => {
        const now = performance.now();
        const deltaTime = lastTimeRef.current ? now - lastTimeRef.current : 16.67;
        lastTimeRef.current = now;
        frameCountRef.current++;

        const newMetrics = calculateMetrics(deltaTime);
        setMetrics(newMetrics);

        // Check performance thresholds
        const isGood = 
            newMetrics.fps >= thresholds.minFps &&
            newMetrics.renderTime <= thresholds.maxRenderTime &&
            (newMetrics.memoryUsage ? newMetrics.memoryUsage <= thresholds.maxMemoryMB : true);
        
        setIsPerformanceGood(isGood);

        if (enabled) {
            animationFrameRef.current = requestAnimationFrame(measurePerformance);
        }
    }, [enabled, thresholds, calculateMetrics]);

    useEffect(() => {
        if (enabled) {
            lastTimeRef.current = performance.now();
            animationFrameRef.current = requestAnimationFrame(measurePerformance);
        }

        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, [enabled, measurePerformance]);

    const getPerformanceLevel = useCallback((): 'excellent' | 'good' | 'fair' | 'poor' => {
        if (metrics.fps >= 55 && metrics.renderTime < 10) return 'excellent';
        if (metrics.fps >= 45 && metrics.renderTime < 14) return 'good';
        if (metrics.fps >= 30 && metrics.renderTime < 20) return 'fair';
        return 'poor';
    }, [metrics]);

    const resetMetrics = useCallback(() => {
        fpsHistoryRef.current = [];
        frameTimesRef.current = [];
        frameCountRef.current = 0;
        setMetrics({
            fps: 60,
            avgFps: 60,
            minFps: 60,
            maxFps: 60,
            renderTime: 0,
            avgRenderTime: 0,
            frameCount: 0,
            timestamp: Date.now(),
        });
    }, []);

    return {
        metrics,
        isPerformanceGood,
        performanceLevel: getPerformanceLevel(),
        resetMetrics,
    };
}
