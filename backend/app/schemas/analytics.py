from typing import Dict, List, Any, Optional
import uuid
from pydantic import BaseModel, Field

# Analytics schemas
class DivisionStats(BaseModel):
    """Statistics for a legal division."""
    total_questions: int
    correct_answers: int
    accuracy: float


class TopicStats(BaseModel):
    """Statistics for a legal topic."""
    total_questions: int
    correct_answers: int
    accuracy: float


class OverallStats(BaseModel):
    """Overall user performance statistics."""
    total_questions_answered: int
    correct_answers: int
    accuracy: float


class UserStats(BaseModel):
    """Comprehensive user statistics."""
    overall: OverallStats
    by_division: Dict[str, DivisionStats]
    by_topic: Dict[str, TopicStats]
    weakest_divisions: List[str]
    weakest_topics: List[str]


class Suggestion(BaseModel):
    """A learning path suggestion."""
    type: str
    name: str
    reason: str


class LearningSummaryResponse(BaseModel):
    """Response schema for the user's learning summary."""
    stats: UserStats
    ai_feedback: str
    suggestions: List[Suggestion]


# Learning Goal schemas
class LearningGoal(BaseModel):
    """A learning goal option."""
    key: str
    description: str


class LearningGoalsResponse(BaseModel):
    """Response schema for available learning goals."""
    goals: List[LearningGoal]