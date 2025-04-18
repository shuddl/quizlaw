from typing import List, Optional, Dict, Any
import uuid
import logging

from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import session_scope
from app.schemas.mcq import (
    QuizRequest, QuizQuestionResponse, CheckAnswerRequest, CheckAnswerResponse
)
from app.crud import mcq_question as mcq_question_crud
from app.crud import user as user_crud
from app.models.user import SubscriptionTier
from app.models.mcq_question import AnswerOption
from app.api.dependencies import get_current_user


# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/v1/quiz")


@quiz_bp.route("", methods=["POST"])
@validate()
async def get_quiz_questions(body: QuizRequest):
    """
    Get quiz questions based on mode, division, and count.
    
    Args:
        body: Quiz request parameters
        
    Returns:
        List of quiz questions
    """
    try:
        # Validate and normalize mode
        mode = body.mode.lower()
        if mode not in ["random", "sequential", "law_student"]:
            return jsonify({
                "error": "Invalid mode. Must be 'random', 'sequential', or 'law_student'."
            }), 400
        
        async with session_scope() as session:
            # Get questions based on mode and division
            questions = await mcq_question_crud.get_questions_by_division(
                session, body.division, mode, body.num_questions
            )
            
            # Format questions for response (excluding correct answer and explanation)
            response_data = []
            for question in questions:
                # Get the source URL from the related legal section
                source_url = None
                if question.legal_section:
                    source_url = question.legal_section.source_url
                
                # Create response object
                response_data.append(
                    QuizQuestionResponse(
                        id=question.id,
                        question_text=question.question_text,
                        options={
                            "A": question.option_a,
                            "B": question.option_b,
                            "C": question.option_c,
                            "D": question.option_d,
                        },
                        source_url=source_url,
                    )
                )
            
            return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in get_quiz_questions: {str(e)}")
        return jsonify({"error": "An error occurred while fetching quiz questions"}), 500


@quiz_bp.route("/check_answer", methods=["POST"])
@validate()
async def check_answer(body: CheckAnswerRequest):
    """
    Check if an answer to a quiz question is correct.
    
    Args:
        body: Answer check request
        
    Returns:
        Result with correct answer and explanation (if premium)
    """
    try:
        # Convert question_id to UUID
        try:
            question_id = uuid.UUID(str(body.question_id))
        except ValueError:
            return jsonify({"error": "Invalid question ID format"}), 400
        
        async with session_scope() as session:
            # Get the question
            question = await mcq_question_crud.get_by_id(session, question_id)
            if not question:
                return jsonify({"error": "Question not found"}), 404
            
            # Check if the answer is correct
            is_correct = body.selected_answer == question.correct_answer
            
            # Prepare response
            response = {
                "is_correct": is_correct,
                "correct_answer": question.correct_answer,
            }
            
            # Include explanation for premium users
            try:
                current_user = await get_current_user()
                if current_user and current_user.subscription_tier == SubscriptionTier.PREMIUM:
                    response["explanation"] = question.explanation
            except Exception:
                # If there's an error or no user is authenticated, don't include explanation
                pass
            
            return jsonify(CheckAnswerResponse(**response))
    
    except Exception as e:
        logger.error(f"Error in check_answer: {str(e)}")
        return jsonify({"error": "An error occurred while checking the answer"}), 500


@quiz_bp.route("/divisions", methods=["GET"])
async def get_divisions():
    """
    Get a list of all distinct divisions.
    
    Returns:
        List of division names
    """
    try:
        async with session_scope() as session:
            divisions = await mcq_question_crud.get_all_divisions(session)
            return jsonify({"divisions": divisions})
    
    except Exception as e:
        logger.error(f"Error in get_divisions: {str(e)}")
        return jsonify({"error": "An error occurred while fetching divisions"}), 500