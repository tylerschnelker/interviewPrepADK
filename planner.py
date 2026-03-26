"""Planner for deciding next action from session + user command.

This is intentionally explicit and deterministic so behavior is predictable
while still fitting a planner-executor architecture.
"""

from dataclasses import dataclass
from typing import Optional

from models import SessionState


@dataclass
class PlanStep:
    """A single planner output that tells executor what to do."""

    action: str
    reason: str


class InterviewPlanner:
    """Chooses the next tool/action based on conversation state."""

    def decide(self, state: SessionState, user_command: Optional[str]) -> PlanStep:
        command = (user_command or "").strip().lower()

        if not state.questions:
            return PlanStep("generate_questions", "Session has no questions yet.")

        if command == "/model":
            return PlanStep(
                "provide_model_answer",
                "User explicitly requested a model answer.",
            )
        if command == "/end":
            return PlanStep("score_readiness", "User requested final scoring.")
        if command == "/next":
            return PlanStep("next_question", "User requested next question.")
        if command == "/record":
            return PlanStep("capture_answer", "User wants to answer by voice.")
        if command and command not in {"/record", "/model", "/next", "/end"}:
            return PlanStep("evaluate_answer", "Treat raw text as answer transcript.")

        current = state.current_attempt()
        if current and not current.transcript:
            return PlanStep("capture_answer", "Need answer for current question.")
        if current and current.transcript and not current.feedback:
            return PlanStep("evaluate_answer", "Need evaluator feedback.")

        if state.current_index < len(state.attempts) - 1:
            return PlanStep("next_question", "Move to the next queued question.")

        # If all attempts have feedback, end the session automatically.
        if all(a.feedback for a in state.attempts):
            return PlanStep("score_readiness", "All questions completed.")

        return PlanStep("end_session", "No additional action determined.")
