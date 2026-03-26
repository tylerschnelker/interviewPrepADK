"""Local Ollama client wrapper.

This wrapper keeps model invocation logic in one place and guarantees all
generation stays local to the machine.
"""

from typing import Optional

import ollama

from config import settings


def chat(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Runs a local Ollama chat completion and returns text content."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = ollama.chat(model=settings.ollama_model, messages=messages)
    return response["message"]["content"].strip()
