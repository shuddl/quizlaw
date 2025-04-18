from typing import Dict, Optional, List
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4

from app.models.mcq_question import AnswerOption


class MCQBase(BaseModel):
    """Base schema for MCQ questions."""
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class MCQCreate(MCQBase):
    """Schema for creating an MCQ question."""
    legal_section_id: UUID4
    correct_answer: AnswerOption
    explanation: Optional[str] = None
    generated_by_model: str
    is_validated: bool = False


class MCQUpdate(BaseModel):
    """Schema for updating an MCQ question."""
    question_text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[AnswerOption] = None
    explanation: Optional[str] = None
    is_validated: Optional[bool] = None


class MCQRead(MCQBase):
    """Schema for reading an MCQ question."""
    id: UUID4
    legal_section_id: UUID4
    correct_answer: AnswerOption
    explanation: Optional[str] = None
    generated_by_model: str
    is_validated: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizQuestionResponse(BaseModel):
    """Schema for returning a quiz question to the frontend.
    
    Note: This deliberately excludes the correct answer and explanation.
    """
    id: UUID4
    question_text: str
    options: Dict[str, str]
    source_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class CheckAnswerRequest(BaseModel):
    """Schema for checking an answer to a quiz question."""
    question_id: UUID4
    selected_answer: AnswerOption


class CheckAnswerResponse(BaseModel):
    """Schema for the response to a check answer request."""
    is_correct: bool
    correct_answer: AnswerOption
    explanation: Optional[str] = None


class QuizRequest(BaseModel):
    """Schema for requesting a quiz."""
    mode: str = Field(..., description="Quiz mode: 'random', 'sequential', or 'law_student'")
    division: str = Field(..., description="Legal division to use for the quiz")
    num_questions: int = Field(10, ge=5, le=100, description="Number of questions to include")


class MCQGenerationRequest(BaseModel):
    """Schema for requesting MCQ generation for sections."""
    division: str
    num_per_section: int = Field(2, ge=1, le=5)


class MCQGenerationResponse(BaseModel):
    """Schema for the response to an MCQ generation request."""
    total_sections: int
    total_generated: int
    errors: int


# Schema for the expected format from OpenAI API
class MCQFromOpenAI(BaseModel):
    """Schema for validating MCQs from OpenAI API."""
    question_text: str
    options: Dict[str, str]
    correct_answer: AnswerOption
    explanation: str