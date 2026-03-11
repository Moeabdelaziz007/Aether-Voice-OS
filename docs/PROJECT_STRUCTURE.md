# 🌌 AetherOS: Project Structure Map

This document provides a high-level overview of the AetherOS directory structure and codebase organization.

## 📂 Directory Layout

```mermaid
graph TD
    Root["/ (Root)"]
    Root --> Apps["apps/ (Frontend)"]
    Root --> Backend["core/ (Backend Engine)"]
    Root --> Docs["docs/ (Knowledge Base)"]
    Root --> Scripts["scripts/ (Tools & Deployment)"]
    Root --> Infra["infra/ (Cloud & IaC)"]
    Root --> Tests["tests/ (Validation)"]

    Apps --> Portal["portal/ (Next.js AI Dashboard)"]
    
    Backend --> AI["ai/ (Gemini Live Session)"]
    Backend --> Audio["audio/ (Sensory Processing)"]
    Backend --> Identity["identity/ (.ath Package)"]
    
    Docs --> Audit["audit/ (Security & Performance)"]
    Docs --> Guides["guides/ (Initialization)"]
```

---

### 🏛️ Core Components

| Directory | Purpose |
|:---|:---|
| `apps/portal` | The Next.js 15 Cyberpunk interface for agent management. |
| `core/ai` | Orchestration layer for Gemini 2.0 Multimodal sessions. |
| `core/audio` | Thalamic Gate V2 implementation for low-latency voice. |
| `docs/guides` | Quickstart, environment setup, and integration checklists. |
| `docs/audit` | Comprehensive project audits and performance benchmarks. |
| `scripts/deploy` | CI/CD automation and deployment scripts. |
| `infra` | Firebase/GCP configuration and safety rules. |

### 🛠️ Key Command Hub

- **Start Backend:** `python -m core.engine`
- **Start Portal:** `cd apps/portal && npm run dev`
- **Run Tests:** `pytest tests/`

---
*Aether Architecture // v3.0 Alpha // Confidential*
