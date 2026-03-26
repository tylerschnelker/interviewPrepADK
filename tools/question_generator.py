"""Question generation tool.

Why a tool:
- Keeps prompt logic separate from orchestration.
- Lets the planner call generation only when needed.
"""

from pathlib import Path
from typing import List

from adk_runtime import adk_tool
from llm_client import chat
from models import InterviewQuestion


def _read_prompt() -> str:
    return Path("prompts/question_generation.txt").read_text(encoding="utf-8")


@adk_tool("generate_questions")
def generate_questions(
    resume_text: str,
    job_description: str,
    retrieved_context: List[str],
) -> List[InterviewQuestion]:
    """Generates 9 tailored questions across required categories."""
    prompt = _read_prompt()
    context_blob = "\n\n".join(retrieved_context) if retrieved_context else "None"
    user_block = (
        f"{prompt}\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Retrieved context:\n{context_blob}\n"
    )
    raw = chat(user_block)
    questions: List[InterviewQuestion] = []
    for line in raw.splitlines():
        if "::" not in line:
            continue
        category, text = line.split("::", 1)
        category = category.strip().lower()
        text = text.strip()
        if category in {"technical", "behavioral", "role-specific"} and text:
            questions.append(InterviewQuestion(category=category, text=text))

    # Fallback to deterministic starter questions if parsing fails.
    if len(questions) < 9:
        fallback = [
            ("technical", "Walk me through a complex system you built end-to-end."),
            ("technical", "How do you debug a production incident under time pressure?"),
            ("technical", "Describe a trade-off you made between performance and maintainability."),
            ("behavioral", "Tell me about a time you handled conflicting priorities."),
            ("behavioral", "Describe a disagreement with a teammate and how you resolved it."),
            ("behavioral", "Share an example of receiving tough feedback and applying it."),
            ("role-specific", "Why does this role align with your recent experience?"),
            ("role-specific", "How would your first 90 days in this role look?"),
            ("role-specific", "What domain risk in this job would you tackle first and why?"),
        ]
        questions = [InterviewQuestion(category=c, text=t) for c, t in fallback]

    return questions[:9]
