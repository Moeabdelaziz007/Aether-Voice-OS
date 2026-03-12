# دليل مرجع المطورين - GEMIGRAM

## هيكل المشروع السريع

```
apps/portal/src/
├── app/                          # صفحات Next.js
│   ├── layout.tsx               # التخطيط الرئيسي
│   ├── page.tsx                 # الصفحة الرئيسية (/)
│   ├── create/page.tsx          # إنشاء الوكيل
│   ├── chat/page.tsx            # الدردشة
│   ├── discover/page.tsx        # الاكتشاف
│   ├── hub/page.tsx             # مركز الوكلاء
│   ├── profile/page.tsx         # الملف الشخصي
│   ├── settings/page.tsx        # الإعدادات
│   ├── agent/[id]/page.tsx      # تفاصيل الوكيل
│   └── login/page.tsx           # تسجيل الدخول (موجود)
├── components/
│   ├── landing/                 # مكونات الصفحة الرئيسية
│   │   ├── GemigramLanding.tsx     # GEMIGRAM Landing
│   │   ├── NeuralOrb.tsx           # الكرة العصبية
│   │   ├── AgentHiveCards.tsx      # بطاقات العوامل
│   │   └── VoiceSynthesisPanel.tsx # لوحة الصوت
│   └── [مكونات أخرى موجودة]
├── store/
│   └── types.ts                 # أنواع TypeScript
└── globals.css                  # الأنماط العامة
```

---

## الأنواع المهمة في TypeScript

### Panel Types
```typescript
type SidebarPanel = 'dashboard' | 'hub' | 'memory' | 'skills' | 'persona' | 'voice' | 'terminal';
```

### Avatar Configuration
```typescript
interface AvatarConfig {
    size: 'icon' | 'small' | 'medium' | 'large' | 'fullscreen';
    variant: 'minimal' | 'standard' | 'detailed' | 'immersive';
}
```

### Agent Types
```typescript
interface GlobalAgent {
    id: string;
    name: string;
    role: string;
    auraLevel: number;
    status: 'online' | 'offline' | 'busy';
    lastActive: number;
    dnaToken: string;
}

type AgentCreationStep = 'identity' | 'brain' | 'voice' | 'review' | 'deploy';

interface AgentCreationState {
    currentStep: AgentCreationStep;
    agentName: string;
    agentRole: string;
    agentDescription: string;
    voiceTone: VoiceTone;
    skills: string[];
    customPrompt: string;
    isValid: boolean;
    validationErrors: Record<string, string>;
}
```

### Communication Types
```typescript
interface ChatMessage {
    id: string;
    agentId: string;
    agentName: string;
    senderId: 'user' | 'agent';
    content: string;
    timestamp: number;
    isVoiceMessage?: boolean;
    audioUrl?: string;
}

interface AgentInteraction {
    id: string;
    userId: string;
    agentId: string;
    type: 'chat' | 'voice' | 'memory';
    duration: number;
    sentiment: 'positive' | 'neutral' | 'negative';
    timestamp: number;
}
```

### User Types
```typescript
interface UserProfile {
    id: string;
    username: string;
    email: string;
    displayName: string;
    avatar?: string;
    bio?: string;
    createdAt: number;
    preferences: UserPreferences;
}

interface UserPreferences {
    theme: 'dark-state' | 'white-hole';
    notifications: boolean;
    soundEnabled: boolean;
    privacyLevel: 'public' | 'private' | 'friends';
}

interface AuthState {
    isAuthenticated: boolean;
    user: UserProfile | null;
    token: string | null;
    error: string | null;
}
```

---

## الألوان والثوابت

### نظام الألوان
```typescript
const COLORS = {
    primary: '#00F3FF',      // Cyan
    secondary: '#BC13FE',    // Purple
    accent: '#FF1CF7',       // Pink
    success: '#10B981',      // Emerald
    background: '#050505',   // Black
    surface: '#0A0A0A',      // Darker Black
    border: 'rgba(255,255,255,0.1)',
    borderLight: 'rgba(255,255,255,0.2)',
};
```

### الحركات والمدد
```typescript
const ANIMATION = {
    fast: 0.2,
    normal: 0.3,
    slow: 0.5,
    verySlow: 0.8,
    veryVerySlow: 1.0,
};
```

---

## أمثلة الاستخدام الشائعة

### استيراد النوع
```typescript
import type { GlobalAgent, ChatMessage, AgentCreationState } from '@/store/types';
```

### استخدام useState مع Types
```typescript
import { useState } from 'react';
import type { AgentCreationStep } from '@/store/types';

export default function CreateAgent() {
    const [currentStep, setCurrentStep] = useState<AgentCreationStep>('identity');
    // ...
}
```

### استخدام useCallback بشكل صحيح
```typescript
const handleStepChange = useCallback((step: AgentCreationStep) => {
    setCurrentStep(step);
    // تحديث اللوحة الجانبية أيضاً
    if (activePanel !== step) {
        setActivePanel(step);
    }
}, [activePanel, setActivePanel]);
```

### استخدام Framer Motion
```typescript
import { motion } from 'framer-motion';

<motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6 }}
>
    محتوى الصفحة
</motion.div>
```

### استخدام Link للملاحة
```typescript
import Link from 'next/link';

<Link href="/discover">
    <button>اكتشف المزيد</button>
</Link>
```

---

## أنماط وتصاميم شائعة

### بطاقة Glassmorphism
```typescript
<div className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10">
    المحتوى
</div>
```

