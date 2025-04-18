from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User, SubscriptionTier


async def create_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create a new user."""
    user = User(**user_data)
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise


async def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get a user by ID."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email (case insensitive)."""
    # Use the functional lower() for case-insensitive comparison
    query = select(User).where(User.email.ilike(email))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate(db: Session, email: str, password_check_func) -> Optional[User]:
    """Authenticate a user with email and password verification function."""
    user = await get_by_email(db, email)
    if not user:
        return None
    if not password_check_func(user.hashed_password):
        return None
    return user


async def update_user(
    db: Session, user_id: uuid.UUID, update_data: Dict[str, Any]
) -> Optional[User]:
    """Update a user's information."""
    query = (
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
        .returning(User)
    )
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def update_subscription_tier(
    db: Session, user_id: uuid.UUID, tier: SubscriptionTier, stripe_customer_id: Optional[str] = None
) -> Optional[User]:
    """Update a user's subscription tier and optionally Stripe customer ID."""
    update_data = {"subscription_tier": tier}
    if stripe_customer_id:
        update_data["stripe_customer_id"] = stripe_customer_id
        
    return await update_user(db, user_id, update_data)


async def deactivate_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Deactivate a user (soft delete)."""
    return await update_user(db, user_id, {"is_active": False})


async def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    """Hard delete a user from the database."""
    query = delete(User).where(User.id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


async def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users with pagination."""
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()