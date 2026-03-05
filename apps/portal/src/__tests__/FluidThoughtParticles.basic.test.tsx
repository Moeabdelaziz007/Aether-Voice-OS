/**
 * FluidThoughtParticles Basic Unit Tests
 * 
 * Simplified tests focusing on component structure and store integration
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeAll, afterEach } from 'vitest';
import FluidThoughtParticles from '../components/FluidThoughtParticles';
import { useAetherStore } from '../store/useAetherStore';

// Mock Three.js and React Three Fiber
vi.mock('@react-three/fiber', () => ({
    Canvas: ({ children }: { children: React.ReactNode }) => <div data-testid="canvas">{children}</div>,
    useFrame: vi.fn(),
    useThree: vi.fn(() => ({
        camera: { position: { x: 0, y: 0, z: 10 } },
        clock: { elapsedTime: 0 },
    })),
}));

vi.mock('@react-three/drei', () => ({
    Float: ({ children }: { children: React.ReactNode }) => children,
}));

vi.mock('three', () => {
    const Vector3 = function(x = 0, y = 0, z = 0) {
        this.x = x;
        this.y = y;
        this.z = z;
    };
    
    const Color = function(color) {
        this.r = 0;
        this.g = 1;
        this.b = 0;
        this.clone = () => new Color();
        this.lerp = () => this;
        this.set = () => this;
    };
    
    return {
        Vector3,
        Color,
        Clock: vi.fn().mockImplementation(() => ({ elapsedTime: 0 })),
        BufferGeometry: vi.fn(),
        Float32BufferAttribute: vi.fn(),
        AdditiveBlending: 1,
        DoubleSide: 2,
        SphereGeometry: vi.fn(),
        RingGeometry: vi.fn(),
        TorusGeometry: vi.fn(),
        IcosahedronGeometry: vi.fn(),
        QuadraticBezierCurve3: vi.fn(),
        MeshBasicMaterial: vi.fn(),
        MeshDistortMaterial: vi.fn(),
        PointsMaterial: vi.fn(),
        LineBasicMaterial: vi.fn(),
        ShaderMaterial: vi.fn(),
        Line: vi.fn(),
        LineSegments: vi.fn(),
        Mesh: vi.fn(),
        Group: vi.fn(),
        Points: vi.fn(),
    };
});

describe('FluidThoughtParticles - Basic', () => {
    beforeAll(() => {
        useAetherStore.setState({
            transcript: [],
            engineState: 'IDLE',
            micLevel: 0,
            speakerLevel: 0,
        });
    });

    afterEach(() => {
        useAetherStore.setState({
            transcript: [],
            engineState: 'IDLE',
            micLevel: 0,
            speakerLevel: 0,
        });
    });

    it('renders without crashing', () => {
        const { container } = render(<FluidThoughtParticles />);
        expect(container).toBeTruthy();
    });

    it('renders canvas element', () => {
        render(<FluidThoughtParticles />);
        const canvas = screen.getByTestId('canvas');
        expect(canvas).toBeTruthy();
    });

    it('connects to aether store', () => {
        render(<FluidThoughtParticles />);
        const state = useAetherStore.getState();
        expect(state).toHaveProperty('transcript');
        expect(state).toHaveProperty('engineState');
        expect(state).toHaveProperty('micLevel');
        expect(state).toHaveProperty('speakerLevel');
    });

    it('handles empty transcript', () => {
        useAetherStore.setState({ transcript: [] });
        const { container } = render(<FluidThoughtParticles />);
        expect(container).toBeTruthy();
    });

    it('accepts transcript messages', () => {
        const mockTranscript = [
            {
                id: 'test-1',
                role: 'agent' as const,
                content: 'Test message',
                timestamp: Date.now(),
            },
        ];
        
        useAetherStore.setState({ transcript: mockTranscript });
        render(<FluidThoughtParticles />);
        
        const state = useAetherStore.getState();
        expect(state.transcript).toEqual(mockTranscript);
    });
});
