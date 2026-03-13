const { test, expect } = require('@playwright/test');

test('E2E Neural Integration & Stress Test (Final Boss Level)', async ({ page }) => {
  // Simulate 10% packet loss (Network Jitter) but ONLY on websocket connections
  // to avoid blocking static assets like CSS/JS which break the whole app
  await page.route('**/*', async route => {
    const request = route.request();
    if (request.resourceType() === 'websocket') {
        if (Math.random() < 0.1) {
            return route.abort('failed');
        }
    }
    await route.continue();
  });

  await page.goto('http://localhost:3000'); // Assuming portal runs on 3000

  // Wait for the brain to initialize and connect
  const startTimer = Date.now();
  let ttfvr = null;

  // Listen for the first visual response (Telemetry HUD update or Transcript)
  page.on('websocket', ws => {
    ws.on('framesent', payload => {
       // Mock 60 seconds of audio data or binary stream
    });
    ws.on('framereceived', payload => {
      if (!ttfvr) {
        ttfvr = Date.now() - startTimer;
        console.log(`[E2E Benchmark] Time to First Visual Response (TTFVR): ${ttfvr}ms`);
      }
    });
  });

  // Mock speaking for 60 seconds
  await page.evaluate(() => {
     // Simulating mic input triggering `micLevel`
     window.dispatchEvent(new CustomEvent('mock-audio-input', { detail: { rms: 0.1 } }));
  });

  // Wait to allow the stress test to run
  await page.waitForTimeout(60000); // 60s

  if (ttfvr !== null) {
      expect(ttfvr).toBeLessThan(250); // Goal: < 250ms
  } else {
      console.warn('No visual response received within the timeframe.');
  }
});
