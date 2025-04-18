from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Text, Boolean, DateTime, Index, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class LegalSection(BaseModel):
    """Legal Section model.
    
    Represents a section of legal code that can be used to generate MCQs.
    """
    
    __tablename__ = "legal_sections"
    
    division = Column(String, nullable=False, index=True)
    part = Column(String, nullable=True)
    chapter = Column(String, nullable=True)
    section_number = Column(String, nullable=False, index=True)
    section_title = Column(String, nullable=False)
    section_text = Column(Text, nullable=False)
    source_url = Column(String, unique=True, nullable=False)
    is_bar_relevant = Column(Boolean, default=False, index=True)
    last_mcq_generated_at = Column(DateTime(timezone=True), nullable=True)
    topics = Column(JSONB, nullable=True)
    difficulty_score = Column(Float, nullable=True)
    
    # Relationship to MCQQuestion
    mcq_questions = relationship("MCQQuestion", back_populates="legal_section", cascade="all, delete-orphan")
    
    # Create compound indices for common query patterns
    __table_args__ = (
        Index("ix_legal_sections_division_section", "division", "section_number"),
        Index("ix_legal_sections_bar_relevant", "is_bar_relevant", "division"),
    )
    
    def __repr__(self) -> str:
        """String representation of the legal section."""
        return f"<LegalSection(id={self.id}, division={self.division}, section_number={self.section_number})>"