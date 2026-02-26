"""
Script to index the AetherOS codebase visually and semantically into a local Vector DB.
It uses LocalVectorStore to generate embeddings and saves them to '.aether_index.pkl'.
"""

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from core.tools.vector_store import LocalVectorStore

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Settings
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_FILE = ROOT_DIR / ".aether_index.pkl"
EXTENSIONS = {".py", ".ts", ".tsx", ".md", ".json"}
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


async def index_codebase() -> None:
    logger.info("Initializing Codebase Indexer...")
    load_dotenv(ROOT_DIR / ".env")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("AETHER_AI_API_KEY")

    if not api_key:
        logger.error("No Google API Key found. Ensure .env is set.")
        return

    vector_store = LocalVectorStore(api_key=api_key)
    # Attempt to load existing to append/update, but typically we want to overwrite entirely
    # For this script, we'll start fresh to guarantee no stale vectors.

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

    for idx, filepath in enumerate(files_to_index, 1):
        try:
            rel_path = filepath.relative_to(ROOT_DIR)
            content = filepath.read_text(encoding="utf-8")

            # Simple chunking
            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                key = f"{rel_path}:{i}"
                chunk_header = f"File: {rel_path}\nChunk: {i+1}/{len(chunks)}\n---\n"
                full_text = chunk_header + chunk

                # We batch await for simplicity, but a Semaphore would be safer for rate limits
                await vector_store.add_text(
                    key=key,
                    text=full_text,
                    metadata={"file": str(rel_path), "chunk": i},
                )
                total_chunks += 1

            logger.info(
                "[%d/%d] Processed: %s (Chunks: %d)",
                idx,
                total_files,
                rel_path,
                len(chunks),
            )

            # Save incrementally every 50 files
            if idx % 50 == 0:
                vector_store.save(INDEX_FILE)
                logger.info("Checkpoint saved.")
        except Exception as e:
            logger.error("Could not process %s: %s", filepath, e)

    # Final save
    vector_store.save(INDEX_FILE)
    logger.info("Indexing complete! Total chunks embedded: %d", total_chunks)


if __name__ == "__main__":
    asyncio.run(index_codebase())
