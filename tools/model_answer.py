"""Model-answer generation tool.

This gives users a benchmark answer whenever they request one.
"""

from pathlib import Path

from adk_runtime import adk_tool
from llm_client import chat


def _read_prompt() -> str:
    return Path("prompts/model_answer.txt").read_text(encoding="utf-8")


@adk_tool("provide_model_answer")
def provide_model_answer(question_text: str, resume_text: str, job_description: str) -> str:
    """Generates a polished example answer."""
    prompt = _read_prompt()
    return chat(
        f"{prompt}\n\nQuestion:\n{question_text}\n\nResume:\n{resume_text}\n\n"
        f"Job description:\n{job_description}\n"
    )
