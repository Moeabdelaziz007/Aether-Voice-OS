# 🛠️ Aether Architect Tools & Skills (ArchitectExpert)

The Aether Architectural Core relies on high-level tools for vision, research, planning, and task delegation.
These tools are defined dynamically in Python, but their usage rules are defined here.

## 1. Vision Tool (`vision_tool`)
**Skill Name:** Visual Context Pulse
- **Usage:** When you are asked "What is this error?" or "Why does this UI look wrong?", immediately use this tool to request the latest screen frame from the user's desktop.
- **Rule:** Do not guess visual output.

## 2. Search Tool (`search_tool`)
**Skill Name:** Web Grounding
- **Usage:** When asked about external APIs, current documentation (e.g., Next.js 15, Rust PyO3), use Google Search.
- **Rule:** Aether is an offline-capable system. Default to local knowledge first. Use web search only for external, up-to-date documentation.

## 3. RAG Tool (`rag_tool`)
**Skill Name:** Codebase Semantic Search
- **Usage:** To locate logic across the `core/`, `cortex/`, and `apps/` directories.
- **Rule:** If the user asks where a feature is implemented, use this tool to query the `LocalVectorStore`.

## 4. Deep Handover Tool (`delegate_to_agent`)
**Skill Name:** Task Delegation (Hive A2A)
- **Usage:** This is your most powerful tool. When you determine the user's request involves heavy coding, debugging, or running terminal commands (e.g., fixing a failing test, implementing a feature), you **must** hand off the task to `CodingExpert`.
- **Rule:** Provide the `CodingExpert` with exact file paths, desired logic, and the context you already gathered. Do not attempt to code the solution yourself.

## 5. Memory Tool (`memory_tool`)
**Skill Name:** Firestore L2 Synapse
- **Usage:** To read or write architectural decisions (ADRs) or session insights to long-term memory.