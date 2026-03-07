---
name: codebase-organization
description: Organize codebase structure, clean up files, and update documentation with bilingual Arabic/English README format. Use when cleaning up the project, updating docs, or preparing for releases.
---

# Codebase Organization & Documentation Cleanup

## Purpose | الهدف

تنظيم هيكل الكودبيس، تنظيف الملفات غير الضرورية، وتحديث جميع الوثائق وملفات README لتعكس أحدث التغييرات مع الحفاظ على التنسيق ثنائي اللغة (عربي/إنجليزي).

Organize the codebase structure, clean up unnecessary files, and update all documentation and README files to reflect the latest changes while maintaining bilingual (Arabic/English) format.

---

## Workflow Steps

### Phase 1: Analysis | التحليل

1. **Scan directory structure**
   - Identify outdated documentation files
   - Find duplicate or obsolete files
   - Check for broken file references

2. **Review recent changes**
   - Check git history for new features
   - Identify completed phases from plans
   - Note any architectural changes

3. **Audit existing documentation**
   - Compare README content with actual implementation
   - Verify all feature descriptions are accurate
   - Check if badges and links are current

### Phase 2: Cleanup | التنظيف

#### Files to Remove/Delete

```bash
# Temporary files
*.log (except critical logs)
*.tmp, *.temp
__pycache__/ (in docs or public dirs)
.pytest_cache/ (in docs)
node_modules/ (should be in .gitignore)
venv/, .venv/ (should be in .gitignore)

# Outdated documentation
docs/drafts/*.md (if marked as draft > 6 months)
plans/completed/*.md (move to archive/)
old_readme.md, README_OLD.md, etc.

# Build artifacts
dist/, build/ (unless needed)
.next/ (in apps/portal)
*.egg-info/
```

#### Files to Archive

```bash
# Move to archive/ directory
- plans/aether-v3-avatar-system-plan.md (if completed)
- Completed phase plans older than 3 months
- Deprecated architecture docs
```

#### Files to Reorganize

```
Current Structure → Proposed Structure:

AETHER_INDEX.md → docs/index/AETHER_INDEX.md
aether_agents.log → logs/aether_agents.log
test_output.log → logs/test_output.log

brain/ → docs/brain/ (or keep if it's data storage)
plans/ → docs/plans/ (or keep separate)
```

### Phase 3: Update Main README

#### Critical Updates Needed

Based on recent Galaxy Orchestration implementation:

1. **Add Phase H Section**
   ```markdown
   ## 🌌 Phase H: Galaxy Orchestration ···· COMPLETE
   
   - ✅ Gravity-based AI agent routing
   - ✅ Circuit breaker fallback system
   - ✅ Per-galaxy policy enforcement
   - ✅ Cinematic rollback events
   - ✅ 25 passing tests (unit + integration)
   ```

2. **Update Architecture Diagram**
   Add galaxy orchestration layer to mermaid diagram

3. **Update Performance Benchmarks**
   Add handover latency and success rate metrics

4. **Add New Badges**
   ```markdown
   <a href="#"><img src="https://img.shields.io/badge/Galaxy_Orchestration-Complete-success?style=for-the-badge" alt="Galaxy Orchestration"/></a>
   <a href="#"><img src="https://img.shields.io/badge/E2E_Tests-Playwright-orange?style=for-the-badge" alt="E2E Tests"/></a>
   ```

5. **Update Credits Section**
   Ensure all contributors are listed

#### Bilingual Format Rules

✅ **Do:**
- Keep all section headers in English + Arabic
- Preserve badge placement and styling
- Maintain credit sections exactly as-is
- Keep images and banners in original positions
- Translate technical terms accurately

❌ **Don't:**
- Remove existing sections without archiving
- Change badge URLs or styles
- Modify contributor information
- Delete historical context

### Phase 4: Create/Update Supporting Docs

#### Essential Documentation

1. **GALAXY_ORCHESTRATION.md** (NEW)
   ```markdown
   # Galaxy Orchestration System
   
   Complete guide to gravity-based routing, fallback strategies, and policy enforcement.
   
   ## Components
   - GravityRouter
   - FallbackStrategy  
   - GalaxyPolicyEnforcer
   
   ## Usage Examples
   ## Testing Strategy
   ```

