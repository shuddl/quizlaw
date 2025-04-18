import enum
from typing import Optional, List

from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AnswerOption(str, enum.Enum):
    """Enum for MCQ answer options."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class MCQQuestion(BaseModel):
    """MCQ Question model.
    
    Represents a multiple-choice question generated from a legal section.
    """
    
    __tablename__ = "mcq_questions"
    
    legal_section_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("legal_sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(Enum(AnswerOption), nullable=False)
    explanation = Column(Text, nullable=True)
    generated_by_model = Column(String, nullable=False)
    is_validated = Column(Boolean, default=False, nullable=False)
    topic_tags = Column(JSONB, nullable=True)
    difficulty_rating = Column(Integer, nullable=True)
    
    # Relationship to LegalSection
    legal_section = relationship("LegalSection", back_populates="mcq_questions")
    
    # Relationship to UserResponse
    user_responses = relationship("UserResponse", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the MCQ question."""
        return f"<MCQQuestion(id={self.id}, legal_section_id={self.legal_section_id})>"


class UserResponse(BaseModel):
    """User Response model.
    
    Represents a user's response to an MCQ question.
    """
    
    __tablename__ = "user_responses"
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("mcq_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_answer = Column(Enum(AnswerOption), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    
    # Relationships
    user = relationship("User")
    question = relationship("MCQQuestion", back_populates="user_responses")
    
    # Create compound index for faster user history lookups
    __table_args__ = (
        Index("ix_user_responses_user_question", "user_id", "question_id"),
    )
    
    def __repr__(self) -> str:
        """String representation of the user response."""
        return f"<UserResponse(id={self.id}, user_id={self.user_id}, question_id={self.question_id})>"