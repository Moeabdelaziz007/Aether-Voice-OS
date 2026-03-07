'use client';

import { useCallback, useRef } from 'react';

/**
 * Micro-Animations Hook — Provides programmatic control over micro-interactions
 * 
 * Usage:
 * const { triggerHapticShake, triggerRipple } = useMicroAnimations();
 * 
 * <button onClick={triggerHapticShake}>Shake Me</button>
 */
export function useMicroAnimations() {
    const animationTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    /**
     * Trigger haptic shake animation on an element
     * @param element - The DOM element to animate
     * @param intensity - 'normal' | 'intense'
     */
    const triggerHapticShake = useCallback((element: HTMLElement | null, intensity: 'normal' | 'intense' = 'normal') => {
        if (!element) return;

        // Remove existing class first
        element.classList.remove('haptic-shake', 'haptic-shake--intense');
        
        // Force reflow
        void element.offsetWidth;
        
        // Add appropriate shake class
        element.classList.add(intensity === 'intense' ? 'haptic-shake--intense' : 'haptic-shake');
        
        // Clean up after animation completes
        if (animationTimeoutRef.current) {
            clearTimeout(animationTimeoutRef.current);
        }
        
        animationTimeoutRef.current = setTimeout(() => {
            element.classList.remove('haptic-shake', 'haptic-shake--intense');
        }, 500);
    }, []);

    /**
     * Trigger magnetic hover effect
     * Note: This is mostly CSS-driven, but can be enhanced with JS
     */
    const applyMagneticEffect = useCallback((element: HTMLElement | null, cursorX: number, cursorY: number) => {
        if (!element) return;

        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        const deltaX = cursorX - centerX;
        const deltaY = cursorY - centerY;
        
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const maxDistance = 100; // px radius of influence
        
        if (distance < maxDistance) {
            const strength = 1 - (distance / maxDistance);
            const moveX = (deltaX / maxDistance) * 8 * strength;
            const moveY = (deltaY / maxDistance) * 8 * strength;
            
            element.style.transform = `translate(${moveX}px, ${moveY}px) scale(${1 + strength * 0.05})`;
        } else {
            element.style.transform = 'translate(0, 0) scale(1)';
        }
    }, []);

    /**
     * Reset all animations (cleanup)
     */
    const resetAnimations = useCallback(() => {
        if (animationTimeoutRef.current) {
            clearTimeout(animationTimeoutRef.current);
            animationTimeoutRef.current = null;
        }
    }, []);

    return {
        triggerHapticShake,
        applyMagneticEffect,
        resetAnimations,
    };
}
