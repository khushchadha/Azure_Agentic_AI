import os

from utils.paths import PROMPTS_DIR


def load_prompt(prompt_name: str) -> str:
    """Read and return text content from a .md prompt file in backend/prompts/.

    Accepts either a bare file name ("cook.md") or the legacy
    "prompts/cook.md" form.
    """
    prompt_name = prompt_name.replace("\\", "/").split("prompts/")[-1]
    prompt_path = os.path.join(PROMPTS_DIR, prompt_name)

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()
