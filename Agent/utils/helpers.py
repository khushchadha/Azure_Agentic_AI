import os

def load_prompt(prompt_path: str) -> str:
    """Read and return text content from a .md prompt file."""
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()