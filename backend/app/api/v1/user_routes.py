from typing import List, Optional, Dict, Any
import uuid
import logging

from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.session import session_scope
from app.schemas.user import UserRead, UserUpdate
from app.schemas.analytics import LearningSummaryResponse, LearningGoalsResponse, LearningGoal
from app.crud import user as user_crud
from app.services.analytics_service import get_analytics_and_feedback
from app.services.learning_path_service import get_allowed_learning_goals
from app.api.dependencies import get_current_user, login_required


# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint("user", __name__, url_prefix="/api/v1/users")


@user_bp.route("/me", methods=["GET"])
@login_required
async def get_current_user_profile():
    """
    Get the current user's profile information.
    
    Returns:
        User profile data
    """
    try:
        user = await get_current_user()
        return jsonify(UserRead.model_validate(user))
    
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching user profile"
        }), 500


@user_bp.route("/me", methods=["PUT"])
@login_required
@validate()
async def update_current_user(body: UserUpdate):
    """
    Update the current user's profile.
    
    Args:
        body: User update data
        
    Returns:
        Updated user profile
    """
    try:
        user = await get_current_user()
        
        # Validate learning goal if provided
        if body.learning_goal is not None:
            allowed_goals = await get_allowed_learning_goals()
            if body.learning_goal and body.learning_goal not in allowed_goals:
                return jsonify({
                    "error": f"Invalid learning goal. Valid options are: {', '.join(allowed_goals.keys())}"
                }), 400
        
        async with session_scope() as session:
            # Handle password updates
            update_data = body.model_dump(exclude_unset=True)
            if "password" in update_data:
                from app.core.security import get_password_hash
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            # Update user
            updated_user = await user_crud.update_user(
                session, user.id, update_data
            )
            
            if not updated_user:
                return jsonify({
                    "error": "Failed to update user"
                }), 500
            
            return jsonify(UserRead.model_validate(updated_user))
    
    except IntegrityError:
        logger.error(f"IntegrityError updating user")
        return jsonify({
            "error": "Email already in use"
        }), 400
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({
            "error": "An error occurred while updating user"
        }), 500


@user_bp.route("/me/learning-summary", methods=["GET"])
@login_required
async def get_learning_summary():
    """
    Get the current user's learning summary including statistics, 
    feedback, and next step suggestions.
    
    Returns:
        Learning summary data
    """
    try:
        user = await get_current_user()
        
        async with session_scope() as session:
            # Get analytics, feedback, and suggestions
            summary = await get_analytics_and_feedback(session, user.id)
            
            return jsonify(LearningSummaryResponse(**summary))
    
    except Exception as e:
        logger.error(f"Error getting learning summary: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching learning summary"
        }), 500


@user_bp.route("/learning-goals", methods=["GET"])
async def get_learning_goals():
    """
    Get a list of available learning goals.
    
    Returns:
        List of learning goals with descriptions
    """
    try:
        allowed_goals = await get_allowed_learning_goals()
        
        goals = [
            LearningGoal(key=key, description=description)
            for key, description in allowed_goals.items()
        ]
        
        return jsonify(LearningGoalsResponse(goals=goals))
    
    except Exception as e:
        logger.error(f"Error getting learning goals: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching learning goals"
        }), 500