import enum
from typing import Optional

from sqlalchemy import Column, String, Boolean, Enum, Index
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class SubscriptionTier(str, enum.Enum):
    """Enum for user subscription tiers."""
    FREE = "Free"
    PREMIUM = "Premium"


class User(BaseModel):
    """User model.
    
    Represents a user of the application with authentication and subscription information.
    """
    
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    subscription_tier = Column(
        Enum(SubscriptionTier), 
        default=SubscriptionTier.FREE,
        index=True,
        nullable=False,
    )
    stripe_customer_id = Column(String, nullable=True)
    learning_goal = Column(String, nullable=True)
    
    # Create an index on email for faster lookups
    __table_args__ = (
        Index("ix_users_email_lower", "lower(email)"),
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"