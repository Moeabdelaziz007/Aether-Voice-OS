import os
import tempfile
from scripts.auto_improve import analyze_file, MAX_COMPLEXITY, MAX_FUNCTION_LENGTH

def test_analyze_file_no_issues():
    content = """
def say_hello():
    pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        temp_name = f.name

    issues = analyze_file(temp_name)
    os.remove(temp_name)
    assert len(issues) == 0

def test_analyze_file_with_print():
    content = """
def debug_stuff():
    print("This is a debug message")
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        temp_name = f.name

    issues = analyze_file(temp_name)
    os.remove(temp_name)
    assert any("print()" in issue['message'] for issue in issues)

def test_analyze_file_high_complexity():
    content = f"""
def complex_function():
"""
    for i in range(MAX_COMPLEXITY + 2):
        content += f"    if {i} == {i}:\n        pass\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        temp_name = f.name

    issues = analyze_file(temp_name)
    os.remove(temp_name)
    assert any("high complexity" in issue['message'] for issue in issues)

def test_analyze_file_broad_except():
    content = """
def risky_function():
    try:
        pass
    except Exception:
        pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        temp_name = f.name

    issues = analyze_file(temp_name)
    os.remove(temp_name)
    # broad except triggers 2 rules: empty except and broad except
    assert any("Broad except" in issue['message'] for issue in issues)
