# 📦 `.ath` Package Specification

> Aether Identity Packages — the DNA format for AI agent personas.

## Overview

An `.ath` (Aether) package encapsulates an agent's complete identity, capabilities,
and autonomous behaviors into a portable, verifiable archive.

## Package Structure

```
<package_name>/
├── manifest.json        # Metadata, capabilities, version
├── Soul.md              # Core persona instructions
├── Skills.md            # Available tools and integrations
├── heartbeat.md         # Autonomous background routines
├── checksums.sha256     # Integrity verification
└── assets/              # Optional static resources
    ├── voice_profile.json
    └── avatar.png
```

---

## manifest.json Schema

```json
{
  "name": "AetherCore",
  "version": "1.0.0",
  "author": "The Aether Architect",
  "description": "Core Aether persona with full multimodal capabilities",
  "capabilities": ["voice.stream", "vision.render", "tool.execute"],
  "min_runtime": "0.1.0",
  "rbac": {
    "workspace": "ro",
    "network": "restricted",
    "filesystem": "sandbox"
  },
  "checksum_algorithm": "sha256"
}
```

### Field Reference

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | ✅ | Unique package identifier |
| `version` | semver | ✅ | Package version (Major.Minor.Patch) |
| `author` | string | ✅ | Package author or organization |
| `capabilities` | string[] | ✅ | Requested permissions |
| `min_runtime` | semver | ❌ | Minimum Aether OS version |
| `rbac` | object | ❌ | Fine-grained access controls |

---

## Capability RBAC Matrix

| Capability | Risk | Description | Auto-Granted |
| :--- | :--- | :--- | :--- |
| `voice.stream` | Low | Real-time audio I/O | ✅ |
| `vision.render` | Medium | UI/Canvas manipulation | ✅ |
| `tool.execute` | High | System command execution | ❌ |
| `workspace.rw` | Critical | Write access to codebase | ❌ |

---

## Integrity Verification

All packages must include a `checksums.sha256` file:

```
e3b0c44298fc1c149afbf4c8996fb924...  manifest.json
a7ffc6f8bf1ed76651c14756a061d662...  Soul.md
d7a8fbb307d7809469ca9abcb0082e4f...  Skills.md
```

### Verification Flow

```python
from core.registry import AthPackage

pkg = AthPackage("brain/packages/AetherCore")
assert pkg.verify_integrity(), "Package integrity check failed!"
```

---

## Hot-Swap Protocol

1. New package is dropped into `brain/packages/`.
2. `AetherRegistry.scan()` detects the new directory.
3. Integrity verification runs automatically.
4. If valid, state migration transfers context from old to new persona.
5. Old package is archived (not deleted) for rollback safety.

---

## Best Practices

- **Keep Soul.md under 500 tokens** — concise identity prevents context dilution.
- **Version bump** on every capability change using semver.
- **Never include secrets** in packages — use environment injection.
- **Test locally** before deploying to production registry.
