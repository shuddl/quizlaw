from typing import List, Optional, Dict, Any, Tuple
import uuid
import random

from sqlalchemy import select, update, func, desc, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import text

from app.models.mcq_question import MCQQuestion, AnswerOption
from app.models.legal_section import LegalSection


async def create_mcq_question(db: Session, question_data: Dict[str, Any]) -> MCQQuestion:
    """Create a new MCQ question."""
    mcq_question = MCQQuestion(**question_data)
    db.add(mcq_question)
    await db.commit()
    await db.refresh(mcq_question)
    return mcq_question


async def get_by_id(db: Session, question_id: uuid.UUID) -> Optional[MCQQuestion]:
    """Get an MCQ question by its ID with legal section relationship loaded."""
    query = select(MCQQuestion).where(
        MCQQuestion.id == question_id
    ).options(joinedload(MCQQuestion.legal_section))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_questions_for_section(
    db: Session, section_id: uuid.UUID
) -> List[MCQQuestion]:
    """Get all MCQ questions for a legal section."""
    query = select(MCQQuestion).where(
        MCQQuestion.legal_section_id == section_id
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_questions_by_division(
    db: Session, division: str, mode: str, limit: int
) -> List[MCQQuestion]:
    """
    Get MCQ questions based on the specified division and mode.
    
    Args:
        db: Database session
        division: Legal division to filter by
        mode: "random", "sequential", or "law_student"
        limit: Maximum number of questions to return
        
    Returns:
        List of MCQQuestion objects matching the criteria
    """
    # Base query joining MCQQuestion with LegalSection
    query = select(MCQQuestion).join(
        LegalSection, MCQQuestion.legal_section_id == LegalSection.id
    ).where(
        LegalSection.division == division
    )
    
    # Add mode-specific filters and ordering
    if mode == "law_student":
        query = query.where(LegalSection.is_bar_relevant == True)
    
    if mode == "random":
        # Use database-specific random function
        query = query.order_by(text("RANDOM()"))
    elif mode == "sequential":
        # Order by section number and then by question ID
        query = query.order_by(
            LegalSection.section_number, 
            MCQQuestion.id
        )
    else:  # law_student mode defaults to sequential ordering
        query = query.order_by(
            LegalSection.section_number, 
            MCQQuestion.id
        )
    
    # Add limit
    query = query.limit(limit)
    
    # Execute query
    result = await db.execute(query)
    return result.scalars().unique().all()


async def mark_as_validated(db: Session, question_id: uuid.UUID) -> Optional[MCQQuestion]:
    """Mark an MCQ question as validated."""
    query = (
        update(MCQQuestion)
        .where(MCQQuestion.id == question_id)
        .values(is_validated=True)
        .returning(MCQQuestion)
    )
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def get_question_count_by_division(db: Session, division: str) -> int:
    """Get the count of MCQ questions for a division."""
    query = select(func.count(MCQQuestion.id)).join(
        LegalSection, MCQQuestion.legal_section_id == LegalSection.id
    ).where(
        LegalSection.division == division
    )
    result = await db.execute(query)
    return result.scalar_one()