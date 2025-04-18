from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.legal_section import LegalSection


async def create_legal_section(db: Session, section_data: Dict[str, Any]) -> LegalSection:
    """Create a new legal section."""
    legal_section = LegalSection(**section_data)
    db.add(legal_section)
    try:
        await db.commit()
        await db.refresh(legal_section)
        return legal_section
    except IntegrityError:
        await db.rollback()
        raise


async def get_by_source_url(db: Session, source_url: str) -> Optional[LegalSection]:
    """Get a legal section by its source URL."""
    query = select(LegalSection).where(LegalSection.source_url == source_url)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_id(db: Session, section_id: uuid.UUID) -> Optional[LegalSection]:
    """Get a legal section by its ID."""
    query = select(LegalSection).where(LegalSection.id == section_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_division_and_section(
    db: Session, division: str, section_number: str
) -> Optional[LegalSection]:
    """Get a legal section by its division and section number."""
    query = select(LegalSection).where(
        LegalSection.division == division,
        LegalSection.section_number == section_number
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_sections_by_division(db: Session, division: str) -> List[LegalSection]:
    """Get all legal sections for a division."""
    query = select(LegalSection).where(
        LegalSection.division == division
    ).order_by(LegalSection.section_number)
    result = await db.execute(query)
    return result.scalars().all()


async def get_bar_relevant_sections(db: Session, division: str) -> List[LegalSection]:
    """Get all bar-relevant legal sections for a division."""
    query = select(LegalSection).where(
        LegalSection.division == division,
        LegalSection.is_bar_relevant == True
    ).order_by(LegalSection.section_number)
    result = await db.execute(query)
    return result.scalars().all()


async def update_section(
    db: Session, section_id: uuid.UUID, update_data: Dict[str, Any]
) -> Optional[LegalSection]:
    """Update a legal section."""
    query = (
        update(LegalSection)
        .where(LegalSection.id == section_id)
        .values(**update_data)
        .returning(LegalSection)
    )
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def get_all_divisions(db: Session) -> List[str]:
    """Get a list of all distinct divisions."""
    query = select(LegalSection.division).distinct()
    result = await db.execute(query)
    return result.scalars().all()


async def update_bar_relevance(
    db: Session, division: str, relevant_section_numbers: List[str]
) -> Dict[str, int]:
    """Update the bar relevance flag for sections in a division."""
    # First mark all sections in the division as not bar relevant
    irrelevant_query = (
        update(LegalSection)
        .where(LegalSection.division == division)
        .values(is_bar_relevant=False)
    )
    await db.execute(irrelevant_query)
    
    # If there are no relevant sections, just return
    if not relevant_section_numbers:
        await db.commit()
        return {"marked_relevant": 0, "marked_irrelevant": 0}
    
    # Then mark the specified sections as bar relevant
    relevant_query = (
        update(LegalSection)
        .where(
            LegalSection.division == division,
            LegalSection.section_number.in_(relevant_section_numbers)
        )
        .values(is_bar_relevant=True)
    )
    result = await db.execute(relevant_query)
    await db.commit()
    
    # Get counts for status report
    relevant_count = result.rowcount
    total_query = select(func.count()).select_from(LegalSection).where(
        LegalSection.division == division
    )
    total_result = await db.execute(total_query)
    total_count = total_result.scalar_one()
    
    return {
        "marked_relevant": relevant_count,
        "marked_irrelevant": total_count - relevant_count
    }