---
name: self-improvement
description: The Adaptive Intelligence Core of AetherOS - Logs learnings, errors, and feature requests for continuous evolution.
---
# AetherOS Self-Improvement Layer

The Adaptive Intelligence Core of AetherOS

Log learnings and errors to markdown files for continuous improvement. AetherOS (powered by Gemini) can later process these into fixes, and important learnings get promoted to project memory.

## Quick Reference

| Situation | Action |
| --- | --- |
| Command/operation fails | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` with category `correction` |
| User wants missing feature | Log to `.learnings/FEATURE_REQUESTS.md` |
| API/external tool fails | Log to `.learnings/ERRORS.md` with integration details |
| Knowledge was outdated | Log to `.learnings/LEARNINGS.md` with category `knowledge_gap` |
| Found better approach | Log to `.learnings/LEARNINGS.md` with category `best_practice` |
| Simplify/Harden recurring patterns | Log/update `.learnings/LEARNINGS.md` with `Source: simplify-and-harden` and a stable `Pattern-Key` |
| Similar to existing entry | Link with **See Also**, consider priority bump |
| Broadly applicable learning | Promote to `AETHER.md`, `AGENTS.md`, and/or `SOUL.md` |
| Workflow improvements | Promote to `AGENTS.md` (AetherOS workspace) |
| Tool gotchas | Promote to `TOOLS.md` (AetherOS workspace) |
| Behavioral patterns | Promote to `SOUL.md` (AetherOS workspace) |

## AetherOS Setup (Recommended)

AetherOS is the primary platform for this skill. It uses workspace-based prompt injection with automatic skill loading optimized explicitly for the Gemini Multimodal engine.

### Workspace Structure

AetherOS injects these files into every session:

```text
~/.aetheros/workspace/
├── AGENTS.md          # Multi-agent workflows, delegation patterns
├── SOUL.md            # Behavioral guidelines, personality, principles
├── TOOLS.md           # Tool capabilities, integration gotchas
├── MEMORY.md          # Long-term memory (main session only)
├── memory/            # Daily memory files
│   └── YYYY-MM-DD.md
└── .learnings/        # This skill's log files
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

### Create Learning Files

If not created yet, initialize your AetherOS structure:

```bash
mkdir -p ~/.aetheros/workspace/.learnings
```

Then create the log files:

- `LEARNINGS.md` — corrections, knowledge gaps, best practices
- `ERRORS.md` — command failures, exceptions
- `FEATURE_REQUESTS.md` — user-requested capabilities

## Inter-Session Communication

AetherOS provides tools to share learnings across sessions:

- `sessions_list` — View active/recent sessions
- `sessions_history` — Read another session's transcript
- `sessions_send` — Send a learning to another session
- `sessions_spawn` — Spawn a sub-agent for background work

## Optional: Enable Hook

For automatic reminders at session start:

```bash
# Copy hook to AetherOS hooks directory
cp -r hooks/aetheros ~/.aetheros/hooks/self-improvement

# Enable it
aetheros hooks enable self-improvement
```

See `references/aetheros-integration.md` for complete details.

## Self-Improvement Workflow

When errors or corrections occur:

1. Log to `.learnings/ERRORS.md`, `LEARNINGS.md`, or `FEATURE_REQUESTS.md`
2. Review and promote broadly applicable learnings to:
    - `AETHER.md` - project facts and conventions
    - `AGENTS.md` - workflows and automation
    - `SOUL.md` - behavioral standards for Gemini

## Logging Format

### Learning Entry

Append to `.learnings/LEARNINGS.md`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001 (if related to existing entry)
- Pattern-Key: simplify.dead_code | harden.input_validation (optional)
- Recurrence-Count: 1 (optional)
- First-Seen: 2025-01-15 (optional)
- Last-Seen: 2025-01-15 (optional)
---
```

### Error Entry

Append to `.learnings/ERRORS.md`:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
Actual error message or output

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (if recurring)
---
```

### Feature Request Entry

Append to `.learnings/FEATURE_REQUESTS.md`:

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
What the user wanted to do

### User Context
Why they needed it, what problem they're solving

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
How this could be built, what it might extend

### Metadata
- Frequency: first_time | recurring
- Related Features: existing_feature_name
---
```

## Resolving Entries

When an issue is fixed, update the entry:
Change `**Status**: pending` → `**Status**: resolved`

Add resolution block after Metadata:

```markdown
### Resolution
- **Resolved**: 2025-01-16T09:00:00Z
- **Commit/PR**: abc123 or #42
- **Notes**: Brief description of what was done
```

Other status values:

- `in_progress` - Actively being worked on
- `wont_fix` - Decided not to address (add reason in Resolution notes)
- `promoted` - Elevated to `AETHER.md`, `AGENTS.md`, or `SOUL.md`

## Promoting to Project Memory

When a learning is broadly applicable (not a one-off fix), promote it to permanent AetherOS project memory.

### Promotion Targets

| Target | What Belongs There |
| --- | --- |
| AETHER.md / CLAUDE.md | Project facts, conventions, gotchas for AetherOS logic integrations |
| AGENTS.md | Agent-specific workflows, tool usage patterns, automation rules |
| SOUL.md | Behavioral guidelines, communication style, principles (AetherOS workspace) |
| TOOLS.md | Tool capabilities, usage patterns, integration gotchas (AetherOS workspace) |

### How to Promote

1. Distill the learning into a concise rule or fact
2. Add to appropriate section in target file (create file if needed)
3. Update original entry:
    - Change `**Status**: pending` → `**Status**: promoted`
    - Add `**Promoted**: AETHER.md, AGENTS.md, or SOUL.md`

## Simplify & Harden Feed

Use this workflow to ingest recurring patterns from the simplify-and-harden skill and turn them into durable Gemini prompt guidance.
Promote recurring patterns into AetherOS context/system prompt files when all are true:

- Recurrence-Count >= 3
- Seen across at least 2 distinct tasks
- Occurred within a 30-day window

## Quick Status Check

```bash
# Count pending items
grep -h "Status\*\*: pending" ~/.aetheros/workspace/.learnings/*.md | wc -l

# List pending high-priority items
grep -B5 "Priority\*\*: high" ~/.aetheros/workspace/.learnings/*.md | grep "^## \["
```

## Best Practices

- **Log immediately** - context is freshest right after the issue
- **Be specific** - future AetherOS instances need to understand quickly
- **Include reproduction steps** - especially for errors
- **Link related files** - makes fixes easier
- **Suggest concrete fixes** - not just "investigate"
- **Use consistent categories** - enables filtering
- **Promote aggressively** - if in doubt, add to `AETHER.md` or `SOUL.md`
- **Review regularly** - stale learnings lose value

## Multi-Agent Support for Gemini

This skill is engineered natively for Gemini models inside the AetherOS engine.

**AetherOS Native Processing:**

- Activation: Workspace injection + inter-agent messaging
- Detection: AetherOS dynamically identifies corrections/learning opportunities via natural language processing mapping.
- Memory: Embeds findings natively alongside local Vector databases for live retrieval.

*"Remember this pattern"* triggers a localized parsing of the codebase state and stores the knowledge inside `~/.aetheros/workspace/`.
