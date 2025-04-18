from functools import wraps
from typing import Optional
import logging

from flask import request, jsonify, g
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import session_scope
from app.core.security import decode_access_token
from app.crud import user as user_crud
from app.models.user import User


# Set up logger
logger = logging.getLogger(__name__)


async def get_current_user() -> Optional[User]:
    """
    Get the current authenticated user from the Authorization header.
    
    Returns:
        User object if authenticated, None otherwise
    """
    # Check if we already have the user in the request context
    if hasattr(g, "current_user"):
        return g.current_user
    
    # Get the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    # Extract token
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # Decode token
    token_data = decode_access_token(token)
    if not token_data or not token_data.user_id:
        return None
    
    # Get user from database
    try:
        async with session_scope() as session:
            user = await user_crud.get_by_id(session, token_data.user_id)
            if not user or not user.is_active:
                return None
            
            # Store in request context for future use
            g.current_user = user
            return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None


def login_required(f):
    """
    Decorator to require login for a route.
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        user = await get_current_user()
        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401
        return await f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges for a route.
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        user = await get_current_user()
        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401
        if not user.is_superuser:
            return jsonify({
                "error": "Admin privileges required"
            }), 403
        return await f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """
    Decorator to require premium subscription for a route.
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        user = await get_current_user()
        if not user:
            return jsonify({
                "error": "Authentication required"
            }), 401
        if user.subscription_tier != "Premium":
            return jsonify({
                "error": "Premium subscription required"
            }), 403
        return await f(*args, **kwargs)
    return decorated_function