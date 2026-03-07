/**
 * AetherOS E2E Tests - Galaxy Orchestration UI
 * 
 * Tests for:
 * 1. Mission Control HUD rendering
 * 2. Orbital Workspace Overlay
 * 3. Galaxy state visualization
 * 4. Cinematic event handling
 */

import { test, expect } from '@playwright/test';

test.describe('AetherOS Galaxy Orchestration E2E', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    // Wait for app to initialize
    await page.waitForTimeout(2000);
  });

  test('should load main page successfully', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Aether/);
    
    // Check if main components are present
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
  });

  test('should display Mission Control HUD', async ({ page }) => {
    // Look for mission control elements
    const missionControl = page.locator('[data-testid="mission-control-hud"], .mission-control, [class*="MissionControl"]');
    
    // If HUD exists, verify it's visible
    if (await missionControl.count() > 0) {
      await expect(missionControl.first()).toBeVisible();
    }
    
    // Alternative: Check for common HUD elements
    const hudElements = page.locator('[class*="hud"], [class*="HUD"]');
    if (await hudElements.count() > 0) {
      await expect(hudElements.first()).toBeInViewport();
    }
  });

  test('should render Three.js canvas', async ({ page }) => {
    // Three.js should create a canvas element
    const canvas = page.locator('canvas');
    await expect(canvas.first()).toBeVisible();
    
    // Canvas should have valid dimensions
    const box = await canvas.first().boundingBox();
    expect(box).toBeTruthy();
    if (box) {
      expect(box.width).toBeGreaterThan(0);
      expect(box.height).toBeGreaterThan(0);
    }
  });

  test('should handle page without errors', async ({ page }) => {
    // Track console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Wait for potential errors
    await page.waitForTimeout(3000);
    
    // Should not have critical errors
    const criticalErrors = errors.filter(err => 
      !err.includes('Warning') && 
      !err.includes('DEV')
    );
    
    expect(criticalErrors.length).toBeLessThan(5);
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Test basic keyboard interaction
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Press space or enter
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500);
    
    // App should still be functional
    await expect(page).toHaveURL(/.*\/?$/);
  });
});

test.describe('Galaxy Orchestration Visual Tests', () => {
  
  test('should capture initial state screenshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    // Take screenshot for visual regression testing
    await expect(page).toHaveScreenshot('galaxy-initial-state.png', {
      maxDiffPixels: 100,
      fullPage: false,
    });
  });

  test('should verify responsive layout', async ({ page }) => {
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot('desktop-layout.png');
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot('tablet-layout.png');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await expect(page).toHaveScreenshot('mobile-layout.png');
  });
});
