/**
 * Test Audio Generator
 * 
 * Utility for generating synthetic audio data during testing.
 * Mocks Web Audio API and generates synthetic audio levels.
 */

import { vi } from 'vitest';

// Mock AudioContext for testing
export class MockAudioContext {
    sampleRate = 44100;
    currentTime = 0;
    state = 'running';
    
    createGain() {
        return {
            gain: { value: 1 },
            connect: vi.fn(),
            disconnect: vi.fn(),
        };
    }
    
    createAnalyser() {
        return {
            fftSize: 256,
            frequencyBinCount: 128,
            getByteFrequencyData: vi.fn(),
            getByteTimeDomainData: vi.fn(),
        };
    }
    
    createOscillator() {
        return {
            type: 'sine',
            frequency: { value: 440 },
            start: vi.fn(),
            stop: vi.fn(),
            connect: vi.fn(),
            disconnect: vi.fn(),
        };
    }
    
    createPanner() {
        return {
            panningModel: 'HRTF',
            setPosition: vi.fn(),
            connect: vi.fn(),
            disconnect: vi.fn(),
        };
    }
    
    close() {
        return Promise.resolve();
    }
    
    suspend() {
        return Promise.resolve();
    }
    
    resume() {
        return Promise.resolve();
    }
}

// Generate synthetic audio level (0-1)
export function generateAudioLevel(smoothness: number = 0.1): number {
    return Math.random();
}

// Generate smooth audio level with easing
export function generateSmoothAudioLevel(
    currentLevel: number,
    targetLevel: number,
    smoothing: number = 0.1
): number {
    return currentLevel + (targetLevel - currentLevel) * smoothing;
}

// Generate audio waveform data
export function generateWaveformData(length: number = 256): Float32Array {
    const data = new Float32Array(length);
    for (let i = 0; i < length; i++) {
        data[i] = Math.sin(i * 0.1) * 0.5 + (Math.random() - 0.5) * 0.3;
    }
    return data;
}

// Generate frequency data
export function generateFrequencyData(length: number = 128): Uint8Array {
    const data = new Uint8Array(length);
    for (let i = 0; i < length; i++) {
        // Simulate frequency spectrum with decay
        const value = Math.max(0, 255 - i * 2 + Math.random() * 50);
        data[i] = Math.floor(value);
    }
    return data;
}

// Simulate transcript messages for testing
export interface MockTranscriptMessage {
    id: string;
    role: 'user' | 'agent';
    content: string;
    timestamp: number;
}

export function createMockTranscript(
    count: number = 5,
    options: { role?: 'user' | 'agent'; content?: string } = {}
): MockTranscriptMessage[] {
    const { role = 'agent', content = 'This is a test message for the neural voice interface.' } = options;
    
    return Array.from({ length: count }, (_, i) => ({
        id: `msg-${i}-${Date.now()}`,
        role: i % 2 === 0 ? role : (role === 'user' ? 'agent' : 'user'),
        content: `${content} ${i}`,
        timestamp: Date.now() - (count - i) * 1000,
    }));
}

// Generate random particle positions for testing
export function generateParticlePositions(count: number = 100): Float32Array {
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 10;     // x
        positions[i + 1] = (Math.random() - 0.5) * 10; // y
        positions[i + 2] = (Math.random() - 0.5) * 10; // z
    }
    return positions;
}

// Mock Three.js objects for testing
export const mockThreeObjects = {
    Vector3: vi.fn().mockImplementation((x = 0, y = 0, z = 0) => ({ x, y, z })),
    Color: vi.fn().mockImplementation((color) => ({ r: 0, g: 1, b: 0, set: vi.fn() })),
    Mesh: vi.fn().mockImplementation(() => ({
        position: { x: 0, y: 0, z: 0 },
        scale: { x: 1, y: 1, z: 1 },
        rotation: { x: 0, y: 0, z: 0 },
    })),
    SphereGeometry: vi.fn(),
    BufferGeometry: vi.fn().mockImplementation(() => ({
        setAttribute: vi.fn(),
    })),
};

// Create mock store state for testing
export function createMockStoreState(overrides: Record<string, any> = {}) {
    return {
        transcript: [],
        engineState: 'IDLE' as const,
        micLevel: 0,
        speakerLevel: 0,
        preferences: {
            accentColor: 'green' as const,
            waveStyle: 'helix' as const,
            transcriptMode: 'persistent' as const,
        },
        ...overrides,
    };
}

// Simulate audio level changes over time
export class AudioLevelSimulator {
    private currentLevel: number = 0;
    private targetLevel: number = 0;
    private smoothing: number = 0.1;
    
    constructor(smoothing: number = 0.1) {
        this.smoothing = smoothing;
    }
    
    setTarget(level: number): void {
        this.targetLevel = Math.max(0, Math.min(1, level));
    }
    
    update(): number {
        this.currentLevel += (this.targetLevel - this.currentLevel) * this.smoothing;
        return this.currentLevel;
    }
    
    getCurrent(): number {
        return this.currentLevel;
    }
    
    reset(): void {
        this.currentLevel = 0;
        this.targetLevel = 0;
    }
}
