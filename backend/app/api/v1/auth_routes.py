from datetime import timedelta
import logging

from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from sqlalchemy.exc import IntegrityError

from app.db.session import session_scope
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.core.security import (
    verify_password, get_password_hash, create_access_token, decode_access_token
)
from app.core.config import settings
from app.crud import user as user_crud


# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/register", methods=["POST"])
@validate()
async def register_user(body: UserCreate):
    """
    Register a new user.
    
    Args:
        body: User registration data
        
    Returns:
        Created user data
    """
    try:
        async with session_scope() as session:
            # Check if user already exists
            existing_user = await user_crud.get_by_email(session, body.email)
            if existing_user:
                return jsonify({
                    "error": "Email already registered"
                }), 400
            
            # Create user
            hashed_password = get_password_hash(body.password)
            user_data = {
                "email": body.email,
                "hashed_password": hashed_password,
            }
            
            user = await user_crud.create_user(session, user_data)
            
            return jsonify(UserRead.model_validate(user))
    
    except IntegrityError:
        logger.error(f"IntegrityError registering user with email {body.email}")
        return jsonify({
            "error": "Email already registered"
        }), 400
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            "error": "An error occurred while registering user"
        }), 500


@auth_bp.route("/login", methods=["POST"])
async def login():
    """
    Log in a user.
    
    Form data:
        username: User's email
        password: User's password
        
    Returns:
        JWT access token
    """
    try:
        form_data = request.form
        
        if not form_data or not form_data.get("username") or not form_data.get("password"):
            return jsonify({
                "error": "Missing username or password"
            }), 400
        
        email = form_data.get("username")  # username is actually the email
        password = form_data.get("password")
        
        async with session_scope() as session:
            # Get the user
            user = await user_crud.get_by_email(session, email)
            
            if not user or not verify_password(password, user.hashed_password):
                return jsonify({
                    "error": "Incorrect email or password"
                }), 401
            
            if not user.is_active:
                return jsonify({
                    "error": "Inactive user"
                }), 403
            
            # Create access token
            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                subject=user.id, expires_delta=access_token_expires
            )
            
            return jsonify(Token(
                access_token=access_token,
                token_type="bearer"
            ))
    
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return jsonify({
            "error": "An error occurred while logging in"
        }), 500