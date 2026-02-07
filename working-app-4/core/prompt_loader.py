from pathlib import Path

def load_prompt(path: str, variables: dict) -> str:
    template = Path(path).read_text()

    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))

    return template
