import logging
from typing import Dict, List, Any, Optional
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.mcq_question import MCQQuestion
from app.models.legal_section import LegalSection
from app.services.openai_service import OpenAIService

# Set up logger
logger = logging.getLogger(__name__)


# Predefined learning goals and their descriptions
LEARNING_GOALS = {
    "bar_exam": "Prepare for the bar examination",
    "practice_readiness": "Prepare for legal practice",
    "general_knowledge": "Improve general legal knowledge",
    "academic": "Academic research or teaching",
    "specific_practice_area": "Focus on a specific practice area",
}


async def suggest_next_steps(
    session: AsyncSession,
    user_id: uuid.UUID,
    user_goal: Optional[str],
    user_stats: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Generate personalized suggestions for next steps in the learning path.
    
    Args:
        session: Database session
        user_id: ID of the user
        user_goal: User's learning goal (if set)
        user_stats: Dictionary containing user statistics
        
    Returns:
        List of dictionaries with suggestions
    """
    suggestions = []
    
    try:
        # 1. Suggest based on weakest topics/divisions
        if user_stats["weakest_topics"]:
            for topic in user_stats["weakest_topics"][:2]:
                suggestions.append({
                    "type": "topic",
                    "name": topic,
                    "reason": f"You've had difficulty with questions related to '{topic}'. More practice here will strengthen your understanding."
                })
        
        if user_stats["weakest_divisions"] and len(suggestions) < 3:
            for division in user_stats["weakest_divisions"][:2]:
                if len(suggestions) < 3:
                    suggestions.append({
                        "type": "division",
                        "name": division,
                        "reason": f"Your accuracy in '{division}' is lower than other areas. Additional focus here will help improve your performance."
                    })
        
        # 2. Suggest based on user's learning goal
        if user_goal:
            if user_goal == "bar_exam" and len(suggestions) < 4:
                # Find bar-relevant sections user hasn't practiced much
                query = (
                    select(LegalSection)
                    .where(LegalSection.is_bar_relevant == True)
                    .order_by(func.random())
                    .limit(2)
                )
                result = await session.execute(query)
                bar_sections = result.scalars().all()
                
                for section in bar_sections:
                    if len(suggestions) < 5:
                        suggestions.append({
                            "type": "bar_section",
                            "name": f"{section.division} - {section.section_number}",
                            "reason": "This section is frequently tested on the bar exam and will strengthen your preparation."
                        })
            
            elif user_goal == "practice_readiness" and len(suggestions) < 4:
                # Suggest practice-oriented topics
                practice_topics = ["Legal Procedure", "Professional Responsibility", "Client Counseling"]
                
                for topic in practice_topics:
                    if topic not in [s["name"] for s in suggestions] and len(suggestions) < 5:
                        suggestions.append({
                            "type": "practice_topic",
                            "name": topic,
                            "reason": f"Mastering '{topic}' is essential for effective legal practice."
                        })
        
        # 3. Add general suggestions if needed to reach 3-5 total
        general_suggestions = [
            {
                "type": "strategy",
                "name": "Timed Practice",
                "reason": "Practice answering questions under time constraints to build exam readiness."
            },
            {
                "type": "strategy",
                "name": "Review Explanations",
                "reason": "Thoroughly review explanations for questions you answered incorrectly to reinforce learning."
            },
            {
                "type": "strategy",
                "name": "Mixed Division Quiz",
                "reason": "Take quizzes that mix multiple divisions to build connections between different areas of law."
            }
        ]
        
        for suggestion in general_suggestions:
            if len(suggestions) < 5:
                suggestions.append(suggestion)
            else:
                break
        
        # Ensure we have at least 3 suggestions
        if len(suggestions) < 3:
            # Use AI service to generate additional personalized suggestions
            openai_service = OpenAIService()
            stats_summary = f"Overall accuracy: {user_stats['overall']['accuracy'] * 100:.1f}%, "
            stats_summary += f"Weakest areas: {', '.join(user_stats['weakest_divisions'] + user_stats['weakest_topics'])}"
            
            prompt = f"""Given a user with learning goal: {user_goal or 'Not specified'} and stats: {stats_summary}, 
            suggest 2 more personalized learning steps. Return in JSON format with fields: type, name, reason."""
            
            try:
                ai_suggestions = await openai_service.generate_json(prompt, max_tokens=300)
                if "suggestions" in ai_suggestions and isinstance(ai_suggestions["suggestions"], list):
                    for suggestion in ai_suggestions["suggestions"]:
                        if (
                            isinstance(suggestion, dict) and
                            "type" in suggestion and
                            "name" in suggestion and
                            "reason" in suggestion and
                            len(suggestions) < 5
                        ):
                            suggestions.append(suggestion)
            except Exception as e:
                logger.error(f"Error generating AI suggestions: {str(e)}")
        
        # Limit to 5 suggestions
        return suggestions[:5]
    
    except Exception as e:
        logger.error(f"Error suggesting next steps: {str(e)}")
        # Return basic suggestions if an error occurs
        return [
            {
                "type": "general",
                "name": "Practice Regularly",
                "reason": "Regular practice across diverse legal topics builds comprehensive knowledge."
            },
            {
                "type": "general",
                "name": "Review Fundamentals",
                "reason": "Revisit foundational concepts in areas where you struggle."
            },
            {
                "type": "general",
                "name": "Take Mixed Topic Quizzes",
                "reason": "Mixed topic quizzes help identify knowledge gaps and strengthen connections between concepts."
            }
        ]


async def get_allowed_learning_goals() -> Dict[str, str]:
    """
    Get a dictionary of allowed learning goals with descriptions.
    
    Returns:
        Dictionary mapping goal keys to descriptions
    """
    return LEARNING_GOALS