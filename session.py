"""High-level interview session orchestrator.

This class links planner and executor and exposes a small step() API.
"""

from typing import Optional

from executor import InterviewExecutor
from models import SessionState
from planner import InterviewPlanner


class InterviewSession:
    """Planner-executor runtime for one interview session."""

    def __init__(self, resume_text: str, job_description: str) -> None:
        self.state = SessionState(resume_text=resume_text, job_description=job_description)
        self.planner = InterviewPlanner()
        self.executor = InterviewExecutor()

    def step(self, user_command: Optional[str] = None) -> str:
        """Runs one planner decision and corresponding execution."""
        plan = self.planner.decide(self.state, user_command)
        return self.executor.execute(self.state, plan.action, user_command)
