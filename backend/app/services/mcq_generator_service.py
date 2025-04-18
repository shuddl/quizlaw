import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from pydantic import ValidationError

from app.core.config import settings
from app.models.legal_section import LegalSection
from app.models.mcq_question import AnswerOption
from app.schemas.mcq import MCQFromOpenAI, MCQCreate
from app.crud import legal_section as legal_section_crud
from app.crud import mcq_question as mcq_question_crud


# Set up logger
logger = logging.getLogger(__name__)


class MCQGenerationError(Exception):
    """Base exception for MCQ generation errors."""
    pass


class OpenAIError(MCQGenerationError):
    """Exception for OpenAI API errors."""
    pass


class ValidationFailedError(MCQGenerationError):
    """Exception for validation failures of generated MCQs."""
    pass


def construct_mcq_prompt(section: LegalSection, num_questions: int) -> str:
    """
    Construct a prompt for the OpenAI API to generate MCQs.
    
    Args:
        section: Legal section to generate MCQs for
        num_questions: Number of MCQs to generate
        
    Returns:
        String prompt for OpenAI API
    """
    return f"""You are an expert legal exam writer specializing in creating high-quality multiple-choice questions for bar exam preparation.

I need you to create {num_questions} challenging but fair multiple-choice questions testing knowledge and application of the following legal section:

SECTION NUMBER: {section.section_number}
SECTION TITLE: {section.section_title}

SECTION TEXT:
{section.section_text}

For each question:
1. Test understanding of key legal concepts, definitions, or applications from this specific section
2. Create 4 plausible answer options labeled A, B, C, and D
3. Ensure only ONE option is clearly correct
4. Make incorrect options (distractors) plausible but clearly wrong upon careful reading of the section
5. Provide a clear explanation that specifically cites relevant text from the section

FORMAT YOUR RESPONSE AS A JSON ARRAY OF OBJECTS with this exact structure:
[
  {{
    "question_text": "The complete question text goes here?",
    "options": {{
      "A": "First option text",
      "B": "Second option text",
      "C": "Third option text",
      "D": "Fourth option text"
    }},
    "correct_answer": "B",
    "explanation": "Explanation why B is correct and others are wrong, citing specific language from the section text: '[exact quote from section]'."
  }},
  ... additional questions ...
]

IMPORTANT GUIDELINES:
- Ensure each question is self-contained and doesn't require additional context
- Make questions challenging but fair
- Distractors should seem plausible but be clearly incorrect based on the section text
- Don't include anything outside this JSON format in your response
- Provide well-reasoned explanations citing specific language from the section text"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(OpenAIError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def generate_mcqs_with_openai(
    client: AsyncOpenAI, section: LegalSection, num_questions: int
) -> List[Dict[str, Any]]:
    """
    Generate MCQs using OpenAI API with retry logic.
    
    Args:
        client: OpenAI API client
        section: Legal section to generate MCQs for
        num_questions: Number of MCQs to generate
        
    Returns:
        List of generated MCQs
    """
    try:
        prompt = construct_mcq_prompt(section, num_questions)
        
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Use the latest available model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
            seed=42,  # For consistency
        )
        
        # Parse the response
        content = response.choices[0].message.content
        if not content:
            raise OpenAIError("Empty response from OpenAI API")
        
        try:
            # Need to extract the JSON array from the response
            data = json.loads(content)
            
            # Check if the response contains the expected key for the MCQ array
            if isinstance(data, dict) and any(k in data for k in ["mcqs", "questions", "results"]):
                for key in ["mcqs", "questions", "results"]:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                        
            # If data is already a list, return it
            if isinstance(data, list):
                return data
                
            # If we got a dict but not the expected structure, try to find any list
            for value in data.values():
                if isinstance(value, list):
                    return value
            
            raise ValidationFailedError(f"Could not find MCQ list in response: {content}")
            
        except json.JSONDecodeError:
            raise ValidationFailedError(f"Invalid JSON response: {content}")
        
    except Exception as e:
        if "openai" in str(type(e)).lower():
            logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIError(f"OpenAI API error: {str(e)}") from e
        else:
            logger.error(f"Error generating MCQs: {str(e)}")
            raise MCQGenerationError(f"Error generating MCQs: {str(e)}") from e


async def validate_mcq(mcq_data: Dict[str, Any]) -> Tuple[bool, Optional[MCQFromOpenAI]]:
    """
    Validate an MCQ from OpenAI API.
    
    Args:
        mcq_data: MCQ data to validate
        
    Returns:
        Tuple of (is_valid, validated_mcq)
    """
    try:
        # Normalize options if needed
        if "options" not in mcq_data and all(key in mcq_data for key in ["option_a", "option_b", "option_c", "option_d"]):
            mcq_data["options"] = {
                "A": mcq_data.pop("option_a", ""),
                "B": mcq_data.pop("option_b", ""),
                "C": mcq_data.pop("option_c", ""),
                "D": mcq_data.pop("option_d", ""),
            }
        
        # Validate with Pydantic
        validated_mcq = MCQFromOpenAI(**mcq_data)
        
        # Additional validation
        option_keys = set(validated_mcq.options.keys())
        if not option_keys == {"A", "B", "C", "D"}:
            logger.warning(f"MCQ has invalid option keys: {option_keys}")
            return False, None
        
        if validated_mcq.correct_answer not in validated_mcq.options:
            logger.warning(f"MCQ correct_answer '{validated_mcq.correct_answer}' not in options")
            return False, None
        
        return True, validated_mcq
    
    except ValidationError as e:
        logger.warning(f"MCQ validation failed: {str(e)}")
        return False, None
    except Exception as e:
        logger.error(f"Unexpected error during MCQ validation: {str(e)}")
        return False, None


async def format_mcq_for_storage(
    validated_mcq: MCQFromOpenAI, section_id: str
) -> MCQCreate:
    """
    Format a validated MCQ for storage in the database.
    
    Args:
        validated_mcq: Validated MCQ
        section_id: ID of the legal section
        
    Returns:
        MCQCreate object for storage
    """
    return MCQCreate(
        legal_section_id=section_id,
        question_text=validated_mcq.question_text,
        option_a=validated_mcq.options["A"],
        option_b=validated_mcq.options["B"],
        option_c=validated_mcq.options["C"],
        option_d=validated_mcq.options["D"],
        correct_answer=validated_mcq.correct_answer,
        explanation=validated_mcq.explanation,
        generated_by_model="gpt-4-turbo-preview",
        is_validated=True,
    )


async def store_mcq(
    session: AsyncSession, mcq_create: MCQCreate
) -> bool:
    """
    Store an MCQ in the database.
    
    Args:
        session: Database session
        mcq_create: MCQ data to store
        
    Returns:
        True if storing succeeded, False otherwise
    """
    try:
        await mcq_question_crud.create_mcq_question(
            session, mcq_create.model_dump()
        )
        return True
    except Exception as e:
        logger.error(f"Error storing MCQ: {str(e)}")
        return False


async def generate_mcqs_for_section(
    session: AsyncSession, section: LegalSection, num_questions: int = 2
) -> Dict[str, Any]:
    """
    Generate MCQs for a legal section.
    
    Args:
        session: Database session
        section: Legal section to generate MCQs for
        num_questions: Number of MCQs to generate
        
    Returns:
        Dictionary with generation statistics
    """
    stats = {
        "mcqs_requested": num_questions,
        "mcqs_generated": 0,
        "mcqs_validated": 0,
        "mcqs_stored": 0,
        "errors": 0,
    }
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        # Generate MCQs
        mcqs = await generate_mcqs_with_openai(client, section, num_questions)
        stats["mcqs_generated"] = len(mcqs)
        
        # Validate and store MCQs
        for mcq_data in mcqs:
            is_valid, validated_mcq = await validate_mcq(mcq_data)
            
            if is_valid and validated_mcq:
                stats["mcqs_validated"] += 1
                
                # Format and store MCQ
                mcq_create = await format_mcq_for_storage(validated_mcq, section.id)
                if await store_mcq(session, mcq_create):
                    stats["mcqs_stored"] += 1
                else:
                    stats["errors"] += 1
            else:
                stats["errors"] += 1
        
        # Update section's last_mcq_generated_at timestamp
        if stats["mcqs_stored"] > 0:
            await legal_section_crud.update_section(
                session, 
                section.id, 
                {"last_mcq_generated_at": datetime.now()}
            )
        
    except (MCQGenerationError, Exception) as e:
        logger.error(f"Error in generate_mcqs_for_section for section {section.id}: {str(e)}")
        stats["errors"] += 1
    
    return stats


async def generate_mcqs_for_division(
    session: AsyncSession, division_name: str, num_per_section: int = 2
) -> Dict[str, Any]:
    """
    Generate MCQs for all sections in a division.
    
    Args:
        session: Database session
        division_name: Name of the division
        num_per_section: Number of MCQs to generate per section
        
    Returns:
        Dictionary with generation statistics
    """
    overall_stats = {
        "total_sections": 0,
        "sections_processed": 0,
        "total_mcqs_requested": 0,
        "total_mcqs_stored": 0,
        "total_errors": 0,
    }
    
    # Get all sections for the division
    sections = await legal_section_crud.get_sections_by_division(session, division_name)
    overall_stats["total_sections"] = len(sections)
    overall_stats["total_mcqs_requested"] = len(sections) * num_per_section
    
    # Process each section
    for section in sections:
        try:
            section_stats = await generate_mcqs_for_section(
                session, section, num_per_section
            )
            
            overall_stats["sections_processed"] += 1
            overall_stats["total_mcqs_stored"] += section_stats["mcqs_stored"]
            overall_stats["total_errors"] += section_stats["errors"]
            
            logger.info(
                f"Generated {section_stats['mcqs_stored']} MCQs for section {section.section_number}"
            )
            
        except Exception as e:
            logger.error(f"Error processing section {section.id}: {str(e)}")
            overall_stats["total_errors"] += 1
    
    return overall_stats