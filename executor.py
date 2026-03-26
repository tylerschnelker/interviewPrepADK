"""Executor for planner-selected actions.

It invokes registered tools, updates state, and returns user-facing text.
"""

from typing import Optional

import tools  # noqa: F401  # Import registers tools.
from adk_runtime import get_tool
from config import settings
from models import QuestionAttempt, SessionState
from rag import LocalRetriever, load_context_chunks
from voice.listener import WhisperListener


class InterviewExecutor:
    """Runs actions chosen by InterviewPlanner."""

    def __init__(self) -> None:
        context_chunks = load_context_chunks(settings.context_dir)
        self.retriever = LocalRetriever(context_chunks)
        self.listener = WhisperListener()

    def execute(
        self,
        state: SessionState,
        action: str,
        user_command: Optional[str],
    ) -> str:
        """Executes one action and returns response text."""
        if action == "generate_questions":
            query = f"{state.resume_text}\n\n{state.job_description}"
            retrieved = [text for text, _score in self.retriever.retrieve(query, top_k=4)]
            state.retrieved_context = retrieved
            tool = get_tool("generate_questions")
            state.questions = tool(state.resume_text, state.job_description, retrieved)
            state.attempts = [QuestionAttempt(question=q) for q in state.questions]
            first = state.attempts[0].question
            return (
                f"Generated {len(state.questions)} questions.\n\n"
                f"Question 1 [{first.category}]: {first.text}\n"
                "Reply with `/record` for voice answer, type your answer directly, "
                "or use `/model` for a model response."
            )

        if action == "capture_answer":
            attempt = state.current_attempt()
            if not attempt:
                return "No active question."
            transcript = self.listener.record_and_transcribe()
            attempt.transcript = transcript
            return f"Transcript captured:\n{transcript}\n\nNow evaluating..."

        if action == "evaluate_answer":
            attempt = state.current_attempt()
            if not attempt:
                return "No active question."
            text_input = (user_command or "").strip()
            if text_input and not text_input.startswith("/"):
                attempt.transcript = text_input
            if not attempt.transcript:
                return "No answer available yet. Use `/record` or type your answer."
            tool = get_tool("evaluate_answer")
            attempt.feedback = tool(attempt.question.text, attempt.transcript)
            f = attempt.feedback
            return (
                "Answer feedback:\n"
                f"- Relevance: {f.relevance}/10\n"
                f"- Specificity: {f.specificity}/10\n"
                f"- STAR format: {f.star_format}/10\n"
                f"- Notes: {f.feedback}\n\n"
                "Use `/next` to continue or `/model` to compare with a model answer."
            )

        if action == "provide_model_answer":
            attempt = state.current_attempt()
            if not attempt:
                return "No active question."
            tool = get_tool("provide_model_answer")
            attempt.model_answer = tool(
                attempt.question.text,
                state.resume_text,
                state.job_description,
            )
            return f"Model answer:\n{attempt.model_answer}"

        if action == "next_question":
            if state.current_index >= len(state.attempts) - 1:
                return "You are on the final question. Use `/end` for readiness scoring."
            state.current_index += 1
            q = state.attempts[state.current_index].question
            return f"Question {state.current_index + 1} [{q.category}]: {q.text}"

        if action == "score_readiness":
            tool = get_tool("score_readiness")
            state.readiness_summary = tool(state.attempts)
            state.finished = True
            return state.readiness_summary

        state.finished = True
        return "Session ended."
