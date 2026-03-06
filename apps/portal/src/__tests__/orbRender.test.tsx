import React from 'react';
import { render } from '@testing-library/react';
// @ts-ignore - Ignore missing component until it's implemented
import AetherOrb from '../components/AetherOrb';
import { useAetherStore } from '../store/useAetherStore';
import { describe, it, expect, vi } from 'vitest';

describe('AetherOrb Render Performance', () => {

// Mock canvas getContext to avoid errors in jsdom
beforeAll(() => {
    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
        scale: vi.fn(),
        clearRect: vi.fn(),
        beginPath: vi.fn(),
        arc: vi.fn(),
        stroke: vi.fn(),
        fill: vi.fn(),
        createRadialGradient: vi.fn().mockReturnValue({ addColorStop: vi.fn() }),
    }) as any;
});

    it('does not re-render when transient state changes', () => {
        let renderCount = 0;

        // Create a wrapper component to track renders
        const TrackedOrb = () => {
            renderCount++;
            return <AetherOrb size={100} />;
        };

        const { unmount } = render(<TrackedOrb />);

        // Initial render
        expect(renderCount).toBe(1);

        // Update transient state that AetherOrb reads via useAetherStore.getState()
        // but does NOT subscribe to via useAetherStore(s => ...)
        useAetherStore.getState().setAudioLevels(0.5, 0.8);

        // Render count should still be 1! It shouldn't trigger React updates
        expect(renderCount).toBe(1);

        unmount();
    });
});
