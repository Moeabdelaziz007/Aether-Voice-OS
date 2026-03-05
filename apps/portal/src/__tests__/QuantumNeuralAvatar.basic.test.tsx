/**
 * QuantumNeuralAvatar Basic Unit Tests
 * 
 * Simplified tests focusing on component structure and props
 */

import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, vi, beforeAll, afterEach } from 'vitest';
import QuantumNeuralAvatar, { 
    AvatarIcon, 
    AvatarSmall, 
    AvatarMedium, 
} from '../components/QuantumNeuralAvatar';
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
    MeshDistortMaterial: vi.fn(),
    Sphere: vi.fn(),
    Trail: vi.fn(),
}));

vi.mock('three', () => ({
    Vector3: vi.fn().mockImplementation((x = 0, y = 0, z = 0) => ({ x, y, z })),
    Color: vi.fn().mockImplementation(() => ({ r: 0, g: 1, b: 0 })),
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
}));

describe('QuantumNeuralAvatar - Basic', () => {
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
        const { container } = render(<QuantumNeuralAvatar />);
        expect(container).toBeTruthy();
    });

    it('renders canvas element', () => {
        const { container } = render(<QuantumNeuralAvatar />);
        expect(container.querySelector('[data-testid="canvas"]')).toBeTruthy();
    });

    it('accepts size prop', () => {
        const { container } = render(<QuantumNeuralAvatar size="small" />);
        expect(container).toBeTruthy();
    });

    it('accepts variant prop', () => {
        const { container } = render(<QuantumNeuralAvatar variant="minimal" />);
        expect(container).toBeTruthy();
    });

    it('exports avatar variants', () => {
        const { container: iconContainer } = render(<AvatarIcon />);
        expect(iconContainer).toBeTruthy();

        const { container: smallContainer } = render(<AvatarSmall />);
        expect(smallContainer).toBeTruthy();

        const { container: mediumContainer } = render(<AvatarMedium />);
        expect(mediumContainer).toBeTruthy();
    });
});
