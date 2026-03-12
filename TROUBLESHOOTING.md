# Troubleshooting Guide - GEMIGRAM

## Firebase Errors

### Error: `Firebase: Error (auth/invalid-api-key)`

**السبب:**
- متغيرات البيئة لم تُعيّن في Vercel
- API Key غير صحيح
- Firebase لم يتم تهيئته بشكل صحيح

**الحل:**
1. تحقق من متغيرات البيئة في Vercel Settings
2. انسخ API Key الصحيح من Firebase Console
3. أعد بناء المشروع: `vercel rebuild`
4. استخدم Mock User للتطوير (سيتم استخدامه تلقائياً)

### Error: `auth/operation-not-allowed`

**السبب:**
- Google Sign-In لم يتم تفعيله في Firebase
- Authentication methods لم تُفعّل

**الحل:**
1. توجه إلى Firebase Console
2. Authentication → Sign-in method
3. فعّل Google و Email/Password

### Error: `No firebaseConfig.apiKey`

**السبب:**
- `NEXT_PUBLIC_FIREBASE_API_KEY` غير معرّف

**الحل:**
```bash
# التحقق من المتغيرات
echo $NEXT_PUBLIC_FIREBASE_API_KEY

# إذا كانت فارغة:
# 1. أضفها إلى .env.local (للتطوير المحلي)
# 2. أضفها إلى Vercel Settings (للإنتاج)
```

## Hydration Errors

### Error: `Hydration mismatch` أو `Warning: Did not expect server HTML to contain`

**السبب:**
- Firebase يتم تهيئته من جهة الخادم
- Client و Server لديهما HTML مختلف

**الحل:**
تم إصلاح ذلك بـ:
1. فحص `isClient` قبل استخدام Firebase
2. استخدام `useEffect` و `useState` بدلاً من SSR
3. إضافة hydration check في `AuthGuard`

## Build Errors

### Error: `Could not find module '@/lib/firebase'`

**السبب:**
- المسار غير صحيح
- الملف لم ينسخ بشكل صحيح

**الحل:**
```bash
# تحقق من أن الملف موجود
ls apps/portal/src/lib/firebase.ts

# إعادة بناء
npm run build

# تنظيف cache
rm -rf .next
npm run build
```

### Error: `Module not found: can't resolve 'firebase/app'`

**السبب:**
- Firebase package غير مثبت

**الحل:**
```bash
cd apps/portal
npm install firebase
npm run build
```

## Runtime Errors

### Error: `useAuth is not available`

**السبب:**
- `useAuth` تم استدعاؤها من جهة الخادم

**الحل:**
```typescript
// ✗ خطأ - في Server Component
import { useAuth } from '@/hooks/useAuth';
export default function Page() {
    const { user } = useAuth(); // Server Component لا يمكن استخدام Hooks
}

// ✓ صحيح - في Client Component
'use client';
import { useAuth } from '@/hooks/useAuth';
export default function Page() {
    const { user } = useAuth(); // Client Component يمكن استخدام Hooks
}
```

## Development Mode

إذا واجهت مشاكل مع Firebase:

1. **استخدم Mock User:**
   ```
   التطبيق سيستخدم تلقائياً dev user إذا لم تكن Firebase متاحة
   ```

2. **تحقق من Console:**
   ```javascript
   // في Browser DevTools
   localStorage.getItem('aether-user')
   ```

3. **أعد تحميل الصفحة:**
   ```
   Cmd/Ctrl + Shift + R (Hard Refresh)
   ```

## Production Deployment

### Firebase Hosting

```bash
# تسجيل الدخول
firebase login

# بناء التطبيق
npm run build

# نشر
firebase deploy
```

### Vercel

```bash
# أضف المتغيرات في Vercel Settings أولاً

# نشر
vercel deploy --prod
```

## Verification Checklist

- [ ] متغيرات البيئة معرفة في Vercel
- [ ] Firebase Console تم إعدادها
- [ ] Google Sign-In مفعّل
- [ ] API Key صحيح
- [ ] Build ينجح بدون أخطاء
- [ ] App يحمّل في المتصفح
- [ ] Mock User يظهر إذا لم تكن Firebase متاحة

## Getting Help

1. تحقق من الأخطاء في Console (F12)
2. اقرأ Firebase documentation
3. تحقق من متغيرات البيئة
4. أعد بناء المشروع
5. استخدم Mock User للتطوير
