# Frontend E2E Testing Guide

دليل تشغيل اختبارات الواجهة الأمامية باستخدام المتصفح

## 🎯 أنواع الاختبارات

### 1. **Playwright E2E Tests** (متصفح حقيقي)
تعمل على متصفح فعلي وتتطلب تشغيل التطبيق:

```bash
# تثبيت Playwright (مرة واحدة)
cd apps/portal
npx playwright install chromium

# تشغيل التطبيق في وضع التطوير
npm run dev

# تشغيل اختبارات E2E في نافذة متصفح مرئية
npm run test:e2e:headed

# أو تشغيل بدون واجهة رسومية (للـ CI/CD)
npm run test:e2e

# تشغيل مع واجهة Playwright UI
npm run test:e2e:ui

# تشغيل مع التصحيح (Debug)
npm run test:e2e:debug
```

### 2. **Vitest + jsdom** (محاكاة المتصفح)
تعمل بدون الحاجة لتشغيل التطبيق:

```bash
# تشغيل جميع اختبارات Vitest
npm test

# تشغيل اختبار محدد
npm test -- src/__tests__/e2e-browser.test.ts

# تشغيل وضع المراقبة
npm run test:watch
```

## 📋 ملفات الاختبار

### Playwright Tests
- `e2e/galaxy-orchestration.spec.ts` - اختبارات Galaxy Orchestration E2E

### Vitest Tests
- `src/__tests__/e2e-browser.test.ts` - اختبارات محاكاة المتصفح
- `src/__tests__/missionControlHUD.test.tsx` - اختبارات Mission Control HUD
- `src/__tests__/useAetherStore.test.ts` - اختبارات Store

## 🔧 التكوين

### Playwright Config
الملف: `playwright.config.ts`

```typescript
export default defineConfig({
  testDir: './e2e',
  baseURL: 'http://localhost:3000',
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## 🧪 أمثلة الاختبارات

### Playwright Test Example
```typescript
import { test, expect } from '@playwright/test';

test('should load main page', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Aether/);
  
  const canvas = page.locator('canvas').first();
  await expect(canvas).toBeVisible();
});
```

### Vitest Test Example
```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

describe('Component Test', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## 📊 النتائج

### Playwright HTML Report
بعد تشغيل الاختبارات:
```bash
npx playwright show-report
```

### Vitest Coverage
لتوليد تقرير التغطية:
```bash
npm test -- --coverage
```

## ⚠️ ملاحظات مهمة

### Firebase Configuration
قد تظهر أخطاء Firebase بسبب عدم وجود API keys في بيئة الاختبار:
```
FirebaseError: auth/invalid-api-key
```
هذا متوقع ولا يؤثر على صحة الاختبارات.

### Performance
- Playwright tests أبطأ (تتطلب تشغيل التطبيق)
- Vitest tests أسرع (محاكاة فقط)

### CI/CD Integration
لدمج الاختبارات في GitHub Actions:

```yaml
- name: Install dependencies
  run: npm ci

- name: Install Playwright browsers
  run: npx playwright install --with-deps chromium

- name: Run E2E tests
  run: npm run test:e2e
```

## 🎯 Best Practices

1. **استخدم Vitest لـ:**
   - Unit tests
   - Component tests
   - Integration tests السريعة

2. **استخدم Playwright لـ:**
   - E2E tests الكاملة
   - Visual regression tests
   - Cross-browser testing

3. **اكتب اختبارات قابلة للصيانة:**
   - استخدم data-testid للعناصر
   - تجنب selectors الهشة
   - وثق الاختبارات المعقدة

## 🐛 Troubleshooting

### Playwright لا يعمل
```bash
# إعادة تثبيت المتصفحات
npx playwright install --force

# مسح الكاش
npx playwright clean
```

### Vitest يفشل
```bash
# مسح node_modules وإعادة التثبيت
rm -rf node_modules
npm install

# التحقق من إعدادات jsdom
cat vitest.config.ts
```

## 📚 مراجع

- [Playwright Documentation](https://playwright.dev)
- [Vitest Documentation](https://vitest.dev)
- [Testing Library](https://testing-library.com)
