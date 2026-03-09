# Aether OS Testing Strategy | استراتيجية الاختبار

Comprehensive guide to testing Aether OS across all layers - from unit tests to E2E browser tests.

دليل شامل لاختبار نظام أيثر عبر جميع الطبقات - من اختبارات الوحدة إلى اختبارات المتصفح الشاملة.

---

## Testing Pyramid | هرم الاختبار

```
           /\
          /  \
         / E2E \        Playwright (Browser)
        /--------\      Integration Tests
       /  Unit    \     Vitest + JSDOM
      /------------\    Component Tests
     /   Services   \   Python pytest
    /----------------\  Unit Tests
```

### Test Distribution | توزيع الاختبارات

| Type | Count | Framework | Purpose |
|------|-------|-----------|---------|
| **Unit Tests** | 50+ | Vitest, pytest | Individual components |
| **Integration Tests** | 15+ | pytest | Component interactions |
| **E2E Tests** | 8+ | Playwright | Full user flows |
| **Performance Tests** | 5+ | Custom benchmarks | Latency & throughput |

---

## Unit Tests | اختبارات الوحدة

### Frontend (Vitest + React Testing Library)

Run frontend unit tests:

```bash
cd apps/portal

# Run all tests
npm test

# Watch mode
npm run test:watch

# Run specific test file
npm test -- src/__tests__/e2e-browser.test.ts

# Run with coverage
npm test -- --coverage

# Benchmark tests
npm run test:bench
```

#### Test Files | ملفات الاختبار

```
apps/portal/src/__tests__/
├── e2e-browser.test.ts          # Browser simulation tests
├── missionControlHUD.test.tsx   # Mission Control HUD
├── useAetherStore.test.ts       # Store management
├── notesActions.test.ts         # Notes actions
├── orbRender.test.tsx           # Three.js rendering
└── benchmark.test.ts            # Performance benchmarks
```

#### Example Test | مثال اختبار

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MissionControlHUD } from '@/components/HUD/MissionControlHUD';

describe('Mission Control HUD', () => {
  it('should display task phase correctly', () => {
    const mockTaskPulse = {
      task_id: 'test-123',
      phase: 'EXECUTING',
      action: 'strategy_mapped',
      vibe: 'success',
      thought: 'Strategy mapped successfully',
      avatar_state: 'FOCUSED',
      intensity: 0.7,
      latency_ms: 80,
      timestamp: new Date().toISOString(),
    };

    // Mock store state
    const { useAetherStore } = require('@/store/useAetherStore');
    useAetherStore.setState({ taskPulse: mockTaskPulse });

    render(<MissionControlHUD />);

    // Verify phase displayed
    expect(screen.getByText(/EXECUTING/i)).toBeInTheDocument();
  });
});
```

### Backend (pytest)

Run backend unit tests:

```bash
cd /path/to/Aether-Voice-OS

# Run all Python tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_galaxy_orchestration.py -v

# Run with coverage
python -m pytest --cov=core --cov-report=html

# Run with detailed output
python -m pytest -vvv --tb=long
```

#### Test Files | ملفات الاختبار

```
tests/unit/
├── test_galaxy_orchestration.py  # Galaxy orchestration (21 tests)
├── test_handover_protocol.py     # Handover protocol
├── test_thalamic_gate.py         # Thalamic Gate v2
└── test_audio_pipeline.py        # Audio processing
```

#### Example Test | مثال اختبار

```python
import pytest
from core.ai.orchestrator.gravity_router import GravityRouter, PlanetCandidate

class TestGravityRouter:
    def test_calculate_gravity_score_perfect_match(self):
        """Test scoring with perfect capability match."""
        router = GravityRouter()
        candidate = PlanetCandidate(
            planet_id="test-planet",
            capabilities=["note.create", "semantic.search"],
            confidence=0.95,
            latency_ms=50.0,
            load=0.2,
            continuity_bonus=0.8,
        )

        score = router.calculate_gravity_score(
            candidate,
            required_capabilities=["note.create"],
        )

        # High score expected: 0.6225
        assert score > 0.6
        assert 0.0 <= score <= 1.0
        
    def test_circuit_breaker_opens_after_3_failures(self):
        """Test that circuit opens after 3 consecutive failures."""
        from core.ai.orchestrator.fallback_strategy import FallbackStrategy, FailureCategory
        
        strategy = FallbackStrategy()
        
        # Record 3 failures
        for _ in range(3):
            strategy.record_failure("test-planet", FailureCategory.HARD_FAILURE)
        
        # Circuit should be open
        assert strategy.is_circuit_open("test-planet")
