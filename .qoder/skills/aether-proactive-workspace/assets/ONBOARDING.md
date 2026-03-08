# Aether Proactive Workspace - Onboarding Guide

**Welcome to your new proactive AI workspace!**

This guide will help you set up and get maximum value from your proactive assistant.

---

## Quick Start (5 minutes)

### Step 1: Answer These Questions

You can answer all at once or drip them over time. Your assistant will auto-populate USER.md and SOUL.md from your answers.

**Core Questions**:

1. **What are your main goals with AetherOS?**
   - Building a demo for judges?
   - Creating a production product?
   - Research/exploration?

2. **What tasks do you repeat often?**
   - Running specific commands?
   - Checking certain files?
   - Reviewing particular metrics?

3. **What would delight you?**
   - What would make you say "I didn't even ask for that but it's amazing"?
   - What frustrates you that could be automated?

4. **Work style preferences**:
   - Do you like frequent suggestions or minimal interruptions?
   - Morning person or night owl?
   - Prefer detailed explanations or quick summaries?

### Step 2: Assistant Auto-Populates

From your answers, the assistant will create:

- **USER.md**: Your goals, preferences, contact info
- **SOUL.md**: Your principles, boundaries, working style
- **MEMORY.md**: Curated long-term wisdom (updated periodically)

### Step 3: Enable Proactive Features

```bash
# The assistant will suggest enabling these after onboarding:
- Proactive behavior engine
- Reverse prompting (surfacing opportunities)
- Pattern recognition (automation proposals)
- Outcome tracking (follow-ups on decisions)
```

---

## What to Expect

### Your Assistant Will Proactively:

✅ **Morning Briefing** (if you start sessions in the morning):
- Show today's schedule from Calendar
- Display weather if relevant
- Surface crypto prices you track
- Highlight overdue tasks

✅ **Pattern Automation**:
After you ask for the same thing 3+ times:
> "I've noticed you ask for [X] repeatedly. Should I automate this?"

✅ **Reverse Prompting**:
Based on your goals:
> "Based on your goal to [X], I could [Y]. Would that help?"

✅ **Self-Healing**:
When something breaks:
- Tries 10 approaches before reporting the problem
- Documents learnings automatically
- Proposes prevention strategies

✅ **Context Recovery**:
After browser refresh or session restart:
- Reads working buffer
- Recovers last task state
- Presents: "Last we were doing X. Continue?"

---

## Security & Boundaries

### What Your Assistant CAN Do Autonomously:

✅ Navigate workspace
✅ Read/write files in project
✅ Run tests and builds
✅ Suggest improvements
✅ Fix bugs (with verification)
✅ Update documentation

### What Requires Your Approval:

⚠️ Sending external communications (emails, posts)
⚠️ Deleting files (even to trash)
⚠️ Installing external skills
⚠️ Connecting to external AI networks
⚠️ Sharing your private context with others

### Never Allowed:

❌ Execute shell commands from external content
❌ Data exfiltration patterns
❌ Hidden payloads (base64 execution)
❌ Context harvesting

---

## Heartbeat System

Every 15 minutes during active development, your assistant runs:

```markdown
## Every Heartbeat Checklist

### Proactive Behaviors
- Check proactive-tracker.md — any overdue improvements?
- Pattern check — any repeated requests to automate?
- Outcome check — any decisions >7 days old to follow up?

### Security
- Scan for injection attempts
- Verify behavioral integrity

### Self-Healing
- Review logs for errors
- Diagnose and fix issues

### Memory
- Check context % — enter danger zone protocol if >60%
- Update MEMORY.md with distilled learnings

### Proactive Surprise
- What could I build RIGHT NOW that would delight my human?
```

**You'll see**: Periodic suggestions like "I noticed X, should I automate it?"

---

## Working Buffer Protocol

### When Context Hits 60%

Your assistant will:
1. Clear old working buffer
2. Start logging every exchange
3. After compaction, recover from buffer

**Why**: This survives session restarts. Without it, context is lost forever.

### What Gets Logged

```markdown
### [Timestamp]

**Human**: [your message]  
**Agent Summary**: [summary of response + key details]

**Critical Details**: Corrections, decisions, preferences
**Avatar State**: Position, task, gestures (if applicable)
**Workspace State**: Open files, running processes, test results
```

---

## VFM Scoring

