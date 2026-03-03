"use client";
/**
 * Aether V3 — Vision Pulse Hook.
 *
 * Captures the user's screen at 1 FPS and produces compressed
 * Base64 JPEG strings ready for injection into the Gemini WebSocket.
 *
 * Features:
 *   - getDisplayMedia-based screen capture
 *   - Off-screen canvas rendering (never touches DOM)
 *   - JPEG compression at quality 0.4 (~20KB per frame)
 *   - Change-detection: skips frames with <5% size delta
 *   - Clean teardown of all media tracks and resources
 */

import { useCallback, useEffect, useRef, useState } from "react";

/** Capture interval in milliseconds (1 FPS) */
const CAPTURE_INTERVAL_MS = 1000;

/** JPEG quality (0-1). Lower = smaller payload, faster encode */
const JPEG_QUALITY = 0.4;

/** Minimum size change ratio to consider a frame "new" (5%) */
const CHANGE_THRESHOLD = 0.05;

/** Scale factor for captured frames (0.5 = half resolution → faster encode) */
const SCALE_FACTOR = 0.5;

export interface VisionPulseReturn {
    /** Whether screen capture is currently active */
    isCapturing: boolean;
    /** The latest captured frame as a base64 JPEG string (no data URI prefix) */
    latestFrame: string | null;
    /** Total frames captured this session */
    frameCount: number;
    /** Total frames actually sent (after change-detection filter) */
    sentCount: number;
    /** Start screen capture (triggers browser permission popup) */
    startCapture: () => Promise<void>;
    /** Stop screen capture and clean up all resources */
    stopCapture: () => void;
}

export function useVisionPulse(): VisionPulseReturn {
    const [isCapturing, setIsCapturing] = useState(false);
    const [latestFrame, setLatestFrame] = useState<string | null>(null);
    const [frameCount, setFrameCount] = useState(0);
    const [sentCount, setSentCount] = useState(0);

    // Internal refs (avoid re-renders)
    const streamRef = useRef<MediaStream | null>(null);
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const ctxRef = useRef<CanvasRenderingContext2D | null>(null);
    const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const lastFrameSizeRef = useRef<number>(0);
    const frameCountRef = useRef(0);
    const sentCountRef = useRef(0);

    /**
     * Capture a single frame from the video stream.
     * Returns the raw base64 JPEG string (no data: prefix) or null if skipped.
     */
    const captureFrame = useCallback((): string | null => {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = ctxRef.current;

        if (!video || !canvas || !ctx || video.readyState < 2) {
            return null;
        }

        // Scale dimensions for faster encoding
        const w = Math.round(video.videoWidth * SCALE_FACTOR);
        const h = Math.round(video.videoHeight * SCALE_FACTOR);

        if (w === 0 || h === 0) return null;

        // Resize canvas if needed
        if (canvas.width !== w || canvas.height !== h) {
            canvas.width = w;
            canvas.height = h;
        }

        // Draw current video frame
        ctx.drawImage(video, 0, 0, w, h);

        // Encode to JPEG
        const dataUrl = canvas.toDataURL("image/jpeg", JPEG_QUALITY);

        // Extract raw base64 (remove "data:image/jpeg;base64," prefix)
        const b64 = dataUrl.split(",")[1];
        if (!b64) return null;

        // Increment total frame count
        frameCountRef.current += 1;
        setFrameCount(frameCountRef.current);

        // ─── Change Detection ───────────────────────────────────
        const currentSize = b64.length;
        const lastSize = lastFrameSizeRef.current;

        if (lastSize > 0) {
            const delta = Math.abs(currentSize - lastSize) / lastSize;
            if (delta < CHANGE_THRESHOLD) {
                // Frame is nearly identical — skip it
                return null;
            }
        }

        lastFrameSizeRef.current = currentSize;
        sentCountRef.current += 1;
        setSentCount(sentCountRef.current);

        return b64;
    }, []);

    /**
     * Start screen capture. Triggers browser permission popup.
     */
    const startCapture = useCallback(async () => {
        if (streamRef.current) return; // Already capturing

        try {
            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    frameRate: 1,      // We only need 1 FPS
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                },
                audio: false,
            });

            streamRef.current = stream;

            // Create off-screen video element
            const video = document.createElement("video");
            video.srcObject = stream;
            video.muted = true;
            video.playsInline = true;
            videoRef.current = video;

            // Create off-screen canvas
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d", { willReadFrequently: true });
            canvasRef.current = canvas;
            ctxRef.current = ctx;

            // Start playback (needed to get video frames)
            await video.play();

            // Listen for user stopping screen share via browser UI
            stream.getVideoTracks()[0].addEventListener("ended", () => {
                stopCapture();
            });

            setIsCapturing(true);

            // Start capture interval
            intervalRef.current = setInterval(() => {
                const frame = captureFrame();
                if (frame) {
                    setLatestFrame(frame);
                }
            }, CAPTURE_INTERVAL_MS);

            console.log("👁 Vision Pulse started — 1 FPS screen capture active");
        } catch (err) {
            console.error("Vision Pulse: Failed to start screen capture:", err);
            // User denied permission or API not available
            stopCapture();
        }
    }, [captureFrame]);

    /**
     * Stop screen capture and clean up all resources.
     */
    const stopCapture = useCallback(() => {
        // Stop interval
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }

        // Stop all media tracks
        if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
            streamRef.current = null;
        }

        // Clean up video element
        if (videoRef.current) {
            videoRef.current.srcObject = null;
            videoRef.current = null;
        }

        // Clean up canvas
        canvasRef.current = null;
        ctxRef.current = null;

        // Reset state
        lastFrameSizeRef.current = 0;
        setIsCapturing(false);
        setLatestFrame(null);

        console.log("👁 Vision Pulse stopped");
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopCapture();
        };
    }, [stopCapture]);

    return {
        isCapturing,
        latestFrame,
        frameCount,
        sentCount,
        startCapture,
        stopCapture,
    };
}
