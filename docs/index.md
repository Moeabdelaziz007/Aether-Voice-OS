# Aether OS Documentation Index | فهرس وثائق Aether OS

Welcome to the Aether OS documentation hub. This index provides quick access to all guides and references.

مرحبًا بك في مركز وثائق Aether OS. يوفر هذا الفهرس وصولاً سريعًا لجميع الأدلة والمراجع.

---

## 📚 Core Documentation | الوثائق الأساسية

### [README.md](../README.md) | الرئيسية

Project overview, features, status, and getting started guide.  
نظرة عامة على المشروع والميزات والحالة ودليل البدء السريع.

**Contents**:

- Project description and vision
- Key features (Thalamic Gate v2, Galaxy Orchestration, etc.)
- Installation instructions
- Usage examples
- Roadmap
- FAQ

---

### [ARCHITECTURE.md](ARCHITECTURE.md) | الهندسة المعمارية

Complete system architecture documentation covering all layers.  
توثيق كامل للهندسة المعمارية يغطي جميع الطبقات.

**Sections**:

1. Audio Capture & Playback (Thalamic Gate v2)
2. Emotion Processing
3. Gemini Live Session
4. Galaxy Orchestration
5. Gateway Protocol
6. Identity & Memory

**Key Concepts**:

- Pipeline architecture with independent layers
- Thread-safe communication via queues
- <2ms latency for audio processing
- 92% emotion detection accuracy

---

### [GALAXY_ORCHESTRATION.md](GALAXY_ORCHESTRATION.md) | تنظيم المجرة

Comprehensive guide to the Galaxy Orchestration System.  
دليل شامل لنظام تنظيم المجرة.

**Topics Covered**:

- Gravity-based routing algorithm
- Circuit breaker fallbacks
- Policy enforcement
- API reference with examples
- Performance metrics

**Formula**:

```
score = 0.35*capability + 0.25*confidence 
        - 0.15*latency - 0.15*load + 0.10*continuity
```

---

### [TESTING.md](TESTING.md) | الاختبار

Complete testing strategy and how-to guide.  
استراتيجية الاختبار الكاملة ودليل الإرشادات.

**Test Types**:

- Unit tests (Vitest + Pytest)
- Integration tests
- E2E tests (Playwright)
- Performance benchmarks

**Quick Start**:

```bash
# Frontend
npm run test
npm run test:e2e

# Backend
pytest tests/unit/
pytest tests/integration/
```

---

### [WORKSPACE_UPDATES.md](WORKSPACE_UPDATES.md) | تحديثات مساحة العمل

Latest updates on avatar system, workspace enhancements, and galaxy orchestration.  
آخر التحديثات على نظام الأفاتار، وتحسينات مساحة العمل، وتنظيم المجرة.

**Recent Updates**:

- Galaxy Orchestration complete ✅
- Avatar mobility system (80% done)
- Workspace canvas and app dock
- Gesture system implementation
- Testing infrastructure

---

## 🧪 Technical Guides | الأدلة التقنية

### Configuration | الإعدادات

- `.env.example` - Environment variables template
- `apps/portal/.env.local.example` - Frontend environment
- `tsconfig.json` - TypeScript configuration
- `pyproject.toml` - Python project config

### Development | التطوير

- `task_runner.py` - Task automation
- `Dockerfile` - Container build instructions
- `docker-compose.yml` - Multi-container setup
- `.github/workflows/` - CI/CD pipelines

### Testing | الاختبار

- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `apps/portal/src/__tests__/` - Frontend tests
- `apps/portal/e2e/` - E2E tests

---

## 📊 Project Status | حالة المشروع

### Current Version | الإصدار الحالي

**3.0-Alpha** (March 2026)

### Completed Phases | المراحل المكتملة

✅ Phase H: Galaxy Orchestration  
✅ All foundation components (A-G)  
✅ Testing infrastructure  

### In Progress | قيد التنفيذ

🔄 Phase 10: Living Workspace Avatar (80%)  
🔄 Multi-agent collaboration framework  

