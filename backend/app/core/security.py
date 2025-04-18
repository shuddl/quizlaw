from datetime import datetime, timedelta
from typing import Any, Optional, Union
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.token import TokenData


# Configure the password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, uuid.UUID], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Convert UUID to string if necessary
    if isinstance(subject, uuid.UUID):
        subject = str(subject)
    
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(
        to_encode, settings.FLASK_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.FLASK_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        
        # Convert user_id back to UUID
        user_id = uuid.UUID(user_id_str)
        token_data = TokenData(user_id=user_id)
        return token_data
    except (JWTError, ValidationError, ValueError):
        return None