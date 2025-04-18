from typing import Optional
import uuid

from pydantic import BaseModel, UUID4


class Token(BaseModel):
    """Schema for JWT access token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for data stored in JWT token."""
    user_id: Optional[UUID4] = None