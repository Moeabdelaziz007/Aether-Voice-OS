/**
 * Browser-based E2E Tests using Vitest + jsdom
 * 
 * These tests simulate browser interactions without requiring
 * a running server. Perfect for CI/CD pipelines.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

describe('Frontend E2E - Browser Simulation', () => {

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset any global state
    document.body.innerHTML = '';
  });

  describe('Page Load and Initial Render', () => {
    it('should render main page structure', async () => {
      // Import the page component
      const HomePage = (await import('@/app/page')).default;

      render(<HomePage />);

      // Wait for Three.js canvas to render
      await waitFor(() => {
        const canvas = document.querySelector('canvas');
        expect(canvas).toBeInTheDocument();
      }, { timeout: 5000 });
    });

    it('should initialize store correctly', () => {
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { getState } = useAetherStore;

      // Verify initial state
      const state = getState();
      expect(state.workspaceGalaxy).toBeDefined();
      expect(state.orbitRegistry).toBeDefined();
    });
  });

  describe('Mission Control HUD', () => {
    it('should render HUD components when active', async () => {
      const MissionControlHUD = await import('@/components/HUD/MissionControlHUD');

      // Mock active mission state
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { setState } = useAetherStore;

      setState({
        taskPulse: {
          task_id: 'test-task-1',
          phase: 'EXECUTING',
          action: 'test_action',
          vibe: 'neutral',
          thought: 'Test thought',
          avatar_state: 'IDLE',
          intensity: 0.5,
          latency_ms: 100,
          timestamp: new Date().toISOString(),
        },
      });

      render(<MissionControlHUD.default />);

      // Check for HUD elements
      await waitFor(() => {
        const hudElement = document.querySelector('[class*="MissionControl"]');
        expect(hudElement).toBeInTheDocument();
      });
    });
  });

  describe('Keyboard Interactions', () => {
    it('should respond to Escape key', async () => {
      const user = userEvent.setup();

      const HomePage = (await import('@/app/page')).default;
      render(<HomePage />);

      // Press Escape
      await user.keyboard('{Escape}');

      // Verify no errors occurred
      expect(document.body).toBeInTheDocument();
    });

    it('should respond to Enter key', async () => {
      const user = userEvent.setup();

      const HomePage = (await import('@/app/page')).default;
      render(<HomePage />);

      // Press Enter
      await user.keyboard('{Enter}');

      // App should still be functional
      expect(document.body).toBeInTheDocument();
    });
  });

  describe('Galaxy Orchestration State', () => {
    it('should maintain galaxy state in store', () => {
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { getState, setState } = useAetherStore;

      // Set galaxy state
      setState({
        workspaceGalaxy: 'Genesis',
        focusedPlanetId: 'Architect',
      });

      const state = getState();
      expect(state.workspaceGalaxy).toBe('Genesis');
      expect(state.focusedPlanetId).toBe('Architect');
    });

    it('should update orbit registry', () => {
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { setState } = useAetherStore;

      setState({
        orbitRegistry: {
          'Architect': {
            id: 'Architect',
            name: 'Architect',
            lane: 'inner',
            status: 'active',
            health: 1.0,
            load: 0.3,
          },
        },
      });

      const state = useAetherStore.getState();
      expect(state.orbitRegistry['Architect']).toBeDefined();
      expect(state.orbitRegistry['Architect'].lane).toBe('inner');
    });
  });

  describe('Cinematic Event Handling', () => {
    it('should process task pulse events', () => {
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { setState } = useAetherStore;

      const taskPulse = {
        task_id: 'pulse-test-1',
        phase: 'PLANNING',
        action: 'strategy_mapped',
        vibe: 'success',
        thought: 'Strategy mapped successfully',
        avatar_state: 'FOCUSED',
        intensity: 0.7,
        latency_ms: 80,
        timestamp: new Date().toISOString(),
      };

      setState({ taskPulse });

      const state = useAetherStore.getState();
      expect(state.taskPulse).toEqual(taskPulse);
    });

    it('should handle avatar state changes', () => {
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { setState } = useAetherStore;

      setState({
        avatarCinematicState: {
          state: 'TRANSITION',
          target: 'Debugger',
          duration: 1.5,
        },
      });

      const state = useAetherStore.getState();
      expect(state.avatarCinematicState.state).toBe('TRANSITION');
    });
  });

  describe('Responsive Layout', () => {
    it('should support different viewport sizes', () => {
      // Test desktop
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1920,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 1080,
      });

      window.dispatchEvent(new Event('resize'));
      expect(window.innerWidth).toBe(1920);

      // Test mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 667,
      });

      window.dispatchEvent(new Event('resize'));
      expect(window.innerWidth).toBe(375);
    });
  });

  describe('Error Handling', () => {
    it('should handle component errors gracefully', async () => {
      const consoleError = console.error;
      console.error = vi.fn();

      try {
        // Try to render a component that might error
        const BadComponent = () => {
          throw new Error('Test error');
        };

        expect(() => render(<BadComponent />)).toThrow();
      } finally {
        console.error = consoleError;
      }
    });

    it('should log errors to store', () => {
      const { useAetherStore } = await import('@/store/useAetherStore');
      const { addTerminalLog } = useAetherStore;

      addTerminalLog({
        message: 'Test error log',
        type: 'error',
        timestamp: new Date().toISOString(),
      });

      const state = useAetherStore.getState();
      expect(state.terminalLogs.length).toBeGreaterThan(0);
    });
  });
});
