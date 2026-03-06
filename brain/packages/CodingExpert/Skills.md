# 🛠️ Aether Engineer Tools & Skills (CodingExpert)

The Aether Engineering Core relies on low-level, tactical tools for code execution, system navigation, and debugging.
These tools are defined dynamically in Python, but their usage rules are defined here.

## 1. System Tool (`system_tool`)
**Skill Name:** Terminal Execution (Bash)
- **Usage:** This is your primary weapon. Use it to run `pytest`, `cargo build`, `npm run dev`, `ls`, `cat`, `grep`, or write files directly via `echo` or `sed`.
- **Rule:** If a tool call fails (e.g., `ModuleNotFoundError`), you must autonomously attempt to fix it (e.g., `pip install`) and run the tool again before giving up.
- **Rule:** When modifying code, use `sed` or Python scripts to apply diffs accurately. Always verify the change with `cat`.

## 2. Tasks Tool (`tasks_tool`)
**Skill Name:** Jira/Task Management
- **Usage:** If the Architect hands off a list of tasks, use this to mark them as `IN_PROGRESS` or `DONE`.
- **Rule:** Never mark a task as DONE unless you have successfully run the related tests.

## 3. RAG Tool (`rag_tool`)
**Skill Name:** Codebase Context
- **Usage:** When you are assigned a task but don't know the full architecture, use semantic search to locate `core/` and `cortex/` files.
- **Rule:** If the task requires deep architectural changes (e.g., rewriting the Deep Handover Protocol), immediately tell the user to request the Architect instead.

## 4. Memory Tool (`memory_tool`)
**Skill Name:** Firestore Debug Logs
- **Usage:** Write critical bug fixes or learned solutions (e.g., "ALSA driver issues on Pi 4 require PyAudio mock in tests") to long-term memory.
- **Rule:** Always tag memory with `debugging` and `codebase`.