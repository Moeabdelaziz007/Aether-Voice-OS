import React from 'react';
import { render, screen } from '@testing-library/react';
import QuantumNeuralAvatar from '../components/QuantumNeuralAvatar';
import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest';
import { useAetherStore } from '@/store/useAetherStore';

// Mock the child components that use WebGL/Three.js to avoid JSDOM limitations
vi.mock('../components/avatar/AvatarCanvas', () => ({
    AvatarCanvas: ({ children }: { children: React.ReactNode }) => <div data-testid="avatar-canvas">{children}</div>
}));

vi.mock('../components/QuantumNeuralAvatarScene', () => ({
    AvatarSceneContent: ({ state }: { state: string }) => <div data-testid="avatar-scene" data-state={state} />
}));

describe('QuantumNeuralAvatar State Transitions', () => {

    beforeAll(() => {
        global.ResizeObserver = class ResizeObserver {
            observe() { }
            unobserve() { }
            disconnect() { }
        };
    });

    beforeEach(() => {
        // Reset store and engine state
        const state = useAetherStore.getState();
        state.setEngineState('IDLE');
        state.setAudioLevels(0, 0);
    });

    it('renders and displays IDLE state by default', () => {
        render(<QuantumNeuralAvatar />);
        const scene = screen.getByTestId('avatar-scene');
        expect(scene.getAttribute('data-state')).toBe('IDLE');
    });

    it('responds to LISTENING state from the store', () => {
        const store = useAetherStore.getState();
        render(<QuantumNeuralAvatar />);

        // Push state update
        store.setEngineState('LISTENING');

        const scene = screen.getByTestId('avatar-scene');
        expect(scene.getAttribute('data-state')).toBe('LISTENING');
    });

    it('responds to SPEAKING state from the store', () => {
        const store = useAetherStore.getState();
        render(<QuantumNeuralAvatar />);

        store.setEngineState('SPEAKING');

        const scene = screen.getByTestId('avatar-scene');
        expect(scene.getAttribute('data-state')).toBe('SPEAKING');
    });

    it('responds to THINKING state from the store', () => {
        const store = useAetherStore.getState();
        render(<QuantumNeuralAvatar />);

        store.setEngineState('THINKING');

        const scene = screen.getByTestId('avatar-scene');
        expect(scene.getAttribute('data-state')).toBe('THINKING');
    });

    it('responds to INTERRUPTING state (Barge-in)', () => {
        const store = useAetherStore.getState();
        render(<QuantumNeuralAvatar />);

        store.setEngineState('INTERRUPTING');

        const scene = screen.getByTestId('avatar-scene');
        expect(scene.getAttribute('data-state')).toBe('INTERRUPTING');
    });

    it('handles different size variants', () => {
        const { container } = render(<QuantumNeuralAvatar size="fullscreen" />);
        const wrapper = container.querySelector('.quantum-neural-avatar');
        expect(wrapper?.getAttribute('style')).toContain('width: 100%');
        expect(wrapper?.getAttribute('style')).toContain('height: 100%');
    });
});
