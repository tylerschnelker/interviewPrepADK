"""Tool package initialization.

Importing these modules registers all tools with the ADK-style registry.
"""

# Import side-effects are intentional: they register tool functions.
from tools import answer_evaluator, model_answer, question_generator, readiness_scorer  # noqa: F401
