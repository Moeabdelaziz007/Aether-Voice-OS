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
  "persona": "The core systems architect for Aether OS...",
  "voice_id": "Puck",
  "language": "ar-EG",
  "capabilities": ["audio.input", "audio.output", "tool.execute"],
  "expertise": {
    "python_coding": 0.95,
    "cloud_architecture": 0.88
  },
  "public_key": "ed25519-public-key-hex",
  "checksum": "sha256-of-all-files-except-this-one"
}
```

### Field Reference

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | ✅ | Unique package identifier (1-64 chars) |
| `version` | semver | ✅ | Package version (e.g., `1.0.0`) |
| `persona` | string | ✅ | Behavioral identity description |
| `capabilities` | string[] | ✅ | Permissions (e.g., `audio.input`, `ui.render`) |
| `voice_id` | string | ❌ | Gemini voice name (Default: `Puck`) |
| `public_key` | hex | ❌ | Ed25519 public key for gateway auth |
| `checksum` | hex | ❌ | SHA256 integrity hash |

---

## Capability Matrix

| Capability | Risk | Description |
| :--- | :--- | :--- |
| `audio.input` | Low | Real-time mic stream access |
| `audio.output` | Low | Speaker playback access |
| `tool.execute` | High | Sandboxed system tool execution |
| `memory.read` | Medium | Read-only access to Firebase long-term memory |
| `ui.render` | Low | Next.js visualizer updates |

---

## Integrity Verification

The `.ath` package uses deterministic SHA256 hashing. The `checksum` in `manifest.json` must match the hash of all other files in the directory (sorted alphabetically).

```python
from core.identity.package import AthPackage

pkg = AthPackage.load(Path("agents/AetherCore"))
# Automatically verifies checksum if present in manifest
```

---

## Expert-Level Expertise Scores

The `expertise` mapping allows the `HiveCoordinator` to select the best agent for a given task:

- `0.0 - 0.3`: Familiarity
- `0.4 - 0.7`: Competency
- `0.8 - 1.0`: Expert Mastery

---

## Best Practices

- **Keep Soul.md under 500 tokens** — concise identity prevents context dilution.
- **Version bump** on every capability change using semver.
- **Never include secrets** in packages — use environment injection.
- **Test locally** before deploying to production registry.
