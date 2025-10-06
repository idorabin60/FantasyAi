# translate_players.py
# pip install openai python-dotenv

from __future__ import annotations
from typing import List
import json
import os
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

__all__ = ["translate_players"]  # this is the only public export

SYSTEM_PROMPT = (
    "You are a bilingual sports translator. "
    "Translate Hebrew football player names to their standard English full names "
    "as commonly written by international football media (e.g., 'מסי' -> 'Lionel Messi', "
    "'אליסון' -> 'Alisson Becker'). Keep the original order. "
    "Return ONLY a JSON array of strings, no extra text."
)


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    """Create (and cache) an OpenAI client using OPENAI_API_KEY from env/.env."""
    load_dotenv()  # safe to call multiple times; no-op after first
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Set it in your environment or .env file.")
    return OpenAI(api_key=api_key)


def translate_players(hebrew_players: List[str], model: str = "gpt-4.1-mini") -> List[str]:
    """
    Translate a list of Hebrew footballer names to standard English full names.

    :param hebrew_players: list of Hebrew names (e.g., ["מסי", "אליסון"])
    :param model: OpenAI model id (default: gpt-4.1-mini)
    :return: list of English names in the same order
    """
    if not hebrew_players:
        return []

    user_prompt = (
        "Hebrew names:\n"
        + json.dumps(hebrew_players, ensure_ascii=False)
        + "\nReturn only a JSON array of strings."
    )

    client = _get_client()
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = (resp.choices[0].message.content or "").strip()

    # Parse the JSON array; if the model added any stray text, try to salvage.
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1 and end > start:
            return json.loads(content[start: end + 1])
        raise ValueError(f"Model did not return valid JSON:\n{content}")
