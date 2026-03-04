import argparse
import os
import subprocess
from collections import Counter
from datetime import datetime


def get_tree(path, depth=2, current_depth=0):
    if current_depth > depth:
        return ""

    output = ""
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return output

    for i, item in enumerate(items):
        if item in {".git", "node_modules", "__pycache__", "dist", "build"}:
            continue

        full_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        prefix = "└── " if is_last else "├── "
        output += "  " * current_depth + prefix + item + "\n"

        if os.path.isdir(full_path):
            output += get_tree(full_path, depth, current_depth + 1)

    return output


def analyze_languages(path):
    ext_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript (React)",
        ".jsx": "JavaScript (React)",
        ".css": "CSS",
        ".scss": "SCSS",
        ".html": "HTML",
        ".go": "Go",
        ".rs": "Rust",
        ".cpp": "C++",
        ".h": "C/C++",
        ".c": "C",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
    }
    languages = Counter()

    for root, dirs, files in os.walk(path):
        if any(d in root for d in {".git", "node_modules", "__pycache__"}):
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ext_map:
                languages[ext_map[ext]] += 1

    total = sum(languages.values())
    if total == 0:
        return "No detectable languages."

    stats = []
    for lang, count in languages.most_common(5):
        percentage = (count / total) * 100
        stats.append(f"- {lang}: {percentage:.1f}%")
    return "\n".join(stats)


def generate_mermaid(path):
    # Simple heuristic for architecture: Top level directories
    dirs = [
        d
        for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d)) and d not in {".git", "node_modules"}
    ]
    if not dirs:
        return "graph TD\n  Root --> Files"

    lines = ["graph TD", f"  Root[{os.path.basename(path)}]"]
    for d in dirs[:10]:  # Limit to 10 nodes for clarity
        lines.append(f"  Root --> {d}")
    return "\n".join(lines)


def analyze_repo(url, depth=2):
    repo_name = url.rstrip("/").split("/")[-1]
    temp_dir = f"/tmp/aether_analyze_{repo_name}_{datetime.now().strftime('%H%M%S')}"

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, temp_dir],
            check=True,
            capture_output=True,
        )
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"# Repository Analysis: {repo_name}")
    print(f"URL: {url}\n")

    print("## Structure")
    print("```")
    print(get_tree(temp_dir, depth))
    print("```\n")

    print("## Language Breakdown")
    print(analyze_languages(temp_dir))
    print("\n")

    print("## Architecture (Mermaid)")
    print("```mermaid")
    print(generate_mermaid(temp_dir))
    print("```\n")

    # Commit Activity (simplification)
    print("## Recent Activity")
    try:
        git_log = subprocess.check_output(
            ["git", "-C", temp_dir, "log", "-n", "5", "--pretty=format:- %ar: %s"],
            text=True,
        )
        print(git_log)
    except:
        print("Failed to fetch log.")

    subprocess.run(["rm", "-rf", temp_dir])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Repo structure and patterns"
    )
    parser.add_argument("url", help="GitHub Repository URL")
    parser.add_argument(
        "--depth", type=int, default=2, help="Directory traversal depth"
    )
    args = parser.parse_args()

    analyze_repo(args.url, args.depth)
