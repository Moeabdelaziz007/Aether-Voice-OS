from pathlib import Path

from ast_extractor import PythonASTExtractor

extractor = PythonASTExtractor()
info = extractor.extract(Path("core/audio/capture.py"))

print(f"File: {info.file_path}")
print(f"Imports: {info.imports}")
print("\nClasses:")
for cls in info.classes:
    print(f"  - {cls.name} (line {cls.lineno})")
    print(f"    Docstring: {cls.docstring[:50] if cls.docstring else 'None'}...")
    print(f"    Methods: {[m.name for m in cls.methods]}")
