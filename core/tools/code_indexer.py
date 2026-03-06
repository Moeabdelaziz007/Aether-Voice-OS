"""
Script to index the AetherOS codebase visually and semantically into a local Vector DB.
It uses LocalVectorStore to generate embeddings and saves them to '.aether_index.json'.
"""

import asyncio
import json
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from core.tools.firestore_vector_store import FirestoreVectorStore
from tools.ast_extractor import PythonASTExtractor

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Settings
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKUP_FILE = ROOT_DIR / ".aether_index_backup.json"
EXTENSIONS = {".py", ".rs", ".ts", ".tsx", ".md", ".json"}
IGNORE_DIRS = {
    ".git",
    ".idx",
    "node_modules",
    ".next",
    "out",
    "venv",
    "__pycache__",
    "target",
    "assets",
}


def extract_rust_metadata(content: str) -> dict:
    """Extract pub functions, structs, and doc comments from a Rust file."""
    # Extract pub functions
    pub_fns = re.findall(r"pub\s+(?:async\s+)?fn\s+(\w+)\s*\(", content)

    # Extract doc comments (///)
    doc_comments = re.findall(r"///\s*(.+?)(?=\n(?://)|$)", content, re.DOTALL)

    # Extract struct definitions
    structs = re.findall(r"pub\s+struct\s+(\w+)", content)

    return {
        "functions": pub_fns,
        "doc_comments": doc_comments,
        "structs": structs,
    }


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def format_classes(classes: list) -> str:
    """Format extracted classes for text embedding."""
    result = []
    for cls in classes:
        methods = [m.name for m in cls.methods]
        result.append(f"- {cls.name} (Methods: {', '.join(methods)})")
    return "\n".join(result)


def format_functions(functions: list) -> str:
    """Format extracted functions for text embedding."""
    return "\n".join([f"- {f.name}" for f in functions])


async def index_codebase() -> None:
    logger.info("Initializing Codebase Indexer...")
    load_dotenv(ROOT_DIR / ".env")
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        logger.error("No Google API Key found. Ensure .env is set.")
        return

    vector_store = FirestoreVectorStore(api_key=api_key)
    await vector_store.initialize()

    files_to_index = []
    for current_dir, dirs, files in os.walk(ROOT_DIR):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            path = Path(current_dir) / file
            if path.suffix in EXTENSIONS:
                files_to_index.append(path)

    total_chunks = 0
    total_files = len(files_to_index)
    logger.info(
        "Found %d files to index. Beginning chunking and embedding...", total_files
    )

    extractor = PythonASTExtractor()
    semaphore = asyncio.Semaphore(10)
    backup_data = {}

    async def process_file(filepath: Path, idx: int):
        nonlocal total_chunks
        async with semaphore:
            try:
                rel_path = filepath.relative_to(ROOT_DIR)
                content = filepath.read_text(encoding="utf-8")

                metadata = {"file": str(rel_path)}
                text_content = content

                if filepath.suffix == ".py":
                    ast_info = extractor.extract(filepath)
                    text_content = f"""
File: {rel_path}
Module Docstring: {ast_info.docstring or ""}

Classes:
{format_classes(ast_info.classes)}

Functions:
{format_functions(ast_info.functions)}

Imports:
{", ".join(ast_info.imports)}

Source:
{content}
"""
                    metadata.update(
                        {
                            "language": "python",
                            "classes": [c.name for c in ast_info.classes],
                            "functions": [f.name for f in ast_info.functions],
                            "imports": ast_info.imports,
                        }
                    )
                elif filepath.suffix == ".rs":
                    rust_meta = extract_rust_metadata(content)
                    metadata.update(
                        {
                            "language": "rust",
                            "classes": rust_meta["structs"],
                            "functions": rust_meta["functions"],
                        }
                    )

                chunks = chunk_text(text_content)
                file_backup = []

                for i, chunk in enumerate(chunks):
                    key = f"{rel_path}:{i}"
                    chunk_header = (
                        f"File: {rel_path}\nChunk: {i + 1}/{len(chunks)}\n---\n"
                    )
                    full_text = chunk_header + chunk

                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk"] = i

                    await vector_store.add_text(
                        key=key,
                        text=full_text,
                        metadata=chunk_metadata,
                    )

                    file_backup.append(
                        {"key": key, "text": full_text, "metadata": chunk_metadata}
                    )
                    total_chunks += 1

                backup_data[str(rel_path)] = file_backup
                logger.info(
                    "[%d/%d] Processed: %s (Chunks: %d)",
                    idx,
                    total_files,
                    rel_path,
                    len(chunks),
                )

            except Exception as e:
                logger.error("Could not process %s: %s", filepath, e)

    tasks = [process_file(fp, i) for i, fp in enumerate(files_to_index, 1)]
    await asyncio.gather(*tasks)

    # Save local backup
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        logger.info("Local backup saved to %s", BACKUP_FILE)
    except Exception as e:
        logger.error("Could not save backup: %s", e)

    logger.info("Indexing complete! Total chunks embedded: %d", total_chunks)


if __name__ == "__main__":
    asyncio.run(index_codebase())
