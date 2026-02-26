'use client';

import { useEffect, useRef } from 'react';

type AudioState = 'idle' | 'listening' | 'thinking' | 'speaking';

interface LiveWaveLineProps {
    state: AudioState;
}

export function LiveWaveLine({ state }: LiveWaveLineProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId: number;
        let time = 0;

        const render = () => {
            time += 0.05;

            // Clear canvas with transparent background
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Define visual properties based on state
            let color = '#333333';
            let amplitude = 2;
            let frequency = 0.02;
            let glow = 0;

            switch (state) {
                case 'listening':
                    color = '#00f3ff';
                    amplitude = 15;
                    frequency = 0.05;
                    glow = 15;
                    break;
                case 'thinking':
                    color = '#ff00ff'; // neon purple/pink
                    amplitude = 20;
                    frequency = 0.1;
                    glow = 20;
                    break;
                case 'speaking':
                    color = '#00f3ff';
                    amplitude = 30 + Math.sin(time) * 10; // Dynamic amplitude mock
                    frequency = 0.08;
                    glow = 25;
                    break;
                case 'idle':
                default:
                    color = '#555555';
                    amplitude = 3;
                    frequency = 0.01;
                    glow = 2;
                    break;
            }

            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);

            for (let x = 0; x < canvas.width; x++) {
                // Create a sine wave combined with some noise/secondary wave for organic feel
                const y = canvas.height / 2 +
                    Math.sin(x * frequency + time) * amplitude *
                    Math.sin(x * 0.01);
                ctx.lineTo(x, y);
            }

            ctx.strokeStyle = color;
            ctx.lineWidth = 3;

            // Add glow effect
            ctx.shadowBlur = glow;
            ctx.shadowColor = color;

            ctx.stroke();

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    }, [state]);

    // Make canvas responsive to its container width using 100% width, fixed internal resolution
    return (
        <div className="w-full h-16 flex items-center justify-center">
            <canvas
                ref={canvasRef}
                width={300}
                height={64}
                className="w-full h-full object-contain"
            />
        </div>
    );
}
