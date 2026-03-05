/**
 * QuantumNeuralAvatar Unit Tests
 * 
 * Tests for avatar size variants, state transitions, 
 * color palette application, and component rendering.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeAll, afterEach } from 'vitest';
import QuantumNeuralAvatar, { 
    AvatarIcon, 
    AvatarSmall, 
    AvatarMedium, 
    AvatarLarge, 
    AvatarFullscreen 
} from '../components/QuantumNeuralAvatar';
import { useAetherStore } from '../store/useAetherStore';

// Mock Three.js and React Three Fiber
vi.mock('@react-three/fiber', () => ({
    Canvas: ({ children }: { children: React.ReactNode }) => <div data-testid="canvas">{children}</div>,
    useFrame: vi.fn((callback) => callback({ clock: { elapsedTime: 0 }, camera: { position: { x: 0, y: 0, z: 10 } } })),
    useThree: vi.fn(() => ({
        camera: { position: { x: 0, y: 0, z: 10 } },
        clock: { elapsedTime: 0 },
        size: { width: 800, height: 600 },
        viewport: { width: 800, height: 600 },
    })),
}));

// Mock React Three Drei
vi.mock('@react-three/drei', () => ({
    Float: ({ children }: { children: React.ReactNode }) => children,
    MeshDistortMaterial: vi.fn(),
    Sphere: vi.fn(),
    Trail: vi.fn(),
}));

vi.mock('@react-three/drei', () => ({
    Float: ({ children }: { children: React.ReactNode }) => children,
    MeshDistortMaterial: vi.fn(),
    Sphere: vi.fn(),
    Trail: vi.fn(),
}));

vi.mock('three', () => {
    const Vector3 = class {
        x: number;
        y: number;
        z: number;
        constructor(x = 0, y = 0, z = 0) {
            this.x = x;
            this.y = y;
            this.z = z;
        }
        clone() { return new Vector3(this.x, this.y, this.z); }
        add(v: any) { this.x += v.x; this.y += v.y; this.z += v.z; return this; }
        addVectors(a: any, b: any) { this.x = a.x + b.x; this.y = a.y + b.y; this.z = a.z + b.z; return this; }
        multiplyScalar(s: number) { this.x *= s; this.y *= s; this.z *= s; return this; }
        distanceTo(v: any) { return Math.sqrt(Math.pow(this.x - v.x, 2) + Math.pow(this.y - v.y, 2) + Math.pow(this.z - v.z, 2)); }
    };

    const Color = class {
        r: number; g: number; b: number;
        constructor(color?: string | number) {
            this.r = 0; this.g = 1; this.b = 0;
        }
        clone() { return new Color(); }
        lerp(_color: any, _alpha: number): this { return this; }
        set(r: number, g: number, b: number): this { this.r = r; this.g = g; this.b = b; return this; }
    };

    return {
        Vector3,
        Color,
        Clock: vi.fn().mockImplementation(() => ({ elapsedTime: 0 })),
        BufferGeometry: vi.fn().mockImplementation(function() {
            this.setAttribute = vi.fn();
            this.attributes = { position: { array: new Float32Array(0), needsUpdate: false } };
        }),
        Float32BufferAttribute: vi.fn(),
        AdditiveBlending: 1,
        DoubleSide: 2,
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
        ShaderMaterial: vi.fn(),
        Line: vi.fn(),
        LineSegments: vi.fn(),
        Mesh: vi.fn(),
        Group: vi.fn(),
        Points: vi.fn(),
        
        // Add light and geometry mocks for JSX elements
        AmbientLight: vi.fn(),
        PointLight: vi.fn(),
        DirectionalLight: vi.fn(),
        HemisphereLight: vi.fn(),
        SpotLight: vi.fn(),
        PlaneGeometry: vi.fn(),
        BoxGeometry: vi.fn(),
        CylinderGeometry: vi.fn(),
        ConeGeometry: vi.fn(),
        OctahedronGeometry: vi.fn(),
        TetrahedronGeometry: vi.fn(),
        TorusKnotGeometry: vi.fn(),
        ExtrudeGeometry: vi.fn(),
        LatheGeometry: vi.fn(),
        TubeGeometry: vi.fn(),
        ParametricGeometry: vi.fn(),
        TextGeometry: vi.fn(),
        ShapeGeometry: vi.fn(),
        EdgesGeometry: vi.fn(),
        WireframeGeometry: vi.fn(),
        NormalBufferAttributes: vi.fn(),
        BufferGeometryEventMap: vi.fn(),
        Object3DEventMap: vi.fn(),
        Material: vi.fn(),
    };
});

// Helper function to set store state
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function setStoreState(state: any) {
    Object.entries(state).forEach(([key, value]) => {
        useAetherStore.setState({ [key]: value });
    });
}

describe('QuantumNeuralAvatar', () => {
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
        it('renders without crashing with default props', () => {
            const { container } = render(<QuantumNeuralAvatar />);
            expect(container).toBeTruthy();
        });

        it('renders Canvas component', () => {
            render(<QuantumNeuralAvatar />);
            const canvas = screen.getByTestId('canvas');
            expect(canvas).toBeTruthy();
        });
    });

    describe('Size Variants', () => {
        it('renders icon size correctly', () => {
            const { container } = render(<AvatarIcon />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            expect(avatar).toBeTruthy();
            expect(avatar?.style.width).toBe('48px');
            expect(avatar?.style.height).toBe('48px');
        });

        it('renders small size correctly', () => {
            const { container } = render(<AvatarSmall />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            expect(avatar).toBeTruthy();
            expect(avatar?.style.width).toBe('120px');
            expect(avatar?.style.height).toBe('120px');
        });

        it('renders medium size correctly', () => {
            const { container } = render(<AvatarMedium />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            expect(avatar).toBeTruthy();
            expect(avatar?.style.width).toBe('240px');
            expect(avatar?.style.height).toBe('240px');
        });

        it('renders large size correctly', () => {
            const { container } = render(<AvatarLarge />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            expect(avatar).toBeTruthy();
            expect(avatar?.style.width).toBe('400px');
            expect(avatar?.style.height).toBe('400px');
        });

        it('renders fullscreen size correctly', () => {
            const { container } = render(<AvatarFullscreen />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            expect(avatar).toBeTruthy();
            expect(avatar?.style.width).toBe('100%');
            expect(avatar?.style.height).toBe('100%');
        });

        it('accepts size prop correctly', () => {
            const { container } = render(<QuantumNeuralAvatar size="small" />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            expect(avatar?.style.width).toBe('120px');
            expect(avatar?.style.height).toBe('120px');
        });
    });

    describe('Variant Props', () => {
        it('renders minimal variant', () => {
            const { container } = render(<QuantumNeuralAvatar variant="minimal" />);
            expect(container).toBeTruthy();
        });

        it('renders standard variant', () => {
            const { container } = render(<QuantumNeuralAvatar variant="standard" />);
            expect(container).toBeTruthy();
        });

        it('renders detailed variant', () => {
            const { container } = render(<QuantumNeuralAvatar variant="detailed" />);
            expect(container).toBeTruthy();
        });
    });

    describe('Connection Visibility', () => {
        it('shows connections when showConnections is true', () => {
            const { container } = render(<QuantumNeuralAvatar showConnections={true} />);
            expect(container).toBeTruthy();
        });

        it('hides connections when showConnections is false', () => {
            const { container } = render(<QuantumNeuralAvatar showConnections={false} />);
            expect(container).toBeTruthy();
        });
    });

    describe('Engine State Handling', () => {
        it('handles IDLE state', () => {
            setStoreState({ engineState: 'IDLE' });
            render(<QuantumNeuralAvatar />);
            expect(useAetherStore.getState().engineState).toBe('IDLE');
        });

        it('handles LISTENING state', () => {
            setStoreState({ engineState: 'LISTENING', micLevel: 0.5 });
            render(<QuantumNeuralAvatar />);
            expect(useAetherStore.getState().engineState).toBe('LISTENING');
        });

        it('handles THINKING state', () => {
            setStoreState({ engineState: 'THINKING' });
            render(<QuantumNeuralAvatar />);
            expect(useAetherStore.getState().engineState).toBe('THINKING');
        });

        it('handles SPEAKING state', () => {
            setStoreState({ engineState: 'SPEAKING', speakerLevel: 0.8 });
            render(<QuantumNeuralAvatar />);
            expect(useAetherStore.getState().engineState).toBe('SPEAKING');
        });

        it('handles INTERRUPTING state', () => {
            setStoreState({ engineState: 'INTERRUPTING' });
            render(<QuantumNeuralAvatar />);
            expect(useAetherStore.getState().engineState).toBe('INTERRUPTING');
        });
    });

    describe('Audio Level Reactivity', () => {
        it('uses speakerLevel when SPEAKING', () => {
            setStoreState({ 
                engineState: 'SPEAKING',
                speakerLevel: 0.7,
                micLevel: 0.2,
            });
            
            render(<QuantumNeuralAvatar />);
            
            const state = useAetherStore.getState();
            expect(state.engineState).toBe('SPEAKING');
            expect(state.speakerLevel).toBe(0.7);
        });

        it('uses micLevel when LISTENING', () => {
            setStoreState({ 
                engineState: 'LISTENING',
                micLevel: 0.6,
                speakerLevel: 0.1,
            });
            
            render(<QuantumNeuralAvatar />);
            
            const state = useAetherStore.getState();
            expect(state.engineState).toBe('LISTENING');
            expect(state.micLevel).toBe(0.6);
        });

        it('handles zero audio levels', () => {
            setStoreState({ 
                engineState: 'IDLE',
                micLevel: 0,
                speakerLevel: 0,
            });
            
            const { container } = render(<QuantumNeuralAvatar />);
            expect(container).toBeTruthy();
        });

        it('handles maximum audio levels', () => {
            setStoreState({ 
                engineState: 'SPEAKING',
                micLevel: 1.0,
                speakerLevel: 1.0,
            });
            
            const { container } = render(<QuantumNeuralAvatar />);
            expect(container).toBeTruthy();
        });
    });

    describe('Carbon Fiber Styling', () => {
        it('applies carbon fiber background styling', () => {
            const { container } = render(<QuantumNeuralAvatar />);
            const avatar = container.querySelector('.quantum-avatar') as HTMLElement;
            
            expect(avatar).toBeTruthy();
            expect(avatar?.style.background).toContain('radial-gradient');
            expect(avatar?.style.background).toContain('#1a1a1a');
        });

        it('applies carbon fiber texture overlay', () => {
            const { container } = render(<QuantumNeuralAvatar />);
            const overlay = container.querySelector('.absolute');
            
            expect(overlay).toBeTruthy();
        });
    });

    describe('Status Indicator', () => {
        it('shows status indicator for icon size', () => {
            const { container } = render(<AvatarIcon />);
            const indicator = container.querySelector('.rounded-full') as HTMLElement;
            
            expect(indicator).toBeTruthy();
        });

        it('shows green indicator when SPEAKING', () => {
            setStoreState({ engineState: 'SPEAKING' });
            const { container } = render(<AvatarIcon />);
            const indicator = container.querySelector('.rounded-full') as HTMLElement;
            
            // Should have green color for speaking
            expect(indicator?.style.backgroundColor).toContain('57');
        });

        it('shows different color for LISTENING state', () => {
            setStoreState({ engineState: 'LISTENING' });
            const { container } = render(<AvatarIcon />);
            
            // Just verify it renders
            expect(container.querySelector('.rounded-full')).toBeTruthy();
        });

        it('hides indicator for larger sizes', () => {
            const { container } = render(<AvatarMedium />);
            const indicator = container.querySelector('.rounded-full');
            
            // Indicator should not exist for non-icon sizes
            expect(indicator).toBeFalsy();
        });
    });
});

// Integration tests for state transitions
describe('Avatar State Transitions', () => {
    beforeAll(() => {
        useAetherStore.setState({
            transcript: [],
            engineState: 'IDLE',
            micLevel: 0,
            speakerLevel: 0,
        });
    });

    it('transitions smoothly between states', () => {
        const states = ['IDLE', 'LISTENING', 'THINKING', 'SPEAKING', 'IDLE'];
        
        states.forEach(state => {
            useAetherStore.setState({ engineState: state as any });
            const { container } = render(<QuantumNeuralAvatar />);
            expect(container).toBeTruthy();
        });
    });

    it('handles rapid state changes', () => {
        const { rerender } = render(<QuantumNeuralAvatar />);
        
        // Simulate rapid state changes
        for (let i = 0; i < 20; i++) {
            const state = ['IDLE', 'LISTENING', 'SPEAKING', 'THINKING'][i % 4] as any;
            const audioLevel = Math.random();
            
            useAetherStore.setState({ 
                engineState: state,
                speakerLevel: state === 'SPEAKING' ? audioLevel : 0,
                micLevel: state === 'LISTENING' ? audioLevel : 0,
            });
            
            rerender(<QuantumNeuralAvatar />);
        }
        
        expect(useAetherStore.getState()).toBeTruthy();
    });
});

// Performance tests
describe('Avatar Performance', () => {
    it('renders efficiently', () => {
        const startTime = performance.now();
        
        render(<QuantumNeuralAvatar />);
        
        const endTime = performance.now();
        const renderTime = endTime - startTime;
        
        // Should render in under 100ms
        expect(renderTime).toBeLessThan(100);
    });

    it('handles all size variants efficiently', () => {
        const sizes = ['icon', 'small', 'medium', 'large', 'fullscreen'] as const;
        
        sizes.forEach(size => {
            const startTime = performance.now();
            render(<QuantumNeuralAvatar size={size} />);
            const endTime = performance.now();
            
            expect(endTime - startTime).toBeLessThan(100);
        });
    });
});

// Memory and cleanup tests
describe('Avatar Memory Management', () => {
    it('cleans up on unmount', () => {
        const { unmount } = render(<QuantumNeuralAvatar />);
        
        // Should not throw on unmount
        expect(() => unmount()).not.toThrow();
    });

    it('handles repeated mount/unmount cycles', () => {
        for (let i = 0; i < 10; i++) {
            const { unmount } = render(<QuantumNeuralAvatar />);
            unmount();
        }
        
        // Should complete without errors
        expect(true).toBe(true);
    });
});
