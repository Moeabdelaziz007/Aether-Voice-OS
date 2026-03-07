'use client';

/**
 * Vision Pulse Terminal — Visual Context Display
 * 
 * Shows a live preview of what the AI is "seeing" through screen capture.
 * Features:
 * - Real-time frame preview with neural aesthetic
 * - Frame counter and telemetry display
 * - Manual capture trigger button
 * - Visual quality indicator
 */

import React, { useRef, useEffect, useState } from 'react';
import { useVisionPulse } from '@/hooks/useVisionPulse';
import { useMicroAnimations } from '@/hooks/useMicroAnimations';
import clsx from 'clsx';

interface VisionPulseTerminalProps {
    className?: string;
    compact?: boolean;
}

export function VisionPulseTerminal({ className, compact = false }: VisionPulseTerminalProps) {
    const { isCapturing, latestFrame, frameCount, sentCount, startCapture, stopCapture } = useVisionPulse();
    const { triggerHapticShake } = useMicroAnimations();
    const previewRef = useRef<HTMLDivElement>(null);
    const imgRef = useRef<HTMLImageElement>(null);
    const [lastUpdateTime, setLastUpdateTime] = useState<number>(0);
    const [frameSize, setFrameSize] = useState<number>(0);

    // Update frame preview when new frame arrives
    useEffect(() => {
        if (latestFrame && imgRef.current) {
            const img = imgRef.current;
            const previousSrc = img.src;
            
            img.src = `data:image/jpeg;base64,${latestFrame}`;
            
            // Track frame size
            setFrameSize(latestFrame.length);
            setLastUpdateTime(Date.now());
            
            // Subtle flash on new frame
            if (previousSrc && img.parentElement) {
                img.parentElement.classList.add('frame-flash');
                setTimeout(() => {
                    img.parentElement?.classList.remove('frame-flash');
                }, 150);
            }
        }
    }, [latestFrame]);

    const handleToggleCapture = async () => {
        if (previewRef.current) {
            triggerHapticShake(previewRef.current, 'normal');
        }
        
        if (isCapturing) {
            stopCapture();
        } else {
            await startCapture();
        }
    };

    // Calculate FPS (frames per minute for low-frequency updates)
    const framesPerMinute = Math.round(frameCount * 60 / ((Date.now() - lastUpdateTime + 1000) / 1000));

    return (
        <div 
            ref={previewRef}
            className={clsx(
                'vision-pulse-terminal',
                'ultra-glass',
                'rounded-2xl',
                'overflow-hidden',
                'border border-white/10',
                'transition-all duration-300',
                className
            )}
            style={{
                backdropFilter: 'blur(40px) saturate(1.5)',
                WebkitBackdropFilter: 'blur(40px) saturate(1.5)',
            }}
        >
            {/* Header */}
            <div className="vision-pulse-header flex items-center justify-between px-4 py-3 border-b border-white/10">
                <div className="flex items-center gap-3">
                    <div className={clsx(
                        'pulse-indicator w-2 h-2 rounded-full',
                        isCapturing ? 'bg-cyan-400 animate-pulse' : 'bg-gray-500'
                    )} />
                    <span className="text-sm font-medium text-white/90 tracking-tight">
                        👁 Vision Pulse Terminal
                    </span>
                </div>
                
                <button
                    onClick={handleToggleCapture}
                    className={clsx(
                        'text-xs px-3 py-1.5 rounded-lg font-medium transition-all',
                        'magnetic-hover interactive-element',
                        isCapturing 
                            ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
                            : 'bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30'
                    )}
                >
                    {isCapturing ? 'Stop Capture' : 'Start Capture'}
                </button>
            </div>

            {/* Main Preview Area */}
            <div className="vision-pulse-preview relative aspect-video bg-black/50 overflow-hidden">
                {!isCapturing ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center space-y-3">
                            <div className="text-5xl mb-2 opacity-50">👁</div>
                            <p className="text-white/60 text-sm">Vision Pulse Inactive</p>
                            <p className="text-white/40 text-xs max-w-[200px] mx-auto">
                                Click "Start Capture" to share your screen with Aether
                            </p>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* Live Frame Preview */}
                        <div className="frame-container absolute inset-0 p-2">
                            <img
                                ref={imgRef}
                                alt="Live vision frame"
                                className="w-full h-full object-cover rounded-lg border border-white/10"
                                style={{
                                    imageRendering: 'pixelated',
                                }}
                            />
                            
                            {/* Scanline Effect */}
                            <div className="scanlines absolute inset-0 pointer-events-none opacity-20" />
                        </div>

                        {/* Overlay Info */}
                        <div className="absolute top-2 right-2 flex gap-2">
                            <div className="bg-black/70 backdrop-blur-sm px-2 py-1 rounded text-xs text-white/80 border border-white/10">
                                <span className="text-white/60">FPS:</span> {framesPerMinute}
                            </div>
                            <div className="bg-black/70 backdrop-blur-sm px-2 py-1 rounded text-xs text-white/80 border border-white/10">
                                <span className="text-white/60">Size:</span> {(frameSize / 1024).toFixed(1)}KB
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Telemetry Footer */}
            <div className="vision-pulse-footer px-4 py-3 border-t border-white/10 bg-black/30">
                <div className="grid grid-cols-3 gap-4 text-xs">
                    <div className="text-center">
                        <div className="text-white/50 mb-1">Total Frames</div>
                        <div className="text-white/90 font-mono">{frameCount}</div>
                    </div>
                    <div className="text-center">
                        <div className="text-white/50 mb-1">Sent Frames</div>
                        <div className="text-white/90 font-mono">{sentCount}</div>
                    </div>
                    <div className="text-center">
                        <div className="text-white/50 mb-1">Efficiency</div>
                        <div className="text-white/90 font-mono">
                            {frameCount > 0 ? Math.round((sentCount / frameCount) * 100) : 0}%
                        </div>
                    </div>
                </div>
                
                {/* Progress Bar */}
                {isCapturing && (
                    <div className="mt-3 h-0.5 bg-white/10 rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 transition-all duration-1000"
                            style={{
                                width: `${Math.min((frameCount % 60) / 60 * 100, 100)}%`
                            }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

export default VisionPulseTerminal;
