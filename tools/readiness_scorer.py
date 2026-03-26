"""Session readiness scoring tool.

This tool compiles the full interview run into final readiness guidance.
"""

from pathlib import Path
from typing import List

from adk_runtime import adk_tool
from llm_client import chat
from models import QuestionAttempt


def _read_prompt() -> str:
    return Path("prompts/readiness_scorer.txt").read_text(encoding="utf-8")


@adk_tool("score_readiness")
def score_readiness(attempts: List[QuestionAttempt]) -> str:
    """Produces final readiness score and top improvement areas."""
    prompt = _read_prompt()
    transcript_blob = []
    for idx, attempt in enumerate(attempts, start=1):
        transcript_blob.append(
            f"Q{idx} [{attempt.question.category}] {attempt.question.text}\n"
            f"Answer: {attempt.transcript or 'N/A'}\n"
            f"Feedback: {attempt.feedback.feedback if attempt.feedback else 'N/A'}\n"
        )
    return chat(f"{prompt}\n\nSession data:\n" + "\n".join(transcript_blob))
