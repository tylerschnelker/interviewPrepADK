"""Shared data models for interview session state.

These dataclasses keep the planner and executor loosely coupled and readable.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InterviewQuestion:
    """Represents one generated question and its category."""

    category: str
    text: str


@dataclass
class AnswerFeedback:
    """Stores scoring and actionable notes for one answer."""

    relevance: int
    specificity: int
    star_format: int
    feedback: str


@dataclass
class QuestionAttempt:
    """Tracks a question, the user's answer, and evaluator output."""

    question: InterviewQuestion
    transcript: Optional[str] = None
    feedback: Optional[AnswerFeedback] = None
    model_answer: Optional[str] = None


@dataclass
class SessionState:
    """In-memory interview session state used by planner/executor."""

    resume_text: str
    job_description: str
    retrieved_context: List[str] = field(default_factory=list)
    questions: List[InterviewQuestion] = field(default_factory=list)
    attempts: List[QuestionAttempt] = field(default_factory=list)
    current_index: int = 0
    finished: bool = False
    readiness_summary: Optional[str] = None

    def current_attempt(self) -> Optional[QuestionAttempt]:
        """Returns the active question attempt, if available."""
        if 0 <= self.current_index < len(self.attempts):
            return self.attempts[self.current_index]
        return None

    def answer_stats(self) -> Dict[str, float]:
        """Computes aggregate score averages used in readiness output."""
        completed = [a.feedback for a in self.attempts if a.feedback]
        if not completed:
            return {"relevance": 0.0, "specificity": 0.0, "star_format": 0.0}
        count = float(len(completed))
        return {
            "relevance": sum(x.relevance for x in completed) / count,
            "specificity": sum(x.specificity for x in completed) / count,
            "star_format": sum(x.star_format for x in completed) / count,
        }
