'use client';

import { useEffect, useRef } from 'react';

type AudioState = 'idle' | 'listening' | 'thinking' | 'speaking';

interface LiveWaveLineProps {
    state: AudioState;
    valence?: number;
    arousal?: number;
}

export function LiveWaveLine({ state, valence = 0.5, arousal = 0.5 }: LiveWaveLineProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId: number;
        let time = 0;

        // Custom noise generator for organic movement
        const noise = (x: number, t: number) => Math.sin(x * 0.05 + t) * Math.cos(x * 0.03 - t * 0.8);

        const render = () => {
            time += 0.05;

            // Clear canvas with transparent dark blend
            ctx.fillStyle = 'rgba(5, 5, 5, 0.3)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Define visual properties based on state
            let baseColor = '51, 51, 51';
            let amplitudeBase = 3;
            let layers = 1;
            let frequency = 0.01;
            let glitchFactor = 0;

            switch (state) {
                case 'listening':
                    baseColor = valence > 0.6 ? '0, 243, 255' : '255, 153, 0'; // Cyan / Orange
                    amplitudeBase = 15 * (1 + arousal);
                    frequency = 0.04;
                    layers = 3;
                    break;
                case 'thinking':
                    baseColor = '188, 19, 254'; // Purple
                    amplitudeBase = 25 * (1 + arousal);
                    frequency = 0.08;
                    layers = 4;
                    // Introduce erratic high-frequency noise
                    glitchFactor = arousal * 10;
                    break;
                case 'speaking':
                    baseColor = valence > 0.6 ? '0, 243, 255' : valence < 0.4 ? '255, 51, 51' : '0, 243, 255';
                    amplitudeBase = (35 + Math.sin(time * 2) * 15) * (1 + arousal);
                    frequency = 0.06;
                    layers = 3;
                    if (valence < 0.4) glitchFactor = 20; // Frustration causes glitchy peaks
                    break;
                case 'idle':
                default:
                    baseColor = '100, 100, 100';
                    amplitudeBase = 2;
                    frequency = 0.005;
                    layers = 1;
                    break;
            }

            // Draw multi-layered waves
            for (let l = 0; l < layers; l++) {
                const layerOffset = l * Math.PI * 0.5;
                const layerAmplitude = amplitudeBase * (1 - l * 0.2);
                const layerAlpha = 1 - l * 0.2;

                ctx.beginPath();
                ctx.moveTo(0, canvas.height / 2);

                for (let x = 0; x < canvas.width; x++) {
                    // Core sine wave
                    let yOffset = Math.sin(x * frequency + time + layerOffset) * layerAmplitude;

                    // Modulate with organic noise
                    yOffset *= (1 + noise(x, time) * 0.5);

                    // Inject Glitch factor (Sharp high-frequency peaks)
                    if (glitchFactor > 0 && Math.random() < 0.05) {
                        yOffset += (Math.random() - 0.5) * glitchFactor;
                    }

                    const y = canvas.height / 2 + yOffset;
                    ctx.lineTo(x, y);
                }

                ctx.strokeStyle = `rgba(${baseColor}, ${layerAlpha})`;
                ctx.lineWidth = l === 0 ? 3 : 1;

                // Deep Bloom Pass
                ctx.shadowBlur = l === 0 ? 20 : 10;
                ctx.shadowColor = `rgb(${baseColor})`;

                ctx.stroke();
            }

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    }, [state, valence, arousal]);

    return (
        <div className="w-full h-24 flex items-center justify-center relative">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#00f3ff]/5 to-transparent blur-2xl pointer-events-none" />
            <canvas
                ref={canvasRef}
                width={400}
                height={96}
                className="w-full h-full object-contain mix-blend-screen"
            />
        </div>
    );
}
