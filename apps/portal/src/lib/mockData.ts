/**
 * AetherOS — Mock Data for all Realms.
 * Realistic developer-relevant content. No placeholders.
 */

// ─── Skills ────────────────────────────────────────────────
export interface SkillItem {
    id: string;
    icon: string;
    name: string;
    description: string;
    enabled: boolean;
}

export const MOCK_SKILLS: SkillItem[] = [
    {
        id: "coding",
        icon: "💻",
        name: "Coding",
        description: "Write, refactor, and optimize code across 30+ languages with context-aware completions.",
        enabled: true,
    },
    {
        id: "debugging",
        icon: "🐛",
        name: "Debugging",
        description: "Trace stack traces, isolate root causes, and suggest targeted fixes in real-time.",
        enabled: true,
    },
    {
        id: "architecture",
        icon: "🏗️",
        name: "Architecture",
        description: "Design scalable system architectures, evaluate trade-offs, and generate diagrams.",
        enabled: false,
    },
    {
        id: "ai-reasoning",
        icon: "🧠",
        name: "AI Reasoning",
        description: "Multi-step chain-of-thought reasoning for complex problem decomposition.",
        enabled: true,
    },
    {
        id: "code-review",
        icon: "🔍",
        name: "Code Review",
        description: "Analyze PRs for bugs, security issues, performance regressions, and style violations.",
        enabled: false,
    },
    {
        id: "performance",
        icon: "⚡",
        name: "Performance",
        description: "Profile bottlenecks, suggest optimizations, and benchmark before/after improvements.",
        enabled: true,
    },
];

// ─── Memory Entries ────────────────────────────────────────
export interface MemoryEntry {
    id: string;
    title: string;
    summary: string;
    timestamp: string;
    category: "code" | "design" | "resolved" | "debug" | "architecture";
    dotColor: string;
}

const CATEGORY_COLORS: Record<MemoryEntry["category"], string> = {
    code: "#00F3FF",
    design: "#A855F7",
    resolved: "#22C55E",
    debug: "#F59E0B",
    architecture: "#3B82F6",
};

export const MOCK_MEMORIES: MemoryEntry[] = [
    {
        id: "m1",
        title: "Debugged WebSocket reconnection",
        summary: "Fixed exponential backoff logic causing connection storms. Added jitter and max retry cap at 30s.",
        timestamp: "14:32",
        category: "debug",
        dotColor: CATEGORY_COLORS.debug,
    },
    {
        id: "m2",
        title: "Designed session persistence schema",
        summary: "Normalized user and session tables in Firestore. Added TTL indexes for auto-cleanup.",
        timestamp: "13:15",
        category: "design",
        dotColor: CATEGORY_COLORS.design,
    },
    {
        id: "m3",
        title: "Optimized audio pipeline latency",
        summary: "Reduced PCM encoding overhead from 12ms to 3ms by switching to Int16Array direct copy.",
        timestamp: "11:48",
        category: "code",
        dotColor: CATEGORY_COLORS.code,
    },
    {
        id: "m4",
        title: "Resolved CORS preflight failures",
        summary: "Gateway was missing Access-Control-Allow-Headers for custom auth tokens. Added to middleware.",
        timestamp: "10:22",
        category: "resolved",
        dotColor: CATEGORY_COLORS.resolved,
    },
    {
        id: "m5",
        title: "Architected multi-agent handover",
        summary: "Designed event-driven protocol for agent-to-agent task delegation using Redis pub/sub channels.",
        timestamp: "09:55",
        category: "architecture",
        dotColor: CATEGORY_COLORS.architecture,
    },
    {
        id: "m6",
        title: "Fixed emotion detection false positives",
        summary: "Tuned RMS spike threshold from 0.04 to 0.06 and extended quiet duration window to 2 seconds.",
        timestamp: "Yesterday",
        category: "debug",
        dotColor: CATEGORY_COLORS.debug,
    },
    {
        id: "m7",
        title: "Implemented vision frame compression",
        summary: "Added JPEG quality adaptive scaling based on bandwidth. Saves 40% data on slow connections.",
        timestamp: "Yesterday",
        category: "code",
        dotColor: CATEGORY_COLORS.code,
    },
    {
        id: "m8",
        title: "Refactored tool router dispatch",
        summary: "Moved from sequential tool execution to parallel Promise.allSettled with 5s timeout per tool.",
        timestamp: "2 days ago",
        category: "resolved",
        dotColor: CATEGORY_COLORS.resolved,
    },
];

// ─── Telemetry Snapshot ────────────────────────────────────
export interface TelemetrySnapshot {
    latencyMs: number;
    neuralEvents: number;
    emotionState: string;
    emotionIcon: string;
    sessionTokens: number;
    maxTokens: number;
}

export const MOCK_TELEMETRY: TelemetrySnapshot = {
    latencyMs: 42,
    neuralEvents: 1247,
    emotionState: "Focused",
    emotionIcon: "🎯",
    sessionTokens: 23891,
    maxTokens: 1000000,
};

// ─── Superpowers ───────────────────────────────────────────
export interface SuperpowerItem {
    id: string;
    name: string;
    icon: string;
    enabled: boolean;
}

export const MOCK_SUPERPOWERS: SuperpowerItem[] = [
    { id: "fullstack", name: "Full-Stack", icon: "🔧", enabled: true },
    { id: "cloud", name: "Cloud Architect", icon: "☁️", enabled: false },
    { id: "ml", name: "ML Engineer", icon: "🤖", enabled: true },
    { id: "devops", name: "DevOps", icon: "🚀", enabled: false },
    { id: "security", name: "Security", icon: "🛡️", enabled: false },
    { id: "mobile", name: "Mobile", icon: "📱", enabled: true },
];

// ─── Voice Tone & Experience Options ───────────────────────
export const VOICE_TONES = ["Calm", "Energetic", "Professional", "Playful"] as const;
export type VoiceToneOption = (typeof VOICE_TONES)[number];

export const EXPERIENCE_LEVELS = ["Junior", "Mid", "Senior", "Principal"] as const;
export type ExperienceLevelOption = (typeof EXPERIENCE_LEVELS)[number];

// ─── Accent Colors ─────────────────────────────────────────
export const ACCENT_COLOR_SWATCHES = [
    { id: "cyan", color: "#00F3FF", rgb: [0, 243, 255] as [number, number, number] },
    { id: "purple", color: "#A855F7", rgb: [168, 85, 247] as [number, number, number] },
    { id: "green", color: "#22C55E", rgb: [34, 197, 94] as [number, number, number] },
    { id: "amber", color: "#F59E0B", rgb: [245, 158, 11] as [number, number, number] },
    { id: "rose", color: "#F43F5E", rgb: [244, 63, 94] as [number, number, number] },
    { id: "blue", color: "#3B82F6", rgb: [59, 130, 246] as [number, number, number] },
] as const;
