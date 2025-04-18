from typing import Optional
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, UUID4

from app.models.user import SubscriptionTier


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    subscription_tier: Optional[SubscriptionTier] = None
    stripe_customer_id: Optional[str] = None
    learning_goal: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user data."""
    id: UUID4
    is_active: bool
    is_superuser: bool
    subscription_tier: SubscriptionTier
    learning_goal: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserRead):
    """Schema for user data in database, including hashed_password."""
    hashed_password: str
    stripe_customer_id: Optional[str] = None