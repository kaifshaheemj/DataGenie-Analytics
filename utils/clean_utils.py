import re
import json

def clean_json(text: str) -> str:
    if not text:
        return "{}"

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"```[a-zA-Z]*", "", text)
        text = text.replace("```", "").strip()

    return text

