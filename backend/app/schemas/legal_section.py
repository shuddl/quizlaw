from typing import Optional, List
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, UUID4


class LegalSectionBase(BaseModel):
    """Base schema for legal section data."""
    division: str
    part: Optional[str] = None
    chapter: Optional[str] = None
    section_number: str
    section_title: str
    section_text: str
    source_url: str
    is_bar_relevant: bool = False


class LegalSectionCreate(LegalSectionBase):
    """Schema for creating a new legal section."""
    pass


class LegalSectionUpdate(BaseModel):
    """Schema for updating a legal section."""
    division: Optional[str] = None
    part: Optional[str] = None
    chapter: Optional[str] = None
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    section_text: Optional[str] = None
    source_url: Optional[str] = None
    is_bar_relevant: Optional[bool] = None
    last_mcq_generated_at: Optional[datetime] = None


class LegalSectionRead(LegalSectionBase):
    """Schema for reading legal section data."""
    id: UUID4
    created_at: datetime
    last_mcq_generated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DivisionResponse(BaseModel):
    """Schema for response with list of divisions."""
    divisions: List[str]