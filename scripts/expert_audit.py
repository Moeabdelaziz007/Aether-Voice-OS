import os
import re
import sys

# --- Configuration ---
CORE_DOCS = ["README.md", "docs/ARCHITECTURE.md", "docs/index.md"]
FORBIDDEN_PATTERNS = [r".*\.log$", r"dump\.rdb$", r"agents/.*"]
DOCS_DIR = "docs"
BASE_DIR = os.getcwd()

def check_bilingual(file_path):
    """Basic check for Arabic characters in a file."""
    if not os.path.exists(file_path):
        return False, "File missing"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Basic Arabic Unicode range
        arabic_chars = re.findall(r'[\u0600-\u06FF]', content)
        if len(arabic_chars) > 50: # Arbitrary threshold for "meaningful" content
            return True, f"Bilingual check passed ({len(arabic_chars)} Arabic chars)"
        return False, f"Insufficient Arabic content ({len(arabic_chars)} chars)"

def check_broken_links(file_path):
    """Check for broken relative markdown links."""
    if not os.path.exists(file_path):
        return []
    
    broken = []
    file_dir = os.path.dirname(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find markdown links: [text](path)
        links = re.findall(r'\[.*?\]\((?!http)(.*?)\)', content)
        
        for link in links:
            # Handle anchor links
            clean_link = link.split('#')[0]
            if not clean_link:
                continue
            
            # Resolve relative path
            target_path = os.path.normpath(os.path.join(file_dir, clean_link))
            if not os.path.exists(target_path):
                broken.append(f"Broken: [{link}] -> {target_path}")
                
    return broken

def check_forbidden_files():
    """Check for forbidden files or patterns."""
    found = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Exclude common dirs
        path_parts = root.split(os.sep)
        if any(d in path_parts for d in [".git", "node_modules", ".venv", ".cargo_home", "target", "vendor", "__pycache__", "archive", ".idx", ".qoder"]):
            continue
            
        for name in files + dirs:
            rel_path = os.path.relpath(os.path.join(root, name), BASE_DIR)
            for pattern in FORBIDDEN_PATTERNS:
                if re.match(pattern, rel_path):
                    found.append(rel_path)
    return found

def main():
    print("🌠 Running Expert Repository Audit...")
    errors = []
    warnings = []

    # 1. Bilingual Audit
    print("\n--- 🧬 Bilingual Consistency ---")
    for doc in CORE_DOCS:
        status, msg = check_bilingual(doc)
        if status:
            print(f"✅ {doc}: {msg}")
        else:
            warnings.append(f"{doc}: {msg}")
            print(f"⚠️ {doc}: {msg}")

    # 2. Markdown Link Audit
    print("\n--- 🔗 Markdown Link Integrity ---")
    all_md = []
    for root, _, files in os.walk(BASE_DIR):
        path_parts = root.split(os.sep)
        if any(d in path_parts for d in [".git", "node_modules", ".venv", ".cargo_home", "target", "vendor", "__pycache__", "archive", ".idx", ".qoder"]):
            continue
        for f in files:
            if f.endswith(".md"):
                all_md.append(os.path.join(root, f))
    
    for md_file in all_md:
        rel_md = os.path.relpath(md_file, BASE_DIR)
        broken = check_broken_links(md_file)
        if broken:
            print(f"❌ {rel_md}: {len(broken)} broken links found")
            for b in broken:
                errors.append(f"{rel_md}: {b}")
                print(f"   - {b}")
        else:
            print(f"✅ {rel_md}: Links OK")

    # 3. Forbidden Artifact Audit
    print("\n--- 🧹 Repository Cleanliness ---")
    forbidden = check_forbidden_files()
    if forbidden:
        print(f"❌ Forbidden artifacts detected: {len(forbidden)}")
        for f in forbidden:
            errors.append(f"Forbidden file: {f}")
            print(f"   - {f}")
    else:
        print("✅ No forbidden artifacts found")

    # Final Report
    print("\n--- 📊 Audit Summary ---")
    if errors:
        print(f"❌ FAILED: {len(errors)} errors found.")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    elif warnings:
        print(f"⚠️ PASSED WITH WARNINGS: {len(warnings)} issues.")
        sys.exit(0)
    else:
        print("💎 PERFECT REPOSITORY STATUS: Level Expert attained.")
        sys.exit(0)

if __name__ == "__main__":
    main()
