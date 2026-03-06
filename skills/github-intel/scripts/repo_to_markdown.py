import argparse
import os
import subprocess
from datetime import datetime


def is_text_file(file_path):
    """Check if a file is text-based based on common extensions."""
    text_extensions = {
        ".txt",
        ".md",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".css",
        ".scss",
        ".html",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml",
        ".go",
        ".rs",
        ".cpp",
        ".h",
        ".c",
        ".sh",
        ".bash",
        ".sql",
        ".dockerfile",
        ".env",
        ".gitignore",
        ".cfg",
        ".ini",
    }
    return os.path.splitext(file_path)[1].lower() in text_extensions


def get_repo_files(repo_path, max_files=100):
    files_to_process = []
    count = 0

    for root, dirs, files in os.walk(repo_path):
        # Skip git artifacts and common build artifacts
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {
                ".git",
                "node_modules",
                "__pycache__",
                "dist",
                "build",
                "venv",
                ".venv",
            }
        ]

        for file in files:
            file_path = os.path.join(root, file)
            if is_text_file(file_path):
                files_to_process.append(file_path)
                count += 1
                if count >= max_files:
                    return files_to_process, True
    return files_to_process, False


def repo_to_markdown(repo_url, max_files=50):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    temp_dir = f"/tmp/aether_git_{repo_name}_{datetime.now().strftime('%H%M%S')}"

    print(f"Cloning {repo_url} into {temp_dir}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            check=True,
            capture_output=True,
        )
    except Exception as e:
        print(f"Error cloning repo: {e}")
        return

    files, truncated = get_repo_files(temp_dir, max_files)

    print(f"# Repository: {repo_name}")
    print(f"Source: {repo_url}\n")
    print(
        f"## Metadata\n- Generated at: {datetime.now().isoformat()}\n"
        f"- File Count Limit: {max_files}\n"
    )

    for file_path in files:
        rel_path = os.path.relpath(file_path, temp_dir)
        print(f"### File: {rel_path}")
        print("```" + (os.path.splitext(rel_path)[1][1:] or "text"))
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading file: {e}")
        print("```\n")

    if truncated:
        print(f"\n> [!WARNING]\n> Analysis truncated at {max_files} files.")

    # Cleanup
    subprocess.run(["rm", "-rf", temp_dir])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert GitHub Repo to AI-friendly Markdown"
    )
    parser.add_argument("url", help="GitHub Repository URL")
    parser.add_argument(
        "--max-files", type=int, default=50, help="Max files to process"
    )
    args = parser.parse_args()

    repo_to_markdown(args.url, args.max_files)