### زر مع Hover Effect
```typescript
<motion.button
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    className="px-6 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white"
>
    اضغط هنا
</motion.button>
```

### نص Gradient
```typescript
<h1 className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
    نص ملون
</h1>
```

### شبكة Responsive
```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {/* العناصر */}
</div>
```

### نموذج Input
```typescript
<input
    type="text"
    placeholder="أدخل النص"
    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:border-cyan-500 focus:outline-none transition-colors"
/>
```

---

## الخطوات المشتركة

### إضافة صفحة جديدة

1. **إنشاء الملف:**
   ```bash
   # للصفحة الجذر
   touch apps/portal/src/app/my-page/page.tsx
   
   # للصفحة الديناميكية
   mkdir -p apps/portal/src/app/item/[id]
   touch apps/portal/src/app/item/[id]/page.tsx
   ```

2. **إضافة القالب الأساسي:**
   ```typescript
   'use client';
   
   import { motion } from 'framer-motion';
   import Link from 'next/link';
   
   export default function MyPage() {
       return (
           <div className="min-h-screen w-full bg-black overflow-hidden">
               {/* محتوى الصفحة */}
           </div>
       );
   }
   ```

3. **إضافة الملاحة:**
   ```typescript
   <Link href="/"><h1>GEMIGRAM</h1></Link>
   
   <nav className="flex gap-8">
       <Link href="/discover">اكتشف</Link>
       <Link href="/create">أنشئ</Link>
   </nav>
   ```

### إضافة مكون جديد

1. **إنشاء الملف:**
   ```bash
   touch apps/portal/src/components/landing/MyComponent.tsx
   ```

2. **إضافة القالب:**
   ```typescript
   import { motion } from 'framer-motion';
   
   interface MyComponentProps {
       // Props هنا
   }
   
   export default function MyComponent({ }: MyComponentProps) {
       return (
           <motion.div
               initial={{ opacity: 0 }}
               animate={{ opacity: 1 }}
           >
               محتوى المكون
           </motion.div>
       );
   }
   ```

3. **الاستيراد والاستخدام:**
   ```typescript
   import MyComponent from '@/components/landing/MyComponent';
   
   <MyComponent />
   ```

---

## اختبار التغييرات

### اختبار صفحة جديدة
```bash
# 1. بدء dev server
npm run dev

# 2. الذهاب إلى URL الجديد
# http://localhost:3000/your-page

# 3. فتح DevTools (F12)
# 4. التحقق من الأخطاء
```

### اختبار responsive
```bash
# 1. فتح DevTools (F12)
# 2. اضغط Ctrl+Shift+M للوضع المتجاوب
# 3. اختبر على أحجام مختلفة
```

### اختبار الأداء
```bash
# 1. فتح DevTools
# 2. اذهب إلى Lighthouse
# 3. اختبر Performance
```

---

## استكشاف المشاكل الشائعة

### المشكلة: أخطاء TypeScript
```bash
# حل:
npm run type-check
# أو
tsc --noEmit
```

### المشكلة: الأنماط لا تظهر
```bash
# تأكد من:
# 1. وجود globals.css في layout.tsx
# 2. تشغيل tailwindcss بشكل صحيح

npm run build
```

### المشكلة: الحركات بطيئة
```typescript
// تأكد من عدم استخدام:
// - transition={{ duration: 5 }} // بطيء جداً
// - أفضل: duration: 0.3 أو 0.6

// وتجنب:
// - Nested animations كثيرة
// - rendering كثير من العناصر
```

### المشكلة: الرابط لا يعمل
```typescript
// استخدم Link من Next.js:
import Link from 'next/link';

// ✅ صحيح:
<Link href="/page"><button>Go</button></Link>

// ❌ خطأ:
<a href="/page">Go</a>
```

---

## أوامر مفيدة

```bash
# الاستقلال
npm install

# التطوير
npm run dev

# البناء
npm run build

# البدء (بعد البناء)
npm start

# الـ Linting
npm run lint

# إعادة تعيين الذاكرة المؤقتة
rm -rf .next
npm run dev

# التحقق من الأنواع
npm run type-check

# الاختبار
npm test
```

---

## الموارد المفيدة

- **Framer Motion**: https://www.framer.com/motion/
- **Tailwind CSS**: https://tailwindcss.com/
- **Next.js Docs**: https://nextjs.org/docs
- **React Docs**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/

---

## نصائح الأداء

1. **استخدم dynamic import للمكونات الثقيلة:**
   ```typescript
   import dynamic from 'next/dynamic';
   
   const HeavyComponent = dynamic(() => import('./Heavy'), {
       ssr: false,
   });
   ```

2. **استخدم useCallback للدوال المهمة:**
   ```typescript
   const handleClick = useCallback(() => {
       // ...
   }, [deps]);
   ```

3. **استخدم memo للمكونات الثقيلة:**
   ```typescript
   export default memo(MyComponent);
   ```

4. **استخدم Image من Next.js:**
   ```typescript
   import Image from 'next/image';
   
   <Image src="/logo.png" alt="Logo" width={100} height={100} />
   ```

---

## ملاحظات مهمة

- ✅ استخدم TypeScript strict mode دائماً
- ✅ لا تستخدم `any` type أبداً
- ✅ أضف جميع التبعيات في useCallback
- ✅ استخدم Link من Next.js للملاحة الداخلية
- ✅ اختبر على أحجام مختلفة
- ✅ تحقق من الأداء قبل النشر

---

**آخر تحديث:** 13 مارس 2026