### Next Release | الإصدار التالي

**v3.1** - Voice Controls & Advanced Features  
Expected: Q2 2026

---

## 🔍 Quick Reference | مرجع سريع

### Key Commands | الأوامر الرئيسية

```bash
# Install dependencies
pip install -r requirements.txt
cd apps/portal && npm install

# Run backend
python core/server.py

# Run frontend
cd apps/portal && npm run dev

# Run tests
pytest                    # Backend
npm run test              # Frontend unit
npm run test:e2e          # E2E browser tests

# Build
docker-compose build
docker-compose up
```

### File Structure | هيكل الملفات

```
Aether Live Agent/
├── README.md              # Main documentation
├── docs/                  # Detailed guides
│   ├── ARCHITECTURE.md
│   ├── GALAXY_ORCHESTRATION.md
│   ├── TESTING.md
│   └── WORKSPACE_UPDATES.md
├── plans/                 # Architecture plans
├── core/                  # Backend Python code
├── apps/portal/           # Frontend Next.js app
├── tests/                 # All test suites
└── scripts/               # Utility scripts
```

### Key Components | المكونات الرئيسية

**Backend**:

- `core/engine.py` - Main orchestration engine
- `core/server.py` - FastAPI server
- `core/ai/handover/manager.py` - Multi-agent orchestrator
- `core/audio/` - Audio capture and playback

**Frontend**:

- `apps/portal/src/app/` - Next.js pages
- `apps/portal/src/components/` - React components
- `apps/portal/src/store/` - Zustand state management
- `apps/portal/e2e/` - Playwright tests

---

## 🎯 Getting Started | البدء السريع

### For Developers | للمطورين

1. **Setup Environment**

   ```bash
   cp .env.example .env
   cp apps/portal/.env.local.example apps/portal/.env.local
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   cd apps/portal && npm install
   ```

3. **Run Tests First**

   ```bash
   pytest
   npm run test
   ```

4. **Start Development**

   ```bash
   python core/server.py
   cd apps/portal && npm run dev
   ```

### For Reviewers | للمقيمين

1. **Read Overview**: Start with [README.md](../README.md)
2. **Understand Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. **See Galaxy Routing**: Check [GALAXY_ORCHESTRATION.md](GALAXY_ORCHESTRATION.md)
4. **View Tests**: Look at test files in `tests/` and `apps/portal/e2e/`
5. **Run Demo**: Follow setup in README to run locally

---

## 📞 Support & Contribution | الدعم والمساهمة

### Questions | أسئلة

- Check [FAQ section](../README.md#faq) in README
- Review documentation guides
- Search existing GitHub issues

### Contributing | المساهمة

We welcome contributions! Please see our contribution guidelines (coming soon).

نحن نرحب بالمساهمات! يرجى الاطلاع على إرشادات المساهمة (قريبًا).

### Contact | الاتصال

- **GitHub**: [@Moeabdelaziz007](https://github.com/Moeabdelaziz007)
- **Challenge**: [Gemini Live Agent 2026](https://geminiliveagentchallenge.devpost.com)
- **License**: Apache 2.0

---

## 📈 Documentation Metrics | مقاييس الوثائق

### Coverage | التغطية

- ✅ Architecture: 100% documented
- ✅ Core APIs: Fully documented
- ✅ Testing: Comprehensive guides
- ✅ Examples: Code snippets for all features

### Languages | اللغات

- 🇬🇧 English
- 🇸🇦 Arabic (العربية)

All documentation is bilingual to serve both international and Arabic-speaking developers.

جميع الوثائق ثنائية اللغة لخدمة المطورين الدوليين والناطقين بالعربية.

---

## 🔄 Last Updated | آخر تحديث

**March 7, 2026**  
Version: 3.0-Alpha  
Status: Galaxy Orchestration Complete, Avatar Implementation In Progress

---

*This index is automatically updated with major documentation changes.*  
*يتم تحديث هذا الفهرس تلقائيًا مع التغييرات الكبيرة في الوثائق.*
