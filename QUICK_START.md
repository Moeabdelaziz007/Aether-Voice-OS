# GEMIGRAM - دليل البدء السريع

## التثبيت والتشغيل

### 1. تثبيت المتطلبات
```bash
cd apps/portal
npm install
```

### 2. تشغيل التطبيق
```bash
npm run dev
```

التطبيق سيكون متاحاً على: `http://localhost:3000`

---

## مسارات الصفحات الرئيسية

| المسار | الوصف | الحالة |
|--------|-------|--------|
| `/` | الصفحة الرئيسية مع GEMIGRAM Landing | ✅ جديد |
| `/create` | إنشاء وكيل جديد | ✅ جديد |
| `/chat` | واجهة الدردشة مع الوكلاء | ✅ جديد |
| `/discover` | اكتشاف الوكلاء | ✅ جديد |
| `/hub` | مركز الوكلاء | ✅ جديد |
| `/profile` | الملف الشخصي | ✅ جديد |
| `/settings` | الإعدادات | ✅ جديد |
| `/agent/:id` | تفاصيل الوكيل | ✅ جديد |
| `/login` | تسجيل الدخول | ✅ موجود |

---

## المكونات الجديدة والمهمة

### GemigramLanding
```typescript
import GemigramLanding from '@/components/landing/GemigramLanding';

<GemigramLanding 
  onConnectClick={() => handleConnect()}
  onCreateAgentClick={() => handleCreateAgent()}
/>
```

### NeuralOrb
```typescript
import NeuralOrb from '@/components/landing/NeuralOrb';

<NeuralOrb isHovering={isHovering} />
```

### AgentHiveCards
```typescript
import AgentHiveCards from '@/components/landing/AgentHiveCards';

<AgentHiveCards agents={agentsList} />
```

### VoiceSynthesisPanel
```typescript
import VoiceSynthesisPanel from '@/components/landing/VoiceSynthesisPanel';

<VoiceSynthesisPanel />
```

---

## الأنواع الجديدة المهمة

### SidebarPanel
```typescript
import { SidebarPanel } from '@/store/types';

const [activePanel, setActivePanel] = useState<SidebarPanel>('dashboard');
```

### AvatarConfig
```typescript
import { AvatarConfig } from '@/store/types';

const avatarConfig: AvatarConfig = { 
  size: 'medium', 
  variant: 'detailed' 
};
```

### AgentCreationStep
```typescript
import { AgentCreationStep } from '@/store/types';

const [step, setStep] = useState<AgentCreationStep>('identity');
```

### ChatMessage
```typescript
import { ChatMessage } from '@/store/types';

const [messages, setMessages] = useState<ChatMessage[]>([]);
```

---

## أمثلة الاستخدام

### إضافة وكيل جديد
```typescript
const newAgent: GlobalAgent = {
  id: 'agent-001',
  name: 'Nova',
  role: 'Creative Guide',
  auraLevel: 95,
  status: 'online',
  lastActive: Date.now(),
  dnaToken: 'NOVA-DNA-001',
};
```

### إضافة رسالة دردشة
```typescript
const newMessage: ChatMessage = {
  id: Date.now().toString(),
  agentId: 'nova-01',
  agentName: 'Nova',
  senderId: 'user',
  content: 'Hello, Nova!',
  timestamp: Date.now(),
};
```

### إضافة حدث نشاط
```typescript
const activity = {
  action: 'Created agent "Nova Prime"',
  time: '2 hours ago'
};
```

---

## اختبار الصفحات

### اختبار الصفحة الرئيسية
1. اذهب إلى `http://localhost:3000`
2. يجب أن ترى GEMIGRAM Landing مع NeuralOrb المتحرك
3. جرب هover على الأزرار والبطاقات

### اختبار Create Agent
1. اذهب إلى `http://localhost:3000/create`
2. انتقل عبر 5 خطوات
3. تحقق من شريط التقدم

### اختبار Chat
1. اذهب إلى `http://localhost:3000/chat`
2. اختر وكيل من القائمة الجانبية
3. أرسل رسالة وشاهد الرد المحاكى

---

## استكشاف الأخطاء

### المشكلة: الصفحات لا تحمل
```bash
# تأكد من:
npm install
npm run dev

# تحقق من عدم وجود أخطاء في console
# افتح DevTools (F12)
```

### المشكلة: الأنماط لا تظهر
```bash
# أعد بناء Tailwind CSS:
npm run build

# تأكد من وجود globals.css مستورد في layout.tsx
```

### المشكلة: الحركات لا تعمل
```bash
# تحقق من Framer Motion مثبت:
npm list framer-motion

# يجب أن يكون الإصدار 12.34.5+
```

---

## أوامر مفيدة

```bash
# بناء للإنتاج
npm run build

# معاينة الإنتاج محلياً
npm run build
npm run start

# التحقق من الأخطاء
npm run lint

# اختبار الأداء
npm run build --analyze

# مسح الذاكرة المؤقتة
rm -rf .next
npm run dev
```

---

## ملاحظات الأداء

- الصفحات الثقيلة تستخدم dynamic import
- جميع الصور مُحسّنة مع Next.js Image
- Framer Motion محسّن للأداء
- CSS محسّن مع PostCSS و Tailwind

---

## الدعم والمساعدة

- تحقق من `IMPLEMENTATION_SUMMARY.md` للتفاصيل الكاملة
- استعرض `GEMIGRAM_IMPLEMENTATION.md` للنظرة العامة
- اطلع على comments في الكود للشرح
- استخدم TypeScript intellisense في محرر الكود

---

## الخطوة التالية

بعد التشغيل الناجح:

1. **استكشف جميع الصفحات** - تأكد من عمل الملاحة
2. **جرب التفاعلات** - اختبر hover و click effects
3. **تحقق من Responsive Design** - استخدم DevTools للقياس المختلفة
4. **اختبر Performance** - استخدم Lighthouse في DevTools
5. **قم بالنشر** - استخدم `vercel deploy` أو platform آخر

---

**آخر تحديث:** 13 مارس 2026
**الحالة:** جاهز للاستخدام الفوري
