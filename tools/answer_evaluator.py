"""Answer evaluator tool.

This tool scores a transcript on relevance, specificity, and STAR structure.
"""

import json
from pathlib import Path

from adk_runtime import adk_tool
from llm_client import chat
from models import AnswerFeedback


def _read_prompt() -> str:
    return Path("prompts/answer_evaluation.txt").read_text(encoding="utf-8")


@adk_tool("evaluate_answer")
def evaluate_answer(question_text: str, transcript: str) -> AnswerFeedback:
    """Returns structured scoring and coaching feedback."""
    prompt = _read_prompt().format(question=question_text, answer=transcript)
    raw = chat(prompt, format_json=True)
    try:
        parsed = json.loads(raw)
        return AnswerFeedback(
            relevance=int(parsed.get("relevance", 0)),
            specificity=int(parsed.get("specificity", 0)),
            star_format=int(parsed.get("star_format", 0)),
            feedback=str(parsed.get("feedback", "No feedback returned.")),
        )
    except json.JSONDecodeError:
        # Fallback protects CLI flow if model returns non-JSON text.
        return AnswerFeedback(
            relevance=6,
            specificity=6,
            star_format=6,
            feedback=(
                "Could not parse evaluator JSON. Re-answer with a clearer STAR format, "
                "include role-relevant details, and add measurable outcomes."
            ),
        )
