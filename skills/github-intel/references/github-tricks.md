# 💡 GitHub URL Hacks & API Shortcuts

Advanced operators and browser-less tricks for rapid intelligence gathering.

## 1. Quick File View

- Append `?raw=true` to any file URL to get the plain text.
- Use `github.com/owner/repo/raw/branch/path/to/file` for direct downloads.

## 2. API Shortcuts (No Auth Needed for Public)

- **Repo Info**: `https://api.github.com/repos/{owner}/{repo}`
- **List Files**: `https://api.github.com/repos/{owner}/{repo}/contents/{path}`
- **Recent Commits**: `https://api.github.com/repos/{owner}/{repo}/commits`

## 3. Search Operators

- `extension:py`: Files with .py extension
- `path:src/`: Files inside the src directory
- `filename:Dockerfile`: Search specifically for Dockerfiles
- `size:>1000`: Files larger than 1000 bytes

## 4. Comparisons

- `https://github.com/owner/repo/compare/main...develop`: See diff between branches.
- `https://github.com/owner/repo/compare/v1.0...v2.0`: See changes between tags.

## 5. User Intel

- `https://api.github.com/users/{username}/repos`: List all public repos of a user.
- `https://api.github.com/users/{username}/events/public`: Recent public activity of a user.