2. **E2E_TESTING_GUIDE.md** (UPDATE)
   - Already exists in apps/portal/
   - Ensure it's linked from main README

3. **ARCHITECTURE.md** (UPDATE)
   - Add galaxy orchestration layer
   - Update component diagrams
   - Include handover protocol details

4. **TESTING.md** (CREATE)
   ```markdown
   # Testing Strategy
   
   ## Unit Tests (Vitest)
   ## Integration Tests
   ## E2E Tests (Playwright)
   ## Performance Benchmarks
   ```

### Phase 5: Verification

#### Checklist

- [ ] All file references in README work
- [ ] No broken internal links
- [ ] Badges display correctly
- [ ] Images load properly
- [ ] Arabic translations are accurate
- [ ] Technical terms consistent
- [ ] Code examples tested and working
- [ ] Version numbers updated
- [ ] Phase completion status accurate
- [ ] Credits section complete

#### Smoke Tests

```bash
# Test that critical paths work
cd /path/to/project

# Run unit tests
npm test -- apps/portal/src/__tests__/e2e-browser.test.ts
python -m pytest tests/unit/test_galaxy_orchestration.py -v

# Check README renders correctly
cat README.md | head -50

# Verify file structure
find . -name "*.md" -type f | grep -v node_modules | sort
```

---

## File Structure Template

```
Aether-Voice-OS/
├── .github/                    # GitHub configuration
├── .qoder/                     # Qoder skills (keep!)
├── .vscode/                    # VS Code settings
├── apps/
│   └── portal/                 # Next.js frontend
│       ├── e2e/               # Playwright tests
│       ├── src/
│       │   ├── __tests__/     # Vitest tests
│       │   └── components/
│       ├── E2E_TESTING_GUIDE.md
│       └── playwright.config.ts
├── core/                       # Backend core modules
│   ├── ai/
│   │   └── orchestrator/      # Galaxy orchestration
│   └── ...
├── docs/                       # Documentation
│   ├── assets/                # Images and banners
│   ├── audits/                # Audit reports
│   ├── brain/                 # Brain system docs
│   ├── generated/             # Auto-generated docs
│   ├── index/                 # Index files
│   ├── plans/                 # Architecture plans
│   └── TESTING.md            # Testing strategy
├── logs/                       # Log files (create)
│   ├── aether_agents.log
│   └── test_output.log
├── plans/                      # Active plans
│   └── aether-v3-living-workspace-plan.md
├── tests/                      # Python tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── tools/                      # CLI tools
├── AETHER_INDEX.md            # Main index (move to docs/)
├── README.md                  # ⚠️ MAIN README - DO NOT BREAK
├── LICENSE
└── requirements.txt
```

---

## README Template Sections

Maintain this exact order:

1. **Header Banner & Avatar** (preserve images)
2. **Badges Row** (keep all, add new ones at end)
3. **Table of Contents** (update page anchors)
4. **The Problem** (keep as-is)
5. **The Vision | الرؤية** (bilingual - preserve)
6. **Demo & Showcase** (update if new demo exists)
7. **Thalamic Gate v2** (preserve technical details)
8. **Real-World Impact | الأثر الواقعي** (preserve tables)
9. **Performance Benchmarks** (update with new metrics)
10. **Use Cases** (preserve)
11. **For Judges** (preserve for challenge)
12. **Architecture | الهندسة المعمارية** (UPDATE with galaxy)
13. **Getting Started | البداية** (verify commands work)
14. **Package System | نظام الحزم** (preserve)
15. **Gateway Protocol | بروتوكول البوابة** (preserve)
16. **Roadmap** (UPDATE with completed phases)
17. **FAQ** (preserve)
18. **Troubleshooting** (preserve)
19. **Project Status | حالة المشروع** (UPDATE)
20. **Stargazers & Contributors** (preserve)
21. **Special Thanks 🙏** (preserve)
22. **Credits | الفريق** (PRESERVE EXACTLY)
23. **License | الرخصة** (preserve)
24. **Footer Banner** (preserve)

---