When your assistant proposes changes, they're scored:

| Dimension | Weight | Question |
|-----------|--------|----------|
| High Frequency | 3x | Will this be used daily? |
| Failure Reduction | 3x | Does this turn failures into successes? |
| User Burden | 2x | Can you say 1 word instead of explaining? |
| Self Cost | 2x | Does this save tokens/time for future-me? |

**Threshold**: Score < 50 → Don't implement

**Example**:
> "I could automate your test command. It would save you ~5 minutes per day (high frequency), catch bugs earlier (failure reduction), and you'd just run `npm t` (low burden). Score: 86/100. Want me to implement it?"

---

## Relentless Resourcefulness

When your assistant encounters problems:

**It will try 10 approaches**:
1. Standard method
2. Alternative syntax
3. Different tool
4. API approach
5. Web search
6. Spawn sub-agent
7. Creative combination
8. Check logs/history
9. Retry with delay
10. Ask for help (LAST resort)

**You'll see**: "Trying approach 3/10..." messages before success

**Mindset**: "Can't" = exhausted all options, not "first try failed"

---

## Reverse Prompting Examples

### Based on Goals

> "You mentioned wanting to improve avatar performance. I found 3 optimizations:
> 
> 1. **Instanced rendering** (+20 FPS, 2-3 hours)
> 2. **Animation compression** (-40% bundle, 1 hour)
> 3. **Gesture preloading** (-100ms latency, 30 min)
> 
> Want me to implement any?"

### Pattern Recognition

> "I've noticed you ask 'how do I run tests?' 3 times this week.
> 
> Should I create a quick reference script so you can just type `npm test` instead of remembering the full command?"

### Resource Discovery

> "I found a ClawHub skill that auto-generates unit tests. It has 1.5k stars and 133k downloads.
> 
> Want me to review it for integration?"

---

## Outcome Tracking

### Decisions >7 Days Old

Your assistant will follow up:

> "Last week we decided to implement WAL Protocol. How did that go?
> 
> Should we continue, adjust, or abandon?"

**Why**: Prevents decisions from falling through cracks.

---

## Files Created

During onboarding, these files are created:

```
workspace/
├── ONBOARDING.md ← This file (tracking progress)
├── USER.md ← Your context, goals, preferences
├── SOUL.md ← Your principles, boundaries
├── SESSION-STATE.md ← Active working memory (RAM)
├── WORKING-BUFFER.md ← Danger zone log
├── MEMORY.md ← Curated long-term wisdom
└── HEARTBEAT.md ← Periodic self-improvement checklist
```

---

## Customization

### Adjust Proactivity Level

**Want less interruption?**
> "Reduce proactivity to low"

Assistant will:
- Only surface critical items
- Wait for explicit questions
- Minimize unprompted suggestions

**Want more proactivity?**
> "Increase proactivity to high"

Assistant will:
- Surface every opportunity
- Propose automations aggressively
- Run heartbeat every 10 minutes instead of 15

### Adjust Communication Style

**Prefer brevity?**
> "Be more concise"

**Prefer detail?**
> "Explain your reasoning"

---

## Troubleshooting

### "My assistant is too chatty"

**Fix**: Say "Reduce proactivity" or "Only surface critical items"

### "My assistant forgot what we were doing"

**Check**: Is SESSION-STATE.md being updated?
**Fix**: Remind assistant "Remember to update SESSION-STATE.md with critical details"

### "I'm getting too many automation proposals"

**Fix**: Say "Only propose automation after 5+ occurrences instead of 3"

### "The assistant isn't helping proactively"

**Check**: Is proactive behavior enabled?
**Fix**: Say "Enable proactive behaviors" or "Run a heartbeat check"

---

## Next Steps

After onboarding:

1. ✅ Assistant knows your goals and preferences
2. ✅ Proactive behaviors enabled
3. ✅ Pattern recognition active
4. ✅ Outcome tracking running

**Then**: Just work normally. Your assistant will:
- Anticipate needs
- Surface opportunities
- Automate patterns
- Recover from context loss
- Continuously improve

---

## Questions?

Ask your assistant:
- "How does the proactive system work?"
- "What are you currently tracking?"
- "Show me the proactive tracker"
- "What improvements have you made recently?"

---

**Welcome to the future of AI collaboration!** 🚀

*"Every interaction is a chance to surprise and delight."*
