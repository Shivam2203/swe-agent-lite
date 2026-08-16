import os
import ast

def read_file(file_path: str) -> str:
    """Read the content of a file from the dummy repository."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: File {file_path} not found."
    except Exception as e:
        return f"ERROR: Could not read file: {e}"

def write_file(file_path: str, content: str) -> str:
    """Write the patched code back to the file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"SUCCESS: Written to {file_path}"
    except Exception as e:
        return f"ERROR: Could not write file: {e}"

def get_file_path(filename: str) -> str:
    """Construct the full path to a file in the dummy repo."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "dummy_repo", filename)

def validate_python_syntax(code: str) -> tuple[bool, str]:
    """Check if the generated code is valid Python."""
    try:
        ast.parse(code)
        return True, "Valid Python syntax"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"