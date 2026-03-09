import React from 'react';
import { render } from '@testing-library/react';
import QuantumNeuralAvatar from '../components/QuantumNeuralAvatar';
import { describe, it, expect, vi, beforeAll } from 'vitest';

describe('QuantumNeuralAvatar Render Performance', () => {

    beforeAll(() => {
        global.ResizeObserver = class ResizeObserver {
            observe() {}
            unobserve() {}
            disconnect() {}
        };
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

    it('renders without crashing', () => {
        const { container } = render(<QuantumNeuralAvatar />);
        expect(container).toBeTruthy();
    });
});
