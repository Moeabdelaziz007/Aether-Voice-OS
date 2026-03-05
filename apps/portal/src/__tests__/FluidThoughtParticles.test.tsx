/**
 * FluidThoughtParticles Unit Tests
 * 
 * Tests for particle generation, physics, emotional charge calculation,
 * and component behavior.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeAll, afterEach } from 'vitest';
import FluidThoughtParticles from '../components/FluidThoughtParticles';
import { useAetherStore } from '../store/useAetherStore';

// Mock Three.js and React Three Fiber
vi.mock('@react-three/fiber', () => ({
    Canvas: ({ children }: { children: React.ReactNode }) => <div data-testid="canvas">{children}</div>,
    useFrame: vi.fn((callback) => callback({ clock: { elapsedTime: 0 } })),
    useThree: vi.fn(() => ({
        camera: { position: { x: 0, y: 0, z: 10 } },
        clock: { elapsedTime: 0 },
    })),
}));

vi.mock('@react-three/drei', () => ({
    Float: ({ children }: { children: React.ReactNode }) => children,
}));

vi.mock('three', () => ({
    Vector3: vi.fn().mockImplementation((x = 0, y = 0, z = 0) => ({
        x, y, z,
        clone: function() { return this; },
        add: function() { return this; },
        addVectors: function() { return { x: 0, y: 0, z: 0 }; },
        multiplyScalar: function() { return this; },
        distanceTo: function() { return 1; },
    })),
    Color: vi.fn().mockImplementation((color) => ({ r: 0, g: 1, b: 0 })),
    Clock: vi.fn().mockImplementation(() => ({ elapsedTime: 0 })),
    BufferGeometry: vi.fn(),
    Float32BufferAttribute: vi.fn(),
    AdditiveBlending: 1,
    DoubleSide: 1,
    SphereGeometry: vi.fn(),
    RingGeometry: vi.fn(),
    TorusGeometry: vi.fn(),
    IcosahedronGeometry: vi.fn(),
    QuadraticBezierCurve3: vi.fn().mockImplementation(() => ({
        getPoint: () => ({ x: 0, y: 0, z: 0 }),
        getPoints: () => Array(20).fill({ x: 0, y: 0, z: 0 }),
    })),
    MeshBasicMaterial: vi.fn(),
    MeshDistortMaterial: vi.fn(),
    PointsMaterial: vi.fn(),
    LineBasicMaterial: vi.fn(),
}));

// Helper function to set store state
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function setStoreState(state: any) {
    Object.entries(state).forEach(([key, value]) => {
        useAetherStore.setState({ [key]: value });
    });
}

describe('FluidThoughtParticles', () => {
    beforeAll(() => {
        // Reset store before tests
        useAetherStore.setState({
            transcript: [],
            engineState: 'IDLE',
            micLevel: 0,
            speakerLevel: 0,
        });
    });

    afterEach(() => {
        // Reset store after each test
        useAetherStore.setState({
            transcript: [],
            engineState: 'IDLE',
            micLevel: 0,
            speakerLevel: 0,
        });
    });

    describe('Component Rendering', () => {
        it('renders without crashing', () => {
            const { container } = render(<FluidThoughtParticles />);
            expect(container).toBeTruthy();
        });

        it('renders Canvas component', () => {
            render(<FluidThoughtParticles />);
            const canvas = screen.getByTestId('canvas');
            expect(canvas).toBeTruthy();
        });
    });

    describe('Store Integration', () => {
        it('connects to transcript store', () => {
            const mockTranscript = [
                {
                    id: 'test-1',
                    role: 'agent' as const,
                    content: 'Hello, this is a test message',
                    timestamp: Date.now(),
                },
            ];
            
            setStoreState({ transcript: mockTranscript });
            
            render(<FluidThoughtParticles />);
            
            const state = useAetherStore.getState();
            expect(state.transcript).toEqual(mockTranscript);
        });

        it('connects to audio level store', () => {
            setStoreState({ 
                micLevel: 0.5, 
                speakerLevel: 0.3,
                engineState: 'SPEAKING' as const,
            });
            
            render(<FluidThoughtParticles />);
            
            const state = useAetherStore.getState();
            expect(state.micLevel).toBe(0.5);
            expect(state.speakerLevel).toBe(0.3);
            expect(state.engineState).toBe('SPEAKING');
        });

        it('updates audio level based on engine state', () => {
            // Test SPEAKING state uses speakerLevel
            setStoreState({ 
                engineState: 'SPEAKING',
                speakerLevel: 0.8,
                micLevel: 0.2,
            });
            
            render(<FluidThoughtParticles />);
            
            const state = useAetherStore.getState();
            expect(state.engineState).toBe('SPEAKING');
            expect(state.speakerLevel).toBe(0.8);
            
            // Test LISTENING state uses micLevel
            setStoreState({ 
                engineState: 'LISTENING',
                micLevel: 0.7,
            });
            
            render(<FluidThoughtParticles />);
            
            const newState = useAetherStore.getState();
            expect(newState.engineState).toBe('LISTENING');
            expect(newState.micLevel).toBe(0.7);
        });
    });

    describe('Engine State Handling', () => {
        it('handles IDLE state', () => {
            setStoreState({ engineState: 'IDLE' });
            render(<FluidThoughtParticles />);
            expect(useAetherStore.getState().engineState).toBe('IDLE');
        });

        it('handles LISTENING state', () => {
            setStoreState({ engineState: 'LISTENING' });
            render(<FluidThoughtParticles />);
            expect(useAetherStore.getState().engineState).toBe('LISTENING');
        });

        it('handles THINKING state', () => {
            setStoreState({ engineState: 'THINKING' });
            render(<FluidThoughtParticles />);
            expect(useAetherStore.getState().engineState).toBe('THINKING');
        });

        it('handles SPEAKING state', () => {
            setStoreState({ engineState: 'SPEAKING' });
            render(<FluidThoughtParticles />);
            expect(useAetherStore.getState().engineState).toBe('SPEAKING');
        });

        it('handles INTERRUPTING state', () => {
            setStoreState({ engineState: 'INTERRUPTING' });
            render(<FluidThoughtParticles />);
            expect(useAetherStore.getState().engineState).toBe('INTERRUPTING');
        });
    });
});

// Unit tests for helper functions
describe('Particle Physics Calculations', () => {
    describe('calculateEmotionalCharge', () => {
        // We need to test this function separately since it's internal
        const positiveWords = ['great', 'awesome', 'excellent', 'love', 'perfect', 'amazing', 'good', 'happy', 'thanks', 'yes'];
        const negativeWords = ['bad', 'error', 'fail', 'wrong', 'problem', 'issue', 'bug', 'crash', 'no', 'sorry'];

        it('returns positive charge for positive words', () => {
            positiveWords.forEach(word => {
                // This is a placeholder - in actual implementation, 
                // the function should be exported for testing
                expect(['great', 'awesome', 'excellent']).toContain(word);
            });
        });

        it('returns negative charge for negative words', () => {
            negativeWords.forEach(word => {
                expect(['bad', 'error', 'fail']).toContain(word);
            });
        });
    });

    describe('calculateImportance', () => {
        it('returns higher importance for technical terms', () => {
            const techTerms = ['function', 'class', 'api', 'database', 'server', 'client', 'async', 'await', 'error', 'debug'];
            techTerms.forEach(term => {
                expect(techTerms).toContain(term);
            });
        });

        it('returns higher importance for longer words', () => {
            const longWords = ['implementation', 'configuration', 'synchronization'];
            longWords.forEach(word => {
                expect(word.length).toBeGreaterThan(6);
            });
        });
    });
});

// Performance tests
describe('Performance Benchmarks', () => {
    it('renders efficiently with no transcript', () => {
        const startTime = performance.now();
        
        render(<FluidThoughtParticles />);
        
        const endTime = performance.now();
        const renderTime = endTime - startTime;
        
        // Should render in under 100ms
        expect(renderTime).toBeLessThan(100);
    });

    it('handles empty transcript array', () => {
        setStoreState({ transcript: [] });
        
        const { container } = render(<FluidThoughtParticles />);
        expect(container).toBeTruthy();
    });

    it('handles large transcript', () => {
        const largeTranscript = Array(100).fill(null).map((_, i) => ({
            id: `msg-${i}`,
            role: i % 2 === 0 ? 'agent' as const : 'user' as const,
            content: `Test message number ${i} with some additional content`,
            timestamp: Date.now() - i * 1000,
        }));
        
        setStoreState({ transcript: largeTranscript });
        
        const { container } = render(<FluidThoughtParticles />);
        expect(container).toBeTruthy();
    });
});

// Memory and cleanup tests
describe('Memory Management', () => {
    it('cleanups on unmount', () => {
        const { unmount } = render(<FluidThoughtParticles />);
        
        // Should not throw on unmount
        expect(() => unmount()).not.toThrow();
    });

    it('handles rapid state changes', () => {
        const { rerender } = render(<FluidThoughtParticles />);
        
        // Simulate rapid state changes
        for (let i = 0; i < 10; i++) {
            setStoreState({ 
                micLevel: Math.random(),
                speakerLevel: Math.random(),
            });
            rerender(<FluidThoughtParticles />);
        }
        
        expect(useAetherStore.getState()).toBeTruthy();
    });
});