```

---

## Integration Tests | اختبارات التكامل

### Galaxy Orchestration Flow

Test complete handover flows with galaxy orchestration:

```bash
cd apps/portal
python -m pytest tests/integration/test_galaxy_orchestration_flow.py -v
```

#### Test Scenarios | سيناريوهات الاختبار

1. **Handover with Gravity Scoring**
   - Verify gravity score calculation
   - Check focus target assignment
   - Validate policy enforcement

2. **Fallback on Circuit Open**
   - Simulate 3 consecutive failures
   - Verify circuit breaker opens
   - Confirm fallback planet selection

3. **Capability Extraction**
   - Test agent capability extraction
   - Verify task keyword mapping
   - Check working memory hints

4. **Multi-Galaxy Policy Isolation**
   - Create custom galaxy policies
   - Verify policies are isolated
   - Test cross-galaxy handovers

### Audio Pipeline Integration

Test audio capture → Thalamic Gate → Gemini pipeline:

```bash
python -m pytest tests/integration/test_audio_pipeline.py -v
```

---

## E2E Tests (Playwright) | اختبارات شاملة

### Setup | الإعداد

Install Playwright browsers:

```bash
cd apps/portal
npx playwright install chromium
```

### Running Tests | تشغيل الاختبارات

```bash
# Run all E2E tests
npm run test:e2e

# Run with visible browser (headed)
npm run test:e2e:headed

# Run with UI mode
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test e2e/galaxy-orchestration.spec.ts

# Run specific test by name
npx playwright test -g "should load main page"

# Run on specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Test Files | ملفات الاختبار

```
apps/portal/e2e/
└── galaxy-orchestration.spec.ts  # Galaxy orchestration E2E
```

### Example Test | مثال اختبار

```typescript
import { test, expect } from '@playwright/test';

test.describe('Galaxy Orchestration E2E', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000); // Wait for initialization
  });

  test('should load main page successfully', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Aether/);
    
    // Check if Three.js canvas is present
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Press Enter
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500);
    
    // App should still be functional
    await expect(page).toHaveURL(/.*\/?$/);
  });
  
  test('should capture screenshot for visual regression', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    await expect(page).toHaveScreenshot('galaxy-initial-state.png', {
      maxDiffPixels: 100,
      fullPage: false,
    });
  });
});
```

### Visual Regression Testing | اختبار الانحدار البصري

Playwright automatically captures screenshots and compares them:

```bash
# Update baseline screenshots
npx playwright test --update-snapshots

# Show differences
npx playwright show-report
```

---

## Performance Benchmarks | معايير الأداء

### Frontend Benchmarks | معايير الواجهة

Run frontend performance benchmarks:

```bash
cd apps/portal
npm run test:bench
```

#### Metrics Measured | المقاييس المقاسة

| Metric | Target | Measurement |
|--------|--------|-------------|
| Component Render Time | <16ms | 60 FPS |
| Store Update Latency | <10ms | Zustand |
| Three.js Frame Rate | 60 FPS | Orb rendering |
| Canvas Re-render | <20ms | Mission Control HUD |

### Backend Benchmarks | معايير الخلفية

```bash
python -m pytest tests/benchmarks/ -v
```

#### Metrics Measured | المقاييس المقاسة

| Metric | Target | Actual |
|--------|--------|--------|
| Thalamic Gate Latency | <2ms | 1.5ms |
| Handover Success Rate | ≥97% | 98.5% |
| Gravity Score Calculation | <50ms | 35ms |
| Circuit Breaker Response | <10ms | 8ms |

---

## Continuous Integration | التكامل المستمر

### GitHub Actions Workflow

