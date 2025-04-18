import logging
from typing import Dict, List, Any, Optional, Tuple
import uuid
from collections import defaultdict

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.user import User
from app.models.mcq_question import UserResponse, MCQQuestion
from app.models.legal_section import LegalSection
from app.services.openai_service import OpenAIService
from app.services.learning_path_service import suggest_next_steps

# Set up logger
logger = logging.getLogger(__name__)


async def calculate_user_stats(session: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
    """
    Calculate comprehensive user statistics based on their quiz responses.
    
    Args:
        session: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary containing user statistics
    """
    # Get user response data with questions and legal sections
    query = (
        select(UserResponse)
        .where(UserResponse.user_id == user_id)
        .options(
            joinedload(UserResponse.question)
            .joinedload(MCQQuestion.legal_section)
        )
    )
    
    result = await session.execute(query)
    responses = result.scalars().all()
    
    # Initialize stats
    stats = {
        "overall": {
            "total_questions_answered": 0,
            "correct_answers": 0,
            "accuracy": 0.0,
        },
        "by_division": {},
        "by_topic": {},
        "weakest_divisions": [],
        "weakest_topics": [],
    }
    
    # Setup counters
    division_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    topic_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    
    # Process responses
    for response in responses:
        stats["overall"]["total_questions_answered"] += 1
        
        if response.is_correct:
            stats["overall"]["correct_answers"] += 1
        
        # Process by division
        if response.question and response.question.legal_section:
            division = response.question.legal_section.division
            
            division_stats[division]["total"] += 1
            if response.is_correct:
                division_stats[division]["correct"] += 1
        
        # Process by topic
        if response.question and response.question.topic_tags:
            for topic in response.question.topic_tags:
                topic_stats[topic]["total"] += 1
                if response.is_correct:
                    topic_stats[topic]["correct"] += 1
    
    # Calculate overall accuracy
    if stats["overall"]["total_questions_answered"] > 0:
        stats["overall"]["accuracy"] = (
            stats["overall"]["correct_answers"] / stats["overall"]["total_questions_answered"]
        )
    
    # Calculate division accuracy
    for division, counts in division_stats.items():
        if counts["total"] > 0:
            accuracy = counts["correct"] / counts["total"]
            stats["by_division"][division] = {
                "total_questions": counts["total"],
                "correct_answers": counts["correct"],
                "accuracy": accuracy,
            }
    
    # Calculate topic accuracy
    for topic, counts in topic_stats.items():
        if counts["total"] > 0:
            accuracy = counts["correct"] / counts["total"]
            stats["by_topic"][topic] = {
                "total_questions": counts["total"],
                "correct_answers": counts["correct"],
                "accuracy": accuracy,
            }
    
    # Find weakest divisions (at least 3 questions answered)
    division_accuracies = [
        (div, data["accuracy"])
        for div, data in stats["by_division"].items()
        if data["total_questions"] >= 3
    ]
    division_accuracies.sort(key=lambda x: x[1])
    stats["weakest_divisions"] = [div for div, _ in division_accuracies[:3]]
    
    # Find weakest topics (at least 3 questions answered)
    topic_accuracies = [
        (topic, data["accuracy"])
        for topic, data in stats["by_topic"].items()
        if data["total_questions"] >= 3
    ]
    topic_accuracies.sort(key=lambda x: x[1])
    stats["weakest_topics"] = [topic for topic, _ in topic_accuracies[:3]]
    
    return stats


async def generate_ai_feedback(user_stats: Dict[str, Any]) -> str:
    """
    Generate AI feedback based on user statistics.
    
    Args:
        user_stats: Dictionary containing user statistics
        
    Returns:
        String containing AI-generated feedback
    """
    try:
        # Instantiate OpenAI service
        openai_service = OpenAIService()
        
        # Construct prompt for AI
        prompt = f"""As an expert legal tutor, provide personalized feedback based on these quiz statistics:

Overall Performance:
- Questions answered: {user_stats['overall']['total_questions_answered']}
- Correct answers: {user_stats['overall']['correct_answers']}
- Accuracy: {user_stats['overall']['accuracy'] * 100:.1f}%

"""
        
        # Add division information if available
        if user_stats["by_division"]:
            prompt += "Division Performance:\n"
            for division, data in user_stats["by_division"].items():
                prompt += f"- {division}: {data['accuracy'] * 100:.1f}% ({data['correct_answers']}/{data['total_questions']})\n"
        
        # Add topic information if available
        if user_stats["by_topic"]:
            prompt += "\nTopic Performance:\n"
            for topic, data in user_stats["by_topic"].items():
                prompt += f"- {topic}: {data['accuracy'] * 100:.1f}% ({data['correct_answers']}/{data['total_questions']})\n"
        
        # Add weakest areas
        if user_stats["weakest_divisions"]:
            prompt += "\nWeakest Divisions: " + ", ".join(user_stats["weakest_divisions"]) + "\n"
        
        if user_stats["weakest_topics"]:
            prompt += "\nWeakest Topics: " + ", ".join(user_stats["weakest_topics"]) + "\n"
        
        prompt += """\nProvide a concise, actionable 2-paragraph feedback that:
1. Highlights strengths and areas for improvement
2. Offers specific advice for improving knowledge in weak areas
3. Is encouraging and constructive

Keep the tone professional but supportive."""
        
        # Call OpenAI API
        response = await openai_service.generate_text(
            prompt, 
            model="gpt-4o-mini",
            max_tokens=300
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error generating AI feedback: {str(e)}")
        return "Unable to generate personalized feedback at this time. Keep practicing to improve your legal knowledge!"


async def get_analytics_and_feedback(session: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
    """
    Get analytics, AI-generated feedback, and learning path suggestions for a user.
    
    Args:
        session: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary containing statistics, feedback, and suggestions
    """
    # Get the user to access their learning goal
    user_query = select(User).where(User.id == user_id)
    user_result = await session.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    # Fetch user stats
    stats = await calculate_user_stats(session, user_id)
    
    # Generate AI feedback
    feedback = await generate_ai_feedback(stats)
    
    # Generate learning path suggestions
    suggestions = await suggest_next_steps(
        session,
        user_id,
        user.learning_goal,
        stats
    )
    
    # Combine and return
    return {
        "stats": stats,
        "ai_feedback": feedback,
        "suggestions": suggestions
    }