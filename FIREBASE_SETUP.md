# Firebase Setup Guide - GEMIGRAM

## المشكلة الحالية

خطأ `Firebase: Error (auth/invalid-api-key)` يحدث لأن متغيرات البيئة لم تكن معرفة بشكل صحيح.

## الحل السريع

### 1. إضافة متغيرات البيئة إلى Vercel

1. توجه إلى https://vercel.com/dashboard
2. اختر مشروعك
3. اذهب إلى Settings → Environment Variables
4. أضف المتغيرات التالية:

```
NEXT_PUBLIC_FIREBASE_API_KEY = "your_api_key_from_firebase"
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = "your_project.firebaseapp.com"
NEXT_PUBLIC_FIREBASE_PROJECT_ID = "your_project_id"
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = "your_project.appspot.com"
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = "your_sender_id"
NEXT_PUBLIC_FIREBASE_APP_ID = "your_app_id"
```

### 2. الحصول على بيانات Firebase

1. توجه إلى [Firebase Console](https://console.firebase.google.com)
2. اختر مشروعك
3. اذهب إلى Project Settings (⚙️)
4. اختر "Your apps" ← "Web"
5. انسخ البيانات من `firebaseConfig`

### 3. الاختبار المحلي

أنشئ ملف `.env.local` في مجلد `apps/portal`:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY="your_key"
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="your_domain"
NEXT_PUBLIC_FIREBASE_PROJECT_ID="your_project_id"
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="your_storage"
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="your_sender_id"
NEXT_PUBLIC_FIREBASE_APP_ID="your_app_id"
GOOGLE_API_KEY="your_google_api_key"
AETHER_JWT_SECRET="your_jwt_secret"
```

ثم شغل التطبيق:

```bash
cd apps/portal
npm run dev
```

## الميزات المضافة للأمان

1. **Server-Side Safety**: Firebase لن يتم تهيئته من جهة الخادم
2. **Client-Only Initialization**: يتم فحص `isClient` قبل استخدام Firebase
3. **Fallback Mock User**: إذا لم تكن Firebase متاحة، يتم استخدام مستخدم تطوير
4. **Graceful Error Handling**: الأخطاء لا تؤدي لفشل التطبيق

## خطوات Firebase Hosting

إذا كنت تستضيف على Firebase Hosting:

```bash
# تثبيت Firebase CLI
npm install -g firebase-tools

# تسجيل الدخول
firebase login

# تهيئة المشروع
firebase init hosting

# بناء التطبيق
npm run build

# نشر التطبيق
firebase deploy
```

## استكشاف الأخطاء

### الخطأ: `auth/invalid-api-key`
- تحقق من أن API Key صحيح
- تأكد من تفعيل Authentication في Firebase Console
- تحقق من أن العنوان صحيح في Auth Domain

### الخطأ: `auth/operation-not-allowed`
- تأكد من تفعيل Google Sign-In في Firebase Authentication
- اذهب إلى Firebase Console → Authentication → Sign-in method
- فعّل Google وأي methods أخرى تريدها

### الخطأ: Variables غير معرفة
- تأكد من إضافة المتغيرات في Vercel
- أعد بناء المشروع بعد إضافة المتغيرات
- تحقق من أن المتغيرات مرئية (عام/خاص)

## اختبار الاتصال

افتح Browser DevTools وشغل:

```javascript
// تحقق من Firebase config
console.log(process.env.NEXT_PUBLIC_FIREBASE_API_KEY)

// إذا كانت undefined، فالمتغيرات غير معرفة
```

## البدائل

إذا كنت تريد تخطي Firebase مؤقتاً:

1. التطبيق سيستخدم Mock User تلقائياً
2. يمكنك تطوير الواجهات بدون مصادقة حقيقية
3. أضف Firebase لاحقاً عندما تكون جاهزاً