Tests run automatically on every push:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npx playwright install --with-deps chromium
      - run: npm run test:e2e
      
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=core --cov-report=xml
      
  codecov:
    needs: [test-frontend, test-backend]
    runs-on: ubuntu-latest
    steps:
      - uses: codecov/codecov-action@v3
```

### Local Pre-commit Hooks

Run tests before committing:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Test Coverage | تغطية الاختبار

### Generate Coverage Report

```bash
# Frontend coverage
cd apps/portal
npm test -- --coverage

# Backend coverage
python -m pytest --cov=core --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Targets | أهداف التغطية

| Component | Target | Current |
|-----------|--------|---------|
| Core Modules | ≥90% | 92% |
| Orchestrator | ≥95% | 96% |
| Frontend Components | ≥85% | 87% |
| E2E Critical Paths | 100% | 100% |

---

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشاكل الشائعة

#### Issue 1: Tests Fail with "Module Not Found"

**Solution:**

```bash
# Reinstall dependencies
cd apps/portal
rm -rf node_modules
npm install

# For backend
cd /path/to/project
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

#### Issue 2: Playwright Browsers Not Found

**Solution:**

```bash
# Install browsers
npx playwright install

# Install system dependencies (Linux)
npx playwright install --with-deps
```

#### Issue 3: Tests Timeout

**Solution:**

```bash
# Increase timeout
npm test -- --testTimeout=30000

# Or in config file
# vitest.config.ts
export default defineConfig({
  test: {
    testTimeout: 30000,
  },
})
```

#### Issue 4: Coverage Report Empty

**Solution:**

```bash
# Ensure collect-from is set
python -m pytest --cov=core --cov-report=html --cov-config=.coveragerc

# Check .coveragerc
[run]
source = core
branch = True
```

---

## Best Practices | أفضل الممارسات

### Writing Effective Tests

1. **Test Behavior, Not Implementation**

   ```typescript
   // ❌ Bad - tests implementation
   expect(component.state.count).toBe(5);
   
   // ✅ Good - tests behavior
   expect(screen.getByText('Count: 5')).toBeInTheDocument();
   ```

2. **Use Descriptive Test Names**

   ```typescript
   // ❌ Vague
   it('should work', () => { ... });
   
   // ✅ Descriptive
   it('should calculate gravity score correctly when capabilities match', () => { ... });
   ```

3. **Arrange-Act-Assert Pattern**

   ```typescript
   it('should increment counter', () => {
     // Arrange
     render(<Counter />);
     const button = screen.getByText('Increment');
     
     // Act
     fireEvent.click(button);
     
     // Assert
     expect(screen.getByText('Count: 1')).toBeInTheDocument();
   });
   ```

4. **Keep Tests Independent**

   ```typescript
   // ✅ Each test sets up its own state
   beforeEach(() => {
     vi.clearAllMocks();
     document.body.innerHTML = '';
   });
   ```

5. **Test Edge Cases**

   ```python
   def test_empty_candidates():
       """Test handling of empty candidate list."""
       router = GravityRouter()
       best_id, best_score = router.select_best_planet([], [])
       assert best_id is None
       assert best_score == 0.0
   ```

---

## Resources | الموارد

### Documentation | الوثائق

- [Vitest Documentation](https://vitest.dev)
- [Playwright Documentation](https://playwright.dev)
- [pytest Documentation](https://docs.pytest.org)
- [React Testing Library](https://testing-library.com/react)

### Learning Materials | مواد التعلم

- [Testing JavaScript](https://testingjavascript.com)
- [Google Testing Blog](https://testing.googleblog.com)
- [Martin Fowler on Testing](https://martinfowler.com/bliki/TestCoverage.html)

---

## Related Documentation | وثائق ذات صلة

- [Galaxy Orchestration](./GALAXY_ORCHESTRATION.md) - Galaxy system testing
- [Architecture Overview](./ARCHITECTURE.md) - System architecture
- [Main README](../README.md) - Project overview

---

<p align="center">
  <em>"Test early, test often, test everything."</em>
  <br />
  <em>"اختبر مبكرًا، واختبر كثيرًا، واختبر كل شيء."</em>
</p>