## Common Patterns

### Adding New Features to README

```markdown
## 🆕 [Feature Name] | [الاسم بالعربية]

Brief description in English.

وصف مختصر بالعربية.

Key Features:
- Feature 1
- Feature 2

المميزات الرئيسية:
- الميزة ١
- الميزة ٢
```

### Updating Phase Status

```markdown
```
✅ Phase X: [Phase Name] ················· COMPLETE
🔄 Phase Y: [Phase Name] ················· IN PROGRESS
⏳ Phase Z: [Phase Name] ················· PLANNED
```
```

### Adding Test Coverage Badge

```markdown
<a href="#"><img src="https://img.shields.io/badge/Unit_Tests-25_Passing-brightgreen?style=for-the-badge" alt="Unit Tests"/></a>
<a href="#"><img src="https://img.shields.io/badge/E2E_Tests-Playwright-orange?style=for-the-badge" alt="E2E Tests"/></a>
```

---

## Scripts

### cleanup_docs.py

```python
#!/usr/bin/env python3
"""
Documentation Cleanup Script

Removes temporary files, archives old plans, and organizes docs.
"""

import os
import shutil
from pathlib import Path

def cleanup():
    root = Path('.')
    
    # Patterns to remove (excluding critical dirs)
    patterns = [
        '**/*.log',
        '**/__pycache__/',
        '**/.pytest_cache/',
        '**/*.tmp',
        '**/*.pyc',
    ]
    
    for pattern in patterns:
        for file in root.glob(pattern):
            if 'node_modules' not in str(file) and 'venv' not in str(file):
                print(f"Removing: {file}")
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
    
    # Archive old plans
    plans_dir = root / 'plans'
    archive_dir = root / 'archive' / 'plans'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Move completed plans older than 3 months
    # (Implementation left as exercise)
    
    print("Cleanup complete!")

if __name__ == '__main__':
    cleanup()
```

---

## Anti-Patterns

### ❌ Don't Do This

1. **Deleting Historical Context**
   - Never remove old README sections without archiving
   - Preserve evolution of the project

2. **Breaking Bilingual Format**
   - Don't translate only one language
   - Keep English and Arabic parallel

3. **Removing Credits**
   - Never modify contributor sections
   - Preserve attribution exactly

4. **Changing Image Paths**
   - Don't move assets without updating references
   - Test all image links after reorganization

5. **Inconsistent Terminology**
   - Use same Arabic translation throughout
   - Maintain glossary if needed

### ✅ Best Practices

1. **Version Control First**
   - Commit before major cleanup
   - Use branches for large reorganizations

2. **Test Links**
   - Verify all internal hyperlinks work
   - Check external URLs aren't broken

3. **Preserve Formatting**
   - Match existing markdown style
   - Keep badge styles consistent

4. **Document Changes**
   - Add changelog entry
   - Note what was moved/updated

5. **Get Feedback**
   - Review changes with team
   - Verify nothing critical removed

---

## Summary Checklist

Before finalizing codebase organization:

### Structure
- [ ] Unnecessary files removed
- [ ] Old plans archived
- [ ] Logs moved to logs/ directory
- [ ] Test files organized
- [ ] Docs directory structured properly

### Documentation
- [ ] README.md updated with latest features
- [ ] Galaxy Orchestration documented
- [ ] E2E testing guide linked
- [ ] Architecture diagrams current
- [ ] Phase status accurate

### Bilingual Quality
- [ ] All English sections have Arabic equivalent
- [ ] Technical terms translated consistently
- [ ] Headers maintain English | Arabic format
- [ ] No untranslated paragraphs (except code)

### Preservation
- [ ] All badges preserved and working
- [ ] Images still load correctly
- [ ] Credits section untouched
- [ ] Special thanks preserved
- [ ] License section intact

### Verification
- [ ] All file references valid
- [ ] No broken internal links
- [ ] Smoke tests passing
- [ ] Git status clean (only intended changes)
- [ ] Ready to commit

---

## Resources

- [Markdown Guide](https://www.markdownguide.org)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [Keep a Changelog](https://keepachangelog.com)
- [Documentation Driven Development](https://documentation.divio.com/)
